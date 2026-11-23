-- Demo iGaming mart data: synthetic and deterministic (cityHash64, not rand), generated
-- inside ClickHouse, nothing to upload. A FIXED window, 2026-07-04 .. 2026-10-31
-- (120 days, ~880k activity rows): every load gives the same numbers, so the golden set in
-- plugin/evals/golden has universal reference values.
--   clickhouse-client --multiquery < sql/02_data.sql
-- Re-running appends duplicates: TRUNCATE both tables first.
--
-- Traps, on purpose. They mirror the quirks of a real mart; the harness skills must catch
-- them, a bare chat should not:
--   1. project '170' fills ONLY the real-money columns: its standard money columns are NULL
--      and its bet counters are empty, so a plain sum(casino_ggr_usd) silently drops it;
--   2. project '190' must be excluded from gaming_activity entirely, always;
--   3. game_provider_full_name is not 1:1 with the game: the most popular game also shows
--      up under an alias, 'Undefined' and the aggregator's name;
--   4. project '130' has no rows at all on 2026-10-20 .. 2026-10-22.

INSERT INTO demo.gaming_activity
(
    date, company, project, user_id, geo, platform, traffic_source_grouped, is_vip, reg_date,
    game_name, game_provider_full_name, game_aggregator, game_type,
    casino_bet_amount_usd, casino_win_amount_usd, casino_ggr_usd, casino_bet_count,
    casino_bet_amount_real_usd, casino_win_amount_real_usd, casino_ggr_real_usd,
    casino_bet_count_real
)
WITH
    ['110', '120', '130', '140', '150', '160', '170', '190']                    AS codes,
    ['Lumora', 'Kestrel Bet', 'NovaSpin', 'Vantage Casino', 'Orbit Casino',
     'Halcyon Play', 'Corvid Bet', 'Brightwater']                               AS companies,
    ['BR', 'CA', 'DE', 'MX', 'IN', 'CL', 'PE', 'NZ', 'FI', 'JP']               AS geos,
    ['Crash Rocket', 'Sky Dash', 'Pharaoh Vault', 'Fruit Storm', 'Tiki Treasure',
     'Wolf Moon', 'Viking Gold', 'Candy Cascade', 'Neon Sevens', 'Jade Dragon',
     'Buffalo Ridge', 'Auto Roulette Live', 'Speed Baccarat Live', 'Dragon Tiger Live',
     'Blackjack Classic', 'Lucky Wheel Live', 'Mines', 'Plinko Drop', 'Olympus Riches',
     'Sweet Spins']                                                             AS games,
    ['Skyline Studio', 'Skyline Studio', 'Nebula Games', 'Nebula Games', 'Nebula Games',
     'Redstone Studio', 'Redstone Studio', 'Redstone Studio', 'Orbit Play', 'Orbit Play',
     'Orbit Play', 'Velvet Live', 'Velvet Live', 'Velvet Live', 'Ember Gaming',
     'Aurora Live', 'Ember Gaming', 'Ember Gaming', 'Nebula Games', 'Redstone Studio'] AS providers,
    ['crash', 'crash', 'slots', 'slots', 'slots', 'slots', 'slots', 'slots', 'slots',
     'slots', 'slots', 'live', 'live', 'live', 'table', 'live', 'crash', 'crash', 'slots',
     'slots']                                                                   AS types,
    [0.970, 0.970, 0.960, 0.955, 0.960, 0.962, 0.958, 0.965, 0.950, 0.960,
     0.962, 0.973, 0.988, 0.963, 0.990, 0.960, 0.970, 0.968, 0.965, 0.961]      AS rtps,
    number                                                    AS n,
    intDiv(n * 120, 900000)                                   AS day_idx,
    1 + cityHash64(n, 'user') % 40000                         AS uid,
    1 + uid % 8                                               AS p_idx,
    codes[p_idx]                                              AS proj,
    cityHash64(n, 'game')                                     AS hg,
    if(hg % 100 < 18, 1, 2 + intDiv(hg, 100) % 19)            AS g_idx,
    cityHash64(n, 'alias') % 20                               AS ha,
    cityHash64(uid, 'vip') % 100 < 4                          AS vip,
    cityHash64(n, 'bet') % 1000                               AS hb,
    round((5 + hb * hb / 2000.0) * if(vip, 6, 1), 2)          AS bet,
    rtps[g_idx] + ((cityHash64(n, 'win') % 2001) - 1000) / 1000.0 * 0.6 AS ratio,
    round(bet * greatest(ratio, 0), 2)                        AS win,
    0.75 + (cityHash64(n, 'real') % 26) / 100.0               AS share,
    1 + cityHash64(n, 'cnt') % 150                            AS cnt,
    multiIf(g_idx = 1 AND ha < 4, 'Skyline',
            g_idx = 1 AND ha < 7, 'Undefined',
            g_idx = 1 AND ha < 9, 'HubX',
            ha = 19,               'HubX',
            providers[g_idx])                                 AS provider_full
SELECT
    toDate('2026-07-04') + day_idx,
    companies[p_idx],
    proj,
    uid,
    geos[1 + cityHash64(uid, 'geo') % 10],
    ['web', 'mobile'][1 + cityHash64(uid, 'platform') % 2],
    ['organic', 'paid'][1 + cityHash64(uid, 'source') % 2],
    toUInt8(vip),
    toDate('2026-07-04') - cityHash64(uid, 'reg') % 700,
    games[g_idx],
    provider_full,
    if(provider_full = 'HubX', 'Undefined', ['HubX', 'Direct', 'PlayHub'][1 + cityHash64(n, 'agg') % 3]),
    types[g_idx],
    if(proj = '170', NULL, toDecimal64(bet, 2)),
    if(proj = '170', NULL, toDecimal64(win, 2)),
    if(proj = '170', NULL, toDecimal64(bet, 2) - toDecimal64(win, 2)),
    if(proj = '170', NULL, toUInt32(cnt)),
    toDecimal64(bet * share, 2),
    toDecimal64(win * share, 2),
    toDecimal64(bet * share, 2) - toDecimal64(win * share, 2),
    if(proj = '170', toUInt32(0), toUInt32(round(cnt * share)))
FROM numbers(900000)
WHERE NOT (proj = '130' AND day_idx BETWEEN 108 AND 110);

-- Daily P&L per brand. Casino GGR here is already adjusted (project '170' through its
-- real-money GGR, project '190' absent), which is what makes it the reconciliation target.
INSERT INTO demo.daily
SELECT
    date,
    any(company)                                                              AS company,
    project,
    toUInt32(40 + cityHash64(date, project, 'reg') % 90)                      AS registrations,
    toUInt32(25 + cityHash64(date, project, 'dep') % 60)                      AS depositors,
    toDecimal64(depositors * (80 + cityHash64(date, project, 'amt') % 70), 2) AS deposits_usd,
    sum(if(project = '170', casino_ggr_real_usd, casino_ggr_usd))             AS casino_ggr_usd,
    toDecimal64(toFloat64(casino_ggr_usd) * (0.15 + (cityHash64(date, project, 'sport') % 20) / 100.0), 2) AS sport_ggr_usd,
    toDecimal64((toFloat64(casino_ggr_usd) + toFloat64(sport_ggr_usd)) * 0.82, 2) AS ngr_usd,
    toUInt32(uniqExact(user_id))                                              AS active_players
FROM demo.gaming_activity
WHERE project != '190'
GROUP BY date, project;
