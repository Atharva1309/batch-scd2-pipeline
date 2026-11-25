-- Use the current database
USE dea;

-- Create the product table
-- updated_at is maintained by MySQL and drives the Glue incremental extract
CREATE TABLE dea.product (
    product_id      INT PRIMARY KEY,
    product_name    VARCHAR(255) NOT NULL,
    category        VARCHAR(100) NOT NULL,
    unit_price      DECIMAL(10,2) NOT NULL,
    quantity        INT NOT NULL,
    supplier_name   VARCHAR(255),
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
