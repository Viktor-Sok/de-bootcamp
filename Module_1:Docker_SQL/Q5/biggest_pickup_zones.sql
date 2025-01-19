SELECT "Zone" FROM taxi_zones, 
(SELECT "PULocationID" AS location_id, SUM(total_amount) AS all_trips_total_amount  
FROM taxi_trips
WHERE
lpep_pickup_datetime >= '2019-10-18' AND lpep_pickup_datetime < '2019-10-19'
GROUP BY 1
ORDER BY all_trips_total_amount DESC
LIMIT 3) AS t
WHERE t.location_id = "LocationID";
