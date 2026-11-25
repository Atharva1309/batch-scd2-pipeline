-- ============================================================================
-- BATCH 3: INCREMENTAL + BAD DATA  (Day 3)
-- ============================================================================

-- Supplier changed on Wireless Mouse
UPDATE dea.product SET quantity = 140, supplier_name = 'NewMouse Supply' WHERE product_id = 1002;

-- Paper price up + quantity consumed
UPDATE dea.product SET unit_price = 6.99, quantity = 800 WHERE product_id = 3001;

-- New product: Document Shredder
INSERT INTO dea.product (product_id, product_name, category, unit_price, quantity, supplier_name)
VALUES (3005, 'Document Shredder', 'Office Supplies', 89.99, 25, 'Security Plus');

-- New product: Water Dispenser
INSERT INTO dea.product (product_id, product_name, category, unit_price, quantity, supplier_name)
VALUES (3006, 'Water Dispenser', 'Office Supplies', 249.99, 12, 'Refresh Corp');

-- ---------- BAD RECORDS (should be rejected by Glue quality checks) ----------

-- BAD: Negative price
INSERT INTO dea.product (product_id, product_name, category, unit_price, quantity, supplier_name)
VALUES (4001, 'Broken Keyboard', 'Electronics', -49.99, 10, 'GamingGear Ltd');

-- BAD: Negative quantity
INSERT INTO dea.product (product_id, product_name, category, unit_price, quantity, supplier_name)
VALUES (4003, 'Mystery Product', 'Office Supplies', 25.50, -15, 'BadSupply Co');

-- BAD: NULL supplier_name
INSERT INTO dea.product (product_id, product_name, category, unit_price, quantity, supplier_name)
VALUES (4007, 'Orphaned Product', 'Electronics', 49.99, 20, NULL);

SELECT * FROM dea.product;
