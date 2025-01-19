SELECT 
lpep_pickup_datetime AS date,  MAX(taxi_trips.trip_distance) As max_distance_trip
FROM
taxi_trips
GROUP BY 1
ORDER BY max_distance_trip DESC
LIMIT 1;

