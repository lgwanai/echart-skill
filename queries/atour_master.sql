-- 亚朵三年月度间夜/GMV/均价（有效口径）
WITH base AS (
  SELECT date_trunc('month', IN_DATE)::date AS ym,
         EXTRACT(YEAR FROM IN_DATE) AS yr,
         EXTRACT(MONTH FROM IN_DATE) AS mon,
         ROOM_NIGHTS,
         ROOM_PRICE*ROOM_NIGHTS AS gmv
  FROM hotel_order
  WHERE SUPPLIER_NO='亚朵' AND STATUS IN ('已离店','已确认') AND ROOM_NIGHTS>0
    AND booking_name NOT LIKE '%测试%' AND hotel_name NOT LIKE '%测试%'
)
SELECT ym, yr, mon,
       count(*) AS orders,
       SUM(ROOM_NIGHTS) AS room_nights,
       SUM(gmv) AS gmv,
       SUM(gmv)/NULLIF(SUM(ROOM_NIGHTS),0) AS avg_price
FROM base GROUP BY 1,2,3 ORDER BY 1;
