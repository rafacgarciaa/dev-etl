-- This query will return a table with two columns; State, and 
-- Delivery_Difference. The first one will have the letters that identify the 
-- states, and the second one the average difference between the estimate 
-- delivery date and the date when the items were actually delivered to the 
-- customer.
SELECT
  oc.customer_state AS "State",
  CAST(AVG(JULIANDAY(DATE(oo.order_estimated_delivery_date)) - JULIANDAY(DATE(oo.order_delivered_customer_date))) as INT) AS "Delivery_Difference"
FROM olist_orders oo
INNER JOIN olist_customers oc ON oo.customer_id = oc.customer_id
WHERE oo.order_status = 'delivered' AND oo.order_delivered_customer_date IS NOT NULL
GROUP BY oc.customer_state
ORDER BY "Delivery_Difference" ASC;