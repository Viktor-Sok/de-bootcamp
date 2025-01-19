SELECT 
COUNT(CASE WHEN distance.trip_distance <= 1 THEN 1 END) as up_to_i1, 
COUNT(CASE WHEN distance.trip_distance > 1 AND distance.trip_distance <= 3 THEN 1 END) as range_e1_i3,
COUNT(CASE WHEN distance.trip_distance > 3 AND distance.trip_distance <= 7 THEN 1 END) as range_e3_i7, 
COUNT(CASE WHEN distance.trip_distance > 7 AND distance.trip_distance <= 10 THEN 1 END) as range_e7_i10, 
COUNT(CASE WHEN distance.trip_distance > 10 THEN 1 END) as over_e10
FROM
(SELECT trip_distance FROM taxi_trips
WHERE 
lpep_pickup_datetime >= '2019-10-01' AND lpep_dropoff_datetime < '2019-11-01') as distance
