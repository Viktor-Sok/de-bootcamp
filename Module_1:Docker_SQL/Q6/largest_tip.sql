SELECT "Zone" FROM taxi_zones
WHERE "LocationID" =
(SELECT "DOLocationID" FROM 
	(SELECT MAX(tip_amount) AS max_tip, "DOLocationID" FROM taxi_trips
		WHERE EXTRACT(YEAR FROM lpep_pickup_datetime) = 2019 AND EXTRACT(MONTH FROM lpep_pickup_datetime) = 10 
		AND "PULocationID" = (SELECT "LocationID" FROM taxi_zones WHERE "Zone" LIKE 'East Harlem North')
		GROUP BY 2
		ORDER BY max_tip DESC
		LIMIT 1
	) AS t1
);

