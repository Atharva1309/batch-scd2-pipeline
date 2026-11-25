-- #############################################
-- Code to Setup the snowflake product_cp table
-- #############################################

USE ROLE ACCOUNTADMIN;
USE WAREHOUSE COMPUTE_WH;

-- COPY table in RAW schema to stage the data from the S3 bucket.
-- Create once: replacing it wipes COPY load history and causes
-- every S3 file to be reloaded (duplicates in PRODUCT_RAW).
CREATE TABLE IF NOT EXISTS DEA_BATCH_SCD2.RAW.PRODUCT_CP
(
    SOURCE_DATA     VARIANT,
    SOURCE_FILENAME STRING,
    INSERT_DTS      TIMESTAMP(6)
);
