WITH base AS (
  SELECT EXTRACT(YEAR FROM IN_DATE) AS yr,
         CASE WHEN EXTRACT(MONTH FROM IN_DATE)<=6 THEN 'H1' END AS half,
         HOTEL_ID AS hid, ROOM_NIGHTS
  FROM hotel_order
  WHERE SUPPLIER_NO='亚朵' AND STATUS IN ('已离店','已确认') AND ROOM_NIGHTS>0
    AND booking_name NOT LIKE '%测试%' AND hotel_name NOT LIKE '%测试%'
    AND EXTRACT(MONTH FROM IN_DATE)<=6
),
yr25 AS (SELECT DISTINCT hid FROM base WHERE yr=2025),
yr26 AS (SELECT DISTINCT hid FROM base WHERE yr=2026),
buckets AS (
  SELECT b.hid,
         CASE WHEN y25.hid IS NOT NULL AND y26.hid IS NOT NULL THEN 'survivor'
              WHEN y25.hid IS NOT NULL THEN 'exited'
              WHEN y26.hid IS NOT NULL THEN 'new'
              ELSE 'none' END AS bucket,
         COALESCE(SUM(CASE WHEN b.yr=2025 THEN ROOM_NIGHTS END),0) AS rn25,
         COALESCE(SUM(CASE WHEN b.yr=2026 THEN ROOM_NIGHTS END),0) AS rn26
  FROM base b
  LEFT JOIN yr25 y25 ON b.hid=y25.hid
  LEFT JOIN yr26 y26 ON b.hid=y26.hid
  GROUP BY 1,2
)
SELECT bucket, count(*) AS hotels,
       SUM(rn25) AS rn_2025, SUM(rn26) AS rn_2026,
       SUM(rn26)-SUM(rn25) AS delta
FROM buckets GROUP BY bucket ORDER BY delta DESC;
