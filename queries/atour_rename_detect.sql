WITH base AS (
  SELECT EXTRACT(YEAR FROM IN_DATE) AS yr, HOTEL_ID AS hid, HOTEL_NAME AS hname, ROOM_NIGHTS
  FROM hotel_order
  WHERE SUPPLIER_NO='亚朵' AND STATUS IN ('已离店','已确认') AND ROOM_NIGHTS>0
    AND booking_name NOT LIKE '%测试%' AND hotel_name NOT LIKE '%测试%'
    AND EXTRACT(MONTH FROM IN_DATE)<=6
),
nm AS (SELECT hid, yr, max(hname) hname, SUM(ROOM_NIGHTS) rn
       FROM base GROUP BY 1,2)
SELECT a.hid, a.hname AS n25, b.hname AS n26, a.rn rn25, b.rn rn26
FROM nm a JOIN nm b ON a.hid=b.hid AND a.yr=2025 AND b.yr=2026 AND a.hname<>b.hname;
