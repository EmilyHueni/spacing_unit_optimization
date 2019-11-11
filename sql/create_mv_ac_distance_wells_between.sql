--create materialized view production.ac_distance_angle_matrix_eligible_to_neighbor as
--create table production.test_clostest_line as

--create materialized view production.

SELECT t1.*, t2.wells_between FROM production.ac_distance_angle_matrix_eligible_to_neighbor t1
left join 
(SELECT a.row_number, a.api, a.to_api,  a.reservoir, a.to_reservoir, 
a.geom_prod, a.to_geom_prod, (count(b.*)-1) as wells_between
	FROM production.ac_distance_angle_matrix_eligible_to_neighbor a
join 
(
	SELECT api, to_geom_prod as geom_cross
 FROM production.ac_distance_angle_matrix_eligible_to_neighbor
				 where api = '05123443280000'
 				and dist_2d > 0) b
 on st_intersects(geom_cross, st_buffer(st_shortestline(st_line_substring(a.geom_prod, .05::double precision, .95::double precision) , st_line_substring(a.to_geom_prod, .05::double precision, .99::double precision)), 50))									
										
	where a.api = '05123443280000'
	group by a.row_number, a.api, a.to_api,  a.reservoir, a.to_reservoir, 
a.geom_prod, a.to_geom_prod) t2
on t1.api = t2.api and t1.to_api=t2.to_api