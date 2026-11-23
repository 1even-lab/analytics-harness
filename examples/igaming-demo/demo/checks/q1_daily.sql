-- The same total from demo.daily, where casino GGR is already adjusted.
-- Must equal the TOTAL row of checks/q1.sql.
SELECT round(sum(casino_ggr_usd), 2) AS ggr_usd_daily
FROM demo.daily
WHERE date >= '2026-10-19'
  AND date <  '2026-10-26'
