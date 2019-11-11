create materialized view production.ac_distance_angle_matrix_eligible_to_neighbor as
SELECT row_number, api, to_api, first_prod, to_first_prod, last_prod, to_last_prod, to_well_drilled_after, dist_2d, reservoir, to_reservoir, 
depth, to_depth, 
st_length(st_intersection(st_buffer(geom_prod, dist_2d +150), to_geom_prod))/st_length(geom_prod) as percent_near, 
degrees(st_angle(to_geom_prod, geom_prod)) as angle,
geom_prod, to_geom_prod
	FROM production.ab_distance_matrix_eligible_to_neighbor
	