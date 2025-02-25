-- This query will return a table with the differences between the real 
-- and estimated delivery times by month and year. It will have different 
-- columns: month_no, with the month numbers going from 01 to 12; month, with 
-- the 3 first letters of each month (e.g. Jan, Feb); Year2016_real_time, with 
-- the average delivery time per month of 2016 (NaN if it doesn't exist); 
-- Year2017_real_time, with the average delivery time per month of 2017 (NaN if 
-- it doesn't exist); Year2018_real_time, with the average delivery time per 
-- month of 2018 (NaN if it doesn't exist); Year2016_estimated_time, with the 
-- average estimated delivery time per month of 2016 (NaN if it doesn't exist); 
-- Year2017_estimated_time, with the average estimated delivery time per month 
-- of 2017 (NaN if it doesn't exist) and Year2018_estimated_time, with the 
-- average estimated delivery time per month of 2018 (NaN if it doesn't exist).
SELECT
    t.month_no,
    SUBSTR('--JanFebMarAprMayJunJulAugSepOctNovDec', CAST(t.month_no AS INTEGER) * 3, 3) AS "month",
    AVG(CASE WHEN year = 2016 THEN t.real_time ELSE NULL END) AS "Year2016_real_time",
    AVG(CASE WHEN year = 2017 THEN t.real_time ELSE NULL END) AS "Year2017_real_time",
    AVG(CASE WHEN year = 2018 THEN t.real_time ELSE NULL END) AS "Year2018_real_time",
    AVG(CASE WHEN year = 2016 THEN t.estimated_time ELSE NULL END) AS "Year2016_estimated_time",
    AVG(CASE WHEN year = 2017 THEN t.estimated_time ELSE NULL END) AS "Year2017_estimated_time",
    AVG(CASE WHEN year = 2018 THEN t.estimated_time ELSE NULL END) AS "Year2018_estimated_time"
FROM (
    SELECT
    	DISTINCT oo.order_id,
      STRFTIME('%m', oo.order_purchase_timestamp) AS "month_no",
      CAST(STRFTIME('%Y', oo.order_purchase_timestamp) AS INTEGER) AS "year",
      JULIANDAY(oo.order_delivered_customer_date) - JULIANDAY(oo.order_purchase_timestamp) AS "real_time",
      JULIANDAY(oo.order_estimated_delivery_date) - JULIANDAY(oo.order_purchase_timestamp) AS "estimated_time"
    FROM
        olist_orders oo
    WHERE
        oo.order_status = 'delivered' AND oo.order_delivered_customer_date IS NOT NULL
) t
GROUP BY 
    t.month_no
ORDER BY 
    t.month_no;