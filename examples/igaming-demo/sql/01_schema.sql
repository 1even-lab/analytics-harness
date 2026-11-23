-- Demo iGaming mart: fictional brands and players, synthetic data.
-- Run as an admin of a DEMO ClickHouse (never a production cluster):
--   clickhouse-client --multiquery < sql/01_schema.sql
-- The shape follows a real casino mart (one row per player per day per game), so the
-- skills in .claude/skills apply to it the way they apply to the real one.

CREATE DATABASE IF NOT EXISTS demo;

CREATE TABLE IF NOT EXISTS demo.gaming_activity
(
    date                        Date                    COMMENT 'Activity date (UTC)',
    company                     LowCardinality(String)  COMMENT 'Brand',
    project                     LowCardinality(String)  COMMENT 'Internal project code, a string. Never shown to report recipients',
    user_id                     UInt64                  COMMENT 'Player id within the project',
    geo                         LowCardinality(String)  COMMENT 'Player country, ISO 3166-1 alpha-2',
    platform                    LowCardinality(String)  COMMENT 'Lifetime player platform: web | mobile',
    traffic_source_grouped      LowCardinality(String)  COMMENT 'Acquisition channel: organic | paid',
    is_vip                      UInt8                   COMMENT '1 = VIP player',
    reg_date                    Date                    COMMENT 'Player registration date',
    game_name                   LowCardinality(String)  COMMENT 'Game name, normalized. The same name at different providers can be different games (live tables)',
    game_provider_full_name     LowCardinality(String)  COMMENT 'Provider as reported by the feed. NOT normalized: aliases and aggregator names occur; not 1:1 with the game',
    game_aggregator             LowCardinality(String)  COMMENT 'Aggregator the game was played through; Undefined when unknown',
    game_type                   LowCardinality(String)  COMMENT 'slots | live | crash | table',
    casino_bet_amount_usd       Nullable(Decimal(18, 2)) COMMENT 'Handle incl. bonus money, USD. NULL for projects that report real-money columns only',
    casino_win_amount_usd       Nullable(Decimal(18, 2)) COMMENT 'Payouts incl. bonus money, USD. NULL for projects that report real-money columns only',
    casino_ggr_usd              Nullable(Decimal(18, 2)) COMMENT 'GGR = bet - win incl. bonus money, USD. NULL for projects that report real-money columns only',
    casino_bet_count            Nullable(UInt32)         COMMENT 'Number of bets incl. bonus bets',
    casino_bet_amount_real_usd  Nullable(Decimal(18, 2)) COMMENT 'Real-money handle (no bonus), USD',
    casino_win_amount_real_usd  Nullable(Decimal(18, 2)) COMMENT 'Real-money payouts (no bonus), USD',
    casino_ggr_real_usd         Nullable(Decimal(18, 2)) COMMENT 'Real-money GGR (no bonus), USD',
    casino_bet_count_real       Nullable(UInt32)         COMMENT 'Number of real-money bets'
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(date)
ORDER BY (date, project, user_id, game_name)
COMMENT 'Casino activity: one row per player per day per game / provider / aggregator. Casino vertical only (no sportsbook, poker, payments). Money in USD.';

CREATE TABLE IF NOT EXISTS demo.daily
(
    date            Date                   COMMENT 'Date (UTC)',
    company         LowCardinality(String) COMMENT 'Brand',
    project         LowCardinality(String) COMMENT 'Internal project code, a string. Never shown to report recipients',
    registrations   UInt32                 COMMENT 'New registrations',
    depositors      UInt32                 COMMENT 'Players with at least one deposit that day',
    deposits_usd    Decimal(18, 2)         COMMENT 'Deposits, USD',
    casino_ggr_usd  Decimal(18, 2)         COMMENT 'Casino GGR, USD, mandatory adjustments already applied (reconciles with gaming_activity)',
    sport_ggr_usd   Decimal(18, 2)         COMMENT 'Sportsbook GGR, USD',
    ngr_usd         Decimal(18, 2)         COMMENT 'NGR = GGR of all products minus bonus cost and taxes, USD',
    active_players  UInt32                 COMMENT 'Players with casino activity that day'
)
ENGINE = MergeTree
ORDER BY (date, project)
COMMENT 'Daily P&L per brand across products: one row per project per day. The reference for cross-product numbers and for reconciling casino GGR.';
