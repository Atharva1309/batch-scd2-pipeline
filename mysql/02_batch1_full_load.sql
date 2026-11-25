-- ============================================================================
-- BATCH 1: FULL LOAD  (Day 1)
-- 10 clean records, first-time load
-- ============================================================================
INSERT INTO dea.product (product_id, product_name, category, unit_price, quantity, supplier_name) VALUES
-- Electronics
(1001, 'Laptop Pro 15',       'Electronics',    1299.99,  45,  'TechSupply Inc'),
(1002, 'Wireless Mouse',      'Electronics',      29.99, 150,  'Peripheral Corp'),
(1003, 'USB-C Cable',         'Electronics',      12.99, 500,  'CableWorks Ltd'),
(1004, '4K Monitor 27-inch',  'Electronics',     399.99,  30,  'TechSupply Inc'),
-- Furniture
(2001, 'Office Desk Oak',     'Furniture',       299.99,  20,  'Furniture Plus'),
(2002, 'Ergonomic Chair',     'Furniture',       249.99,  35,  'Comfort Seating'),
-- Office Supplies
(3001, 'A4 Paper Ream',       'Office Supplies',   5.99, 1000, 'PaperCo Wholesale'),
(3002, 'Ballpoint Pen Set',   'Office Supplies',   8.99,  500, 'Stationery World'),
(3003, 'Sticky Notes Pack',   'Office Supplies',   3.99,  800, 'PaperCo Wholesale'),
(3004, 'Desk Lamp LED',       'Office Supplies',  34.99,   60, 'Lighting Hub');

SELECT * FROM dea.product;
