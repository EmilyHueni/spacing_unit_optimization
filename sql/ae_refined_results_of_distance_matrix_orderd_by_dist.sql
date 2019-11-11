
	
Create materialized view production.ae_refined_results_of_distance_matrix_orderd_by_dist as	
SELECT api, to_api, dist_2d,  to_reservoir, to_depth, percent_near, to_well_drilled_after,
				   case when to_last_prod::date<first_prod::date+365 and to_last_prod::date-(first_prod::date)>0
				   then (to_last_prod::date-(first_prod::date))/365::double precision 
					when to_last_prod::date<first_prod::date+365
					then 0 
					when to_well_drilled_after = 1
					then (to_first_prod::date-(first_prod::date))/365::double precision 
					else 100.00 end as pecent_days_overlap_prod, 
				   row_number() over(partition by api order by dist_2d) as rw
 FROM production.ad_distance_angle_wells_between_matrix_eligible_to_neighbor
	where (wells_between is null or wells_between=0)
	and percent_near>.4
	and dist_2d>20
						 
