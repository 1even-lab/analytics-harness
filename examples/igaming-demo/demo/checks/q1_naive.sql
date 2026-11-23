-- The obvious query for q1, and why it is wrong: one brand comes out NULL (it reports
-- real-money columns only) and an excluded project is counted in.
-- Compare with checks/q1.sql on stage.
SELECT
    if(grouping(company) = 1, 'TOTAL', company) AS brand,
    round(sum(casino_ggr_usd), 2)               AS ggr_usd_naive
FROM demo.gaming_activity
WHERE date >= '2026-10-19'
  AND date <  '2026-10-26'
GROUP BY GROUPING SETS ((company), ())
ORDER BY ggr_usd_naive DESC
