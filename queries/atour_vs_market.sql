WITH base AS (
  SELECT EXTRACT(YEAR FROM IN_DATE) AS yr, ROOM_NIGHTS,
         CASE WHEN SUPPLIER_NO='亚朵' THEN 'atour' ELSE 'other' END AS grp
  FROM hotel_order
  WHERE STATUS IN ('已离店','已确认') AND ROOM_NIGHTS>0
    AND booking_name NOT LIKE '%测试%' AND hotel_name NOT LIKE '%测试%'
    AND EXTRACT(MONTH FROM IN_DATE)<=6
)
SELECT grp, yr, SUM(ROOM_NIGHTS) AS rn FROM base GROUP BY 1,2 ORDER BY 1,2;
