WITH base AS (
  SELECT EXTRACT(YEAR FROM IN_DATE) AS yr,
         EXTRACT(MONTH FROM IN_DATE) AS mon,
         ROOM_NIGHTS
  FROM hotel_order
  WHERE SUPPLIER_NO='亚朵'
    AND STATUS IN ('已离店','已确认')
    AND ROOM_NIGHTS > 0
    AND booking_name NOT LIKE '%测试%'
    AND hotel_name NOT LIKE '%测试%'
)
SELECT yr, mon, COUNT(*) AS orders, SUM(ROOM_NIGHTS) AS room_nights
FROM base GROUP BY 1,2 ORDER BY 1,2;
