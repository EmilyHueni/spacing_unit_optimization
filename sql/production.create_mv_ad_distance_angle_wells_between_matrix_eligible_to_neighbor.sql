
create materialized view production.ad_distance_angle_wells_between_matrix_eligible_to_neighbor as
SELECT t0.*, case when t2.wells_between is null then 0 else t2.wells_between end as wells_between FROM production.ac_distance_angle_matrix_eligible_to_neighbor t0
left join 
(
SELECT t1.api, t1.to_api, count(CASE WHEN intersects then 1 END) as wells_between
FROM
(SELECT a.api, a.to_api, st_intersects(b.to_geom_prod, a.geom_shortest_line) intersects										
FROM (SELECT  api,  to_api, dist_2d,
st_buffer(st_shortestline(st_line_substring(geom_prod, .05::double precision, .95::double precision) , st_line_substring(to_geom_prod, .05::double precision, .99::double precision)), 50) as geom_shortest_line
FROM production.ac_distance_angle_matrix_eligible_to_neighbor
where dist_2d>0) a
left join
production.ac_distance_angle_matrix_eligible_to_neighbor b
on a.api=b.api and a.dist_2d>b.dist_2d
where a.to_api<>b.to_api
		 ) t1
GROUP BY t1.api, t1.to_api	

) t2
on t0.api = t2.api and t0.to_api=t2.to_api

