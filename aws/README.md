# AWS resources

| Resource | Name |
|---|---|
| S3 data bucket | `<YOUR_S3_DATA_BUCKET>` |
| S3 error bucket | `<YOUR_S3_ERROR_BUCKET>` |
| IAM role (Glue) | `dea-batch-scd2-aws-role` — trust: `iam/glue_role_trust_policy.json`; policies: `AWSGlueServiceRole`, `AmazonS3FullAccess`, `CloudWatchFullAccess` |
| IAM role (Snowflake) | `dea-batch-scd2-snowflake-role` — trust: `iam/snowflake_role_trust_policy.json`; policy: `iam/snowflake_role_s3_policy.json` |
| VPC | `dea-batch-scd2-vpc` (10.0.0.0/16), DNS hostnames + resolution enabled |
| Subnets | `dea-batch-scd2-subnet-01` (10.0.1.0/24), `dea-batch-scd2-subnet-02` (10.0.2.0/24) — different AZs |
| Route table | `dea-batch-scd2-route-table` (0.0.0.0/0 → IGW, both subnets associated) |
| Internet gateway | `dea-batch-scd2-igw` |
| Security group | `dea-batch-scd2-sg` — inbound All TCP from itself; 3306 from your IP |
| VPC endpoints | `dea-batch-scd2-endpoint` (S3, Gateway); Glue (Interface, private DNS on) |
| RDS | `dea-batch-scd2` (MySQL 8.0), DB `dea`, subnet group `dea-batch-scd2-db-subnet-group` |
| Glue connection | `dea-batch-scd2-rds-connection` — `jdbc:mysql://<RDS_ENDPOINT>:3306/dea` |
| Glue jobs | `dea-batch-scd2-mysql-glue-test-job`, `dea-batch-scd2-mysql-data-extract-glue-job` (Python Shell) |
| Glue workflow / trigger | `dea-batch-scd2-mysql-data-extract-glue-workflow` / `...-workflow-trigger` (daily schedule, UTC) |

## S3 layout

```
s3://<YOUR_S3_DATA_BUCKET>/
  data/product/product_<YYYYMMDD_HHMMSS>.parquet
  checkpoint/product_checkpoint.json

s3://<YOUR_S3_ERROR_BUCKET>/
  dq_errors/product/product_errors_<YYYYMMDD_HHMMSS>.parquet
```
