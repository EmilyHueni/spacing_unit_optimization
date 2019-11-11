create materialized view  production.ab_distance_matrix_eligible_to_neighbor as

SELECT 
row_number() OVER () AS row_number,
a.api, b.api as to_api, a.first_prod, b.first_prod as to_first_prod, a.last_prod, b.last_prod as to_last_prod, 
case WHEN (a.first_prod::date)>=b.first_prod THEN 0 ELSE 1 END to_well_drilled_after,
st_distance(a.geom_prod, b.geom_prod) as dist_2d, a.reservoir, b.reservoir as to_reservoir, 
a.depth, b.depth as to_depth, a.geom_prod, b.geom_prod as to_geom_prod
	FROM production.aa_ac_property_eligible_for_study a,
	production.aa_ac_property_eligible_for_study_neighbors b
	where 
	st_dwithin(a.geom_prod, b.geom_prod, 2000)
	and
	a.api<>b.api
	and 
	(a.first_prod::date+365)>=b.first_prod
	