"""
Glue Python Shell job: dea-batch-scd2-mysql-data-extract-glue-job

Incrementally extracts rows from MySQL (RDS) using an updated_at watermark,
runs data-quality checks, and writes:
  - good rows  -> s3://<data bucket>/data/<table>/<table>_<ts>.parquet
  - bad rows   -> s3://<error bucket>/dq_errors/<table>/<table>_errors_<ts>.parquet
The watermark is stored in s3://<data bucket>/checkpoint/<table>_checkpoint.json

Job settings:
  - Type: Python Shell (Python 3.9), Load common analytics libraries = Yes
  - IAM role: dea-batch-scd2-aws-role
  - Connections: dea-batch-scd2-rds-connection
  - Job parameter: --additional-python-modules = pymysql
Scheduled by workflow: dea-batch-scd2-mysql-data-extract-glue-workflow
"""

import boto3
import pymysql
import io
import json
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# ── Config ────────────────────────────────────────────────────────────────────
GLUE_CONNECTION_NAME = "<Your_AWS_Glue_Connection_Name>"
AWS_REGION           = "<Your_AWS_Region>"
TABLE_NAME           = "product"

# S3 – main output bucket
S3_DATA_BUCKET       = "<Your_S3_Data_Bucket_Name>"
S3_OUTPUT_PREFIX     = f"data/{TABLE_NAME}/"          # parquet files land here
CHECKPOINT_KEY       = f"checkpoint/{TABLE_NAME}_checkpoint.json"

# S3 – error / DQ-failure bucket
S3_ERROR_BUCKET      = "<Your_S3_Error_Bucket_Name>"
S3_ERROR_PREFIX      = f"dq_errors/{TABLE_NAME}/"

# Column expected in the source table that drives incremental loads
INCREMENTAL_COL      = "updated_at"


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_s3_client():
    return boto3.client("s3", region_name=AWS_REGION)


# ── Checkpoint helpers ────────────────────────────────────────────────────────
def load_checkpoint(s3, bucket: str, key: str) -> dict:
    """
    Returns a dict with at least:
        last_run_time  – string (UTC) of the previous successful run,
                         or None if this is the first run.
    """
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        checkpoint = json.loads(obj["Body"].read().decode("utf-8"))
        print(f"Checkpoint loaded: {checkpoint}")
        return checkpoint
    except s3.exceptions.NoSuchKey:
        print("No checkpoint found – will perform a full load.")
        return {"last_run_time": None}
    except Exception as exc:
        print(f"Could not read checkpoint ({exc}) – defaulting to full load.")
        return {"last_run_time": None}


def save_checkpoint(s3, bucket: str, key: str, run_time: datetime) -> None:
    payload = {
        "last_run_time": run_time.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at":    datetime.now(timezone.utc).isoformat(),
    }
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(payload).encode("utf-8"),
        ContentType="application/json",
    )
    print(f"Checkpoint saved: {payload}")


# ── MySQL helpers ─────────────────────────────────────────────────────────────
def get_mysql_connection():
    props = boto3.client("glue", region_name=AWS_REGION).get_connection(
        Name=GLUE_CONNECTION_NAME, HidePassword=False
    )["Connection"]["ConnectionProperties"]

    parsed = urlparse(props["JDBC_CONNECTION_URL"][len("jdbc:"):])
    return pymysql.connect(
        host=parsed.hostname,
        port=parsed.port or 3306,
        user=props["USERNAME"],
        password=props["PASSWORD"],
        database=parsed.path.strip("/"),
        connect_timeout=30,
        cursorclass=pymysql.cursors.DictCursor,   # return rows as dicts
    )


def fetch_incremental_data(conn, table: str, incremental_col: str,
                           last_run_time: Optional[str]) -> pd.DataFrame:
    """
    Pull rows whose `incremental_col` is strictly greater than `last_run_time`.
    Falls back to a full load when last_run_time is None.
    """
    if last_run_time:
        sql = (
            f"SELECT * FROM {table} "
            f"WHERE {incremental_col} > %(last_run)s "
            f"ORDER BY {incremental_col}"
        )
        params = {"last_run": last_run_time}
        print(f"Incremental query: {sql} | params: {params}")
    else:
        sql = f"SELECT * FROM {table} ORDER BY {incremental_col}"
        params = {}
        print(f"Full-load query: {sql}")

    with conn.cursor() as cursor:
        cursor.execute(sql, params)
        rows = cursor.fetchall()

    df = pd.DataFrame(rows)
    print(f"Fetched {len(df)} row(s) from '{table}'.")
    return df


# ── Data-quality checks ───────────────────────────────────────────────────────
def run_dq_checks(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns (good_df, bad_df).

    Rules
    -----
    1. unit_price       must not be negative
    2. quantity         must not be negative
    3. supplier_name    must not be NULL / empty
    """
    if df.empty:
        return df.copy(), pd.DataFrame(columns=list(df.columns) + ["dq_failure_reasons"])

    reasons = pd.Series([""] * len(df), index=df.index)

    # Rule 1 – unit_price
    if "unit_price" in df.columns:
        mask = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0) < 0
        reasons[mask] += "NEGATIVE_PRICE; "

    # Rule 2 – quantity
    if "quantity" in df.columns:
        mask = pd.to_numeric(df["quantity"], errors="coerce").fillna(0) < 0
        reasons[mask] += "NEGATIVE_QUANTITY; "

    # Rule 3 – supplier_name
    if "supplier_name" in df.columns:
        mask = df["supplier_name"].isna() | (df["supplier_name"].astype(str).str.strip() == "")
        reasons[mask] += "NULL_SUPPLIER_NAME; "

    bad_mask = reasons.str.strip() != ""
    good_df  = df[~bad_mask].copy()
    bad_df   = df[bad_mask].copy()
    bad_df["dq_failure_reasons"] = reasons[bad_mask].str.strip()

    print(f"DQ check complete – {len(good_df)} good / {len(bad_df)} bad row(s).")
    return good_df, bad_df


# ── S3 write helpers ──────────────────────────────────────────────────────────
def df_to_parquet_bytes(df: pd.DataFrame) -> bytes:
    table  = pa.Table.from_pandas(df, preserve_index=False)
    buffer = io.BytesIO()
    # Microsecond timestamps so Snowflake reads them correctly
    pq.write_table(table, buffer, compression="snappy",
                   coerce_timestamps="us", allow_truncated_timestamps=True)
    return buffer.getvalue()


def write_parquet_to_s3(s3, df: pd.DataFrame, bucket: str,
                        prefix: str, run_time: datetime) -> None:
    if df.empty:
        print("No good records to write.")
        return

    timestamp = run_time.strftime("%Y%m%d_%H%M%S")
    key       = f"{prefix}{TABLE_NAME}_{timestamp}.parquet"

    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=df_to_parquet_bytes(df),
        ContentType="application/octet-stream",
    )
    print(f"✅ Good records written → s3://{bucket}/{key}  ({len(df)} rows)")


def write_error_parquet_to_s3(s3, df: pd.DataFrame, bucket: str,
                              prefix: str, run_time: datetime) -> None:
    if df.empty:
        print("No DQ-failure records to write.")
        return

    timestamp = run_time.strftime("%Y%m%d_%H%M%S")
    key       = f"{prefix}{TABLE_NAME}_errors_{timestamp}.parquet"

    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=df_to_parquet_bytes(df),
        ContentType="application/octet-stream",
    )
    print(f"⚠️  DQ failures written → s3://{bucket}/{key}  ({len(df)} rows)")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    run_time = datetime.now(timezone.utc)   # capture job start time
    s3       = get_s3_client()

    # 1. Load checkpoint (last successful run time)
    checkpoint    = load_checkpoint(s3, S3_DATA_BUCKET, CHECKPOINT_KEY)
    last_run_time = checkpoint.get("last_run_time")  # None → full load

    # 2. Fetch incremental (or full) data from MySQL
    conn = get_mysql_connection()
    try:
        raw_df = fetch_incremental_data(conn, TABLE_NAME, INCREMENTAL_COL, last_run_time)
    finally:
        conn.close()

    if raw_df.empty:
        print(f"No new / updated rows since {last_run_time} – nothing to write.")
        # Still update the checkpoint so the next run window advances
        save_checkpoint(s3, S3_DATA_BUCKET, CHECKPOINT_KEY, run_time)
        return

    # 3. Data-quality checks
    good_df, bad_df = run_dq_checks(raw_df)

    # 4. Write good records → main S3 bucket (Parquet / Snappy)
    write_parquet_to_s3(s3, good_df, S3_DATA_BUCKET, S3_OUTPUT_PREFIX, run_time)

    # 5. Write DQ failures → error S3 bucket (Parquet / Snappy)
    write_error_parquet_to_s3(s3, bad_df, S3_ERROR_BUCKET, S3_ERROR_PREFIX, run_time)

    # 6. Save checkpoint with this run's start time
    #    (using run_time ensures we don't miss rows updated during the job)
    save_checkpoint(s3, S3_DATA_BUCKET, CHECKPOINT_KEY, run_time)

    print(
        f"Job finished. Good: {len(good_df)} | DQ failures: {len(bad_df)} | "
        f"Run time (UTC): {run_time.isoformat()}"
    )


if __name__ == "__main__":
    main()
