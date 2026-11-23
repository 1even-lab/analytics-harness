-- Ground truth for q1: casino GGR by brand for 2026-10-19 .. 2026-10-25, both adjustments.
SELECT
    if(grouping(company) = 1, 'TOTAL', company)                             AS brand,
    round(sum(if(project = '170', casino_ggr_real_usd, casino_ggr_usd)), 2) AS ggr_usd
FROM demo.gaming_activity
WHERE date >= '2026-10-19'
  AND date <  '2026-10-26'
  AND project != '190'
GROUP BY GROUPING SETS ((company), ())
ORDER BY ggr_usd DESC
