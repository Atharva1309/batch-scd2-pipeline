"""
Glue Python Shell job: dea-batch-scd2-mysql-glue-test-job
Tests connectivity from AWS Glue to MySQL on RDS using the Glue JDBC connection.

Job settings:
  - Type: Python Shell (Python 3.9), Load common analytics libraries = Yes
  - IAM role: dea-batch-scd2-aws-role
  - Connections: dea-batch-scd2-rds-connection
  - Job parameter: --additional-python-modules = pymysql
"""

import boto3
import pymysql
from urllib.parse import urlparse

# Fetch connection details from Glue
props = boto3.client("glue", region_name="<Your_AWS_Region>").get_connection(
    Name="<Your_AWS_Glue_Connection_Name>", HidePassword=False
)["Connection"]["ConnectionProperties"]

parsed = urlparse(props["JDBC_CONNECTION_URL"][len("jdbc:"):])

# Test connection
conn = pymysql.connect(
    host=parsed.hostname,
    port=parsed.port or 3306,
    user=props["USERNAME"],
    password=props["PASSWORD"],
    database=parsed.path.strip("/"),
    connect_timeout=10,
)

cursor = conn.cursor()
cursor.execute("SELECT VERSION()")
print("✅ Connected! MySQL version:", cursor.fetchone()[0])

conn.close()
