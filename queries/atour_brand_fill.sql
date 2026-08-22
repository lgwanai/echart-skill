SELECT EXTRACT(YEAR FROM IN_DATE) AS yr,
       count(*) AS total,
       count(*) FILTER (WHERE HOTEL_BRAND IS NOT NULL AND HOTEL_BRAND <> '' AND HOTEL_BRAND <> '未知') AS with_brand,
       count(*) FILTER (WHERE HOTEL_BRAND IS NULL OR HOTEL_BRAND='' OR HOTEL_BRAND='未知') AS no_brand,
       count(DISTINCT HOTEL_NAME) AS hotels
FROM hotel_order
WHERE SUPPLIER_NO='亚朵'
GROUP BY 1 ORDER BY 1;
