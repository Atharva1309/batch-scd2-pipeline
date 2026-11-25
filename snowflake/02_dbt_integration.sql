-- #####################################################
-- Code to Setup the Integration between Snowflake & DBT
-- #####################################################
--
-- Generate the key pair locally (Mac/Linux terminal). Never commit the keys.
--   openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt
--   openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
--   grep -v "PUBLIC KEY" rsa_key.pub | tr -d '\n'      -- prints the value for ALTER USER
--
-- In dbt Cloud: auth method = Key pair, paste the full contents of rsa_key.p8.

USE ROLE ACCOUNTADMIN;
USE WAREHOUSE COMPUTE_WH;

-- Assign the RSA public key to the Snowflake user dbt connects as
ALTER USER <YOUR_USER_NAME> SET RSA_PUBLIC_KEY = '<YOUR_RSA_PUBLIC_KEY>';

-- Verify: RSA_PUBLIC_KEY_FP should have a value
DESC USER <YOUR_USER_NAME>;
