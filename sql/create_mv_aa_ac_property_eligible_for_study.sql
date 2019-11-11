CREATE MATERIALIZED VIEW production.aa_ac_property_eligible_for_study as 

SELECT row_number() OVER () AS row_number, t1.*,t3.last_prod, t2.wkb_geometry as geom, 

st_line_substring(t2.wkb_geometry,(ST_LENGTH(t2.wkb_geometry)-t1.length)/ST_LENGTH(t2.wkb_geometry)::double precision, .99::double precision) as geom_prod

FROM (SELECT propnum,  api, uwi, wellname, spud_date, date_comp, first_prod, major, 
status, final_status,  field, core_area, reservoir,  well_type, 
current_prod_op, operator_combo, operator, driller_td, tvd, depth, 
ip_formation, ip_perf_upper, ip_perf_lower, length,  completion, prop_type, ceramic, proppant, ppt_per_ft, 
stages, ft_per_stg, treat_psi, treat_rate, slk_wtr, xl_gel, fluid_vol, fluid_type, 
 prior_oil, prior_gas, prior_wtr, cum_365_boe
	FROM production.ac_property
	
	where cum_365_boe is not null -- making sure the wells have  a y label(and were procuding for more than a year)
	and (reservoir like '%NIO%' or reservoir like '%COD%')
	and proppant is not null
	and fluid_vol is not null
	and major = 'OIL'
	and core_area is not null
	and length is not null) t1
	
	left join
	
	gis.petra_all_wells_path_26753_ft t2
	on t1.api = t2.uwi
	
	left join
	
	(SELECT propnum, max(p_date) as last_prod FROM production.ac_product
	where oil > 0 
	GROUP BY propnum) t3
	on t1.propnum=t3.propnum
	
	where t2.uwi is not null
	and (ST_LENGTH(t2.wkb_geometry)-t1.length)/ST_LENGTH(t2.wkb_geometry)::double precision < .9
	and (ST_LENGTH(t2.wkb_geometry)-t1.length)/ST_LENGTH(t2.wkb_geometry)::double precision >0
	--st_line_substring(c.wkb_geometry, 0.5::double precision, 0.99::double precision) AS geom_sub
	