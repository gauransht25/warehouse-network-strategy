-- Run against outputs/warehouse_analysis.sqlite (SQLite syntax)
SELECT city, daily_orders, nearest_baseline_warehouse, baseline_km, optimized_km, distance_saved_km FROM city_coverage ORDER BY distance_saved_km DESC;
SELECT ROUND(SUM(daily_orders * baseline_km)*1.0/SUM(daily_orders),2) AS baseline_weighted_km, ROUND(SUM(daily_orders * optimized_km)*1.0/SUM(daily_orders),2) AS optimized_weighted_km FROM city_coverage;
SELECT COUNT(*) AS cities_over_400_km FROM city_coverage WHERE baseline_km > 400;
