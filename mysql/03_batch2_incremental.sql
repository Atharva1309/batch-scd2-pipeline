-- ============================================================================
-- BATCH 2: INCREMENTAL  (Day 2)
-- ============================================================================

-- Product 1001: Product rebranded (name change)
UPDATE dea.product SET product_name = 'Laptop Pro 15 Gen2' WHERE product_id = 1001;

-- Price increase on Monitor
UPDATE dea.product SET unit_price = 429.99 WHERE product_id = 1004;

-- Product 2002: Chair rebranded AND supplier changed together
UPDATE dea.product SET product_name = 'Ergonomic Chair Pro', supplier_name = 'ErgoWorld Inc' WHERE product_id = 2002;

-- Price increase + quantity consumed on Paper
UPDATE dea.product SET unit_price = 6.49, quantity = 950 WHERE product_id = 3001;

-- New product: Wireless Headphones
INSERT INTO dea.product (product_id, product_name, category, unit_price, quantity, supplier_name)
VALUES (1005, 'Wireless Headphones', 'Electronics', 199.99, 55, 'AudioTech Solutions');

-- New product: Desk Organizer
INSERT INTO dea.product (product_id, product_name, category, unit_price, quantity, supplier_name)
VALUES (2003, 'Desk Organizer Set', 'Furniture', 49.99, 80, 'OfficeSetup Co');

SELECT * FROM dea.product;
