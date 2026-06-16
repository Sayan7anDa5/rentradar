-- RentRadar analytical queries over the normalized schema.
-- Each is standalone; run individually.

-- 1. Average rent by city (3-table JOIN), most expensive first.
SELECT c.name AS city,
       ROUND(AVG(li.rent)) AS avg_rent,
       COUNT(*) AS n_listings
FROM listings li
JOIN localities l ON li.locality_id = l.locality_id
JOIN cities c     ON l.city_id = c.city_id
GROUP BY c.name
ORDER BY avg_rent DESC;

-- 2. Furnished premium per city: avg furnished vs unfurnished rent.
SELECT c.name AS city,
       ROUND(AVG(li.rent) FILTER (WHERE li.furnishing = 'Furnished'))   AS furnished_avg,
       ROUND(AVG(li.rent) FILTER (WHERE li.furnishing = 'Unfurnished')) AS unfurnished_avg,
       ROUND(AVG(li.rent) FILTER (WHERE li.furnishing = 'Furnished'))
       - ROUND(AVG(li.rent) FILTER (WHERE li.furnishing = 'Unfurnished')) AS premium
FROM listings li
JOIN localities l ON li.locality_id = l.locality_id
JOIN cities c     ON l.city_id = c.city_id
GROUP BY c.name
ORDER BY premium DESC;

-- 3. Top 10 priciest localities with a reliable sample (>= 10 listings).
SELECT c.name AS city,
       l.name AS locality,
       ROUND(AVG(li.rent)) AS avg_rent,
       COUNT(*) AS n_listings
FROM listings li
JOIN localities l ON li.locality_id = l.locality_id
JOIN cities c     ON l.city_id = c.city_id
GROUP BY c.name, l.name
HAVING COUNT(*) >= 10
ORDER BY avg_rent DESC
LIMIT 10;

-- 4. Price-per-sqft leaders within each city (window function).
SELECT city, locality, avg_rate, city_rank
FROM (
    SELECT c.name AS city,
           l.name AS locality,
           ROUND(AVG(li.area_rate), 2) AS avg_rate,
           RANK() OVER (PARTITION BY c.name ORDER BY AVG(li.area_rate) DESC) AS city_rank
    FROM listings li
    JOIN localities l ON li.locality_id = l.locality_id
    JOIN cities c     ON l.city_id = c.city_id
    GROUP BY c.name, l.name
    HAVING COUNT(*) >= 10
) ranked
WHERE city_rank <= 3
ORDER BY city, city_rank;
