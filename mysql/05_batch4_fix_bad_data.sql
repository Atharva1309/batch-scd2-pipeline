-- ============================================================================
-- BATCH 4 (optional): FIX THE REJECTED RECORDS AT THE SOURCE
-- Fixing a row changes updated_at, so the next Glue run re-extracts it
-- ============================================================================

UPDATE dea.product SET unit_price = 49.99               WHERE product_id = 4001;
UPDATE dea.product SET quantity = 15                    WHERE product_id = 4003;
UPDATE dea.product SET supplier_name = 'Generic Supplies' WHERE product_id = 4007;

SELECT * FROM dea.product WHERE product_id IN (4001, 4003, 4007);
