-- #####################################################
-- Code to Setup the Integration between Snowflake & AWS
-- #####################################################

USE ROLE ACCOUNTADMIN;
USE WAREHOUSE COMPUTE_WH;

-- Database and layer schemas (run once)
CREATE DATABASE IF NOT EXISTS DEA_BATCH_SCD2;
USE DATABASE DEA_BATCH_SCD2;

CREATE SCHEMA IF NOT EXISTS RAW;
CREATE SCHEMA IF NOT EXISTS TRANSFORMED;
CREATE SCHEMA IF NOT EXISTS SNAPSHOT;

-- ===== PART A =====
-- Run CREATE ... STORAGE INTEGRATION only once. Re-running CREATE OR REPLACE
-- generates a new external ID and breaks the AWS trust policy.
-- Use ALTER STORAGE INTEGRATION for later changes.
CREATE STORAGE INTEGRATION IF NOT EXISTS DEA_BATCH_SCD2_INT
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::<AWS_ACCOUNT_ID>:role/dea-batch-scd2-snowflake-role'
  STORAGE_ALLOWED_LOCATIONS = ('s3://<YOUR_S3_DATA_BUCKET>/');

DESC INTEGRATION DEA_BATCH_SCD2_INT;
-- Copy STORAGE_AWS_IAM_USER_ARN and STORAGE_AWS_EXTERNAL_ID into
-- aws/iam/snowflake_role_trust_policy.json and apply it to the IAM role.

-- ===== PART B (after updating the trust policy in AWS) =====
CREATE OR REPLACE STAGE DEA_BATCH_SCD2.RAW.DEA_BATCH_SCD2_STAGE
  STORAGE_INTEGRATION = DEA_BATCH_SCD2_INT
  URL = 's3://<YOUR_S3_DATA_BUCKET>'
  FILE_FORMAT = (TYPE = PARQUET);

-- Test the integration
LIST @DEA_BATCH_SCD2.RAW.DEA_BATCH_SCD2_STAGE;
