# Data Dictionary

**Version:** 1.0
**Last Updated:** 2025-01-15
**Purpose:** Complete reference for all data entities, fields, and relationships

---

## Table of Contents

1. [Database Overview](#database-overview)
2. [Core Tables](#core-tables)
3. [User Management](#user-management)
4. [Fantasy Management](#fantasy-management)
5. [ML & Predictions](#ml--predictions)
6. [System Tables](#system-tables)
7. [Relationships](#relationships)
8. [Data Types Reference](#data-types-reference)
9. [Enumerations](#enumerations)
10. [ML Feature Engineering](#ml-feature-engineering)
11. [Data Retention](#data-retention)

---

## Database Overview

### Schema Summary

| Category | Tables | Description |
|----------|--------|-------------|
| Core | 8 | NBA teams, players, stats, schedule, defense |
| User Management | 4 | Users, auth, tokens |
| Fantasy | 6 | Leagues, teams, rosters, matchups |
| ML & Predictions | 4 | Predictions, accuracy, features |
| System | 3 | Audit, jobs, cache |

### Naming Conventions

- Tables: `snake_case`, plural (e.g., `players`, `user_teams`)
- Primary Keys: `id` (UUID or BIGINT)
- Foreign Keys: `{table_singular}_id` (e.g., `player_id`, `user_id`)
- Timestamps: `created_at`, `updated_at`
- Booleans: `is_` prefix (e.g., `is_active`, `is_premium`)

---

## Core Tables

### `nba_teams`

NBA franchise information.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | - | NBA team ID (official) |
| `abbreviation` | VARCHAR(3) | NO | - | Team abbreviation (e.g., "LAL") |
| `full_name` | VARCHAR(100) | NO | - | Full team name |
| `city` | VARCHAR(50) | NO | - | Team city |
| `nickname` | VARCHAR(50) | NO | - | Team nickname |
| `conference` | VARCHAR(4) | NO | - | "East" or "West" |
| `division` | VARCHAR(20) | NO | - | Division name |
| `arena` | VARCHAR(100) | YES | NULL | Home arena name |
| `year_founded` | INTEGER | YES | NULL | Franchise founding year |
| `is_active` | BOOLEAN | NO | true | Currently active franchise |
| `created_at` | TIMESTAMP | NO | NOW() | Record creation time |
| `updated_at` | TIMESTAMP | NO | NOW() | Last update time |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`abbreviation`)

---

### `players`

NBA player master data.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INTEGER | NO | - | NBA player ID (official) |
| `first_name` | VARCHAR(50) | NO | - | Player first name |
| `last_name` | VARCHAR(50) | NO | - | Player last name |
| `full_name` | VARCHAR(100) | NO | - | Full display name |
| `position` | VARCHAR(5) | YES | NULL | Primary position (PG/SG/SF/PF/C) |
| `positions` | VARCHAR(15)[] | YES | NULL | All eligible positions |
| `team_id` | INTEGER | YES | NULL | Current NBA team ID |
| `jersey_number` | VARCHAR(5) | YES | NULL | Jersey number |
| `height` | VARCHAR(10) | YES | NULL | Height (e.g., "6-6") |
| `weight` | INTEGER | YES | NULL | Weight in pounds |
| `birth_date` | DATE | YES | NULL | Date of birth |
| `country` | VARCHAR(50) | YES | NULL | Country of origin |
| `draft_year` | INTEGER | YES | NULL | NBA draft year |
| `draft_round` | INTEGER | YES | NULL | Draft round |
| `draft_number` | INTEGER | YES | NULL | Draft pick number |
| `roster_status` | VARCHAR(20) | YES | "Active" | Current roster status |
| `is_active` | BOOLEAN | NO | true | Currently in NBA |
| `headshot_url` | VARCHAR(500) | YES | NULL | Player photo URL |
| `created_at` | TIMESTAMP | NO | NOW() | Record creation time |
| `updated_at` | TIMESTAMP | NO | NOW() | Last update time |

**Indexes:**
- PRIMARY KEY (`id`)
- INDEX (`team_id`)
- INDEX (`position`)
- INDEX (`is_active`)
- INDEX (`full_name`) - for search

---

### `player_game_stats`

Individual game statistics.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `player_id` | INTEGER | NO | - | FK to players |
| `game_id` | VARCHAR(20) | NO | - | NBA game ID |
| `game_date` | DATE | NO | - | Game date |
| `season` | VARCHAR(10) | NO | - | Season (e.g., "2024-25") |
| `season_type` | VARCHAR(20) | NO | "Regular" | Regular/Playoffs/PreSeason |
| `team_id` | INTEGER | NO | - | Player's team for this game |
| `opponent_team_id` | INTEGER | NO | - | Opponent team |
| `is_home` | BOOLEAN | NO | - | Home game flag |
| `result` | CHAR(1) | YES | NULL | W/L |
| `minutes` | DECIMAL(5,2) | YES | NULL | Minutes played |
| `points` | INTEGER | YES | 0 | Points scored |
| `rebounds` | INTEGER | YES | 0 | Total rebounds |
| `offensive_rebounds` | INTEGER | YES | 0 | Offensive rebounds |
| `defensive_rebounds` | INTEGER | YES | 0 | Defensive rebounds |
| `assists` | INTEGER | YES | 0 | Assists |
| `steals` | INTEGER | YES | 0 | Steals |
| `blocks` | INTEGER | YES | 0 | Blocks |
| `turnovers` | INTEGER | YES | 0 | Turnovers |
| `personal_fouls` | INTEGER | YES | 0 | Personal fouls |
| `fgm` | INTEGER | YES | 0 | Field goals made |
| `fga` | INTEGER | YES | 0 | Field goals attempted |
| `fg_pct` | DECIMAL(5,3) | YES | NULL | Field goal percentage |
| `fg3m` | INTEGER | YES | 0 | 3-pointers made |
| `fg3a` | INTEGER | YES | 0 | 3-pointers attempted |
| `fg3_pct` | DECIMAL(5,3) | YES | NULL | 3-point percentage |
| `ftm` | INTEGER | YES | 0 | Free throws made |
| `fta` | INTEGER | YES | 0 | Free throws attempted |
| `ft_pct` | DECIMAL(5,3) | YES | NULL | Free throw percentage |
| `plus_minus` | INTEGER | YES | 0 | Plus/minus |
| `fantasy_points` | DECIMAL(6,2) | YES | NULL | Calculated fantasy points |
| `created_at` | TIMESTAMP | NO | NOW() | Record creation time |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`player_id`, `game_id`)
- INDEX (`player_id`, `game_date`)
- INDEX (`game_date`)
- INDEX (`season`)

---

### `player_season_stats`

Aggregated season statistics.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `player_id` | INTEGER | NO | - | FK to players |
| `season` | VARCHAR(10) | NO | - | Season (e.g., "2024-25") |
| `team_id` | INTEGER | NO | - | Primary team for season |
| `games_played` | INTEGER | NO | 0 | Games played |
| `games_started` | INTEGER | NO | 0 | Games started |
| `minutes_total` | DECIMAL(7,2) | NO | 0 | Total minutes |
| `minutes_pg` | DECIMAL(5,2) | YES | NULL | Minutes per game |
| `points_pg` | DECIMAL(5,2) | YES | NULL | Points per game |
| `rebounds_pg` | DECIMAL(5,2) | YES | NULL | Rebounds per game |
| `assists_pg` | DECIMAL(5,2) | YES | NULL | Assists per game |
| `steals_pg` | DECIMAL(5,2) | YES | NULL | Steals per game |
| `blocks_pg` | DECIMAL(5,2) | YES | NULL | Blocks per game |
| `turnovers_pg` | DECIMAL(5,2) | YES | NULL | Turnovers per game |
| `fg3m_pg` | DECIMAL(5,2) | YES | NULL | 3-pointers per game |
| `fgm_pg` | DECIMAL(5,2) | YES | NULL | FG made per game |
| `fga_pg` | DECIMAL(5,2) | YES | NULL | FG attempted per game |
| `fg_pct` | DECIMAL(5,3) | YES | NULL | Field goal percentage |
| `fg3_pct` | DECIMAL(5,3) | YES | NULL | 3-point percentage |
| `ft_pct` | DECIMAL(5,3) | YES | NULL | Free throw percentage |
| `usage_rate` | DECIMAL(5,2) | YES | NULL | Usage rate |
| `true_shooting_pct` | DECIMAL(5,3) | YES | NULL | True shooting % |
| `effective_fg_pct` | DECIMAL(5,3) | YES | NULL | Effective FG % |
| `fantasy_ppg` | DECIMAL(6,2) | YES | NULL | Fantasy points per game |
| `last_calculated_at` | TIMESTAMP | YES | NULL | Last recalculation time |
| `created_at` | TIMESTAMP | NO | NOW() | Record creation time |
| `updated_at` | TIMESTAMP | NO | NOW() | Last update time |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`player_id`, `season`)
- INDEX (`season`)

---

### `player_injuries`

Injury tracking and history.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `player_id` | INTEGER | NO | - | FK to players |
| `status` | VARCHAR(20) | NO | - | HEALTHY/QUESTIONABLE/DOUBTFUL/OUT/GTD |
| `injury_type` | VARCHAR(100) | YES | NULL | Type of injury |
| `body_part` | VARCHAR(50) | YES | NULL | Affected body part |
| `description` | TEXT | YES | NULL | Detailed description |
| `reported_date` | DATE | NO | - | Date injury reported |
| `expected_return` | DATE | YES | NULL | Expected return date |
| `actual_return` | DATE | YES | NULL | Actual return date |
| `games_missed` | INTEGER | YES | 0 | Games missed |
| `source` | VARCHAR(50) | YES | NULL | Information source |
| `is_active` | BOOLEAN | NO | true | Currently active injury |
| `created_at` | TIMESTAMP | NO | NOW() | Record creation time |
| `updated_at` | TIMESTAMP | NO | NOW() | Last update time |

**Indexes:**
- PRIMARY KEY (`id`)
- INDEX (`player_id`, `is_active`)
- INDEX (`status`)
- INDEX (`reported_date`)

---

## User Management

### `users`

User accounts.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `email` | VARCHAR(255) | NO | - | Email address (unique) |
| `username` | VARCHAR(50) | NO | - | Username (unique) |
| `password_hash` | VARCHAR(255) | NO | - | Bcrypt password hash |
| `is_active` | BOOLEAN | NO | true | Account active flag |
| `is_verified` | BOOLEAN | NO | false | Email verified flag |
| `is_premium` | BOOLEAN | NO | false | Premium subscription |
| `premium_expires_at` | TIMESTAMP | YES | NULL | Premium expiration |
| `avatar_url` | VARCHAR(500) | YES | NULL | Profile picture URL |
| `timezone` | VARCHAR(50) | YES | "UTC" | User timezone |
| `notification_prefs` | JSONB | YES | '{}' | Notification settings |
| `last_login_at` | TIMESTAMP | YES | NULL | Last login time |
| `login_count` | INTEGER | NO | 0 | Total login count |
| `created_at` | TIMESTAMP | NO | NOW() | Account creation time |
| `updated_at` | TIMESTAMP | NO | NOW() | Last update time |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`email`)
- UNIQUE (`username`)
- INDEX (`is_active`)

---

### `refresh_tokens`

JWT refresh token storage.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `user_id` | UUID | NO | - | FK to users |
| `token_hash` | VARCHAR(255) | NO | - | Hashed refresh token |
| `device_id` | VARCHAR(100) | YES | NULL | Device identifier |
| `device_info` | JSONB | YES | NULL | Device metadata |
| `ip_address` | INET | YES | NULL | Client IP address |
| `expires_at` | TIMESTAMP | NO | - | Token expiration |
| `revoked_at` | TIMESTAMP | YES | NULL | Revocation time |
| `created_at` | TIMESTAMP | NO | NOW() | Token creation time |

**Indexes:**
- PRIMARY KEY (`id`)
- INDEX (`user_id`)
- INDEX (`token_hash`)
- INDEX (`expires_at`)

---

### `user_sessions`

Active user sessions.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `user_id` | UUID | NO | - | FK to users |
| `session_token` | VARCHAR(255) | NO | - | Session token |
| `device_type` | VARCHAR(20) | YES | NULL | web/mobile/tablet |
| `browser` | VARCHAR(100) | YES | NULL | Browser info |
| `os` | VARCHAR(50) | YES | NULL | Operating system |
| `ip_address` | INET | YES | NULL | Client IP |
| `last_activity` | TIMESTAMP | NO | NOW() | Last activity time |
| `expires_at` | TIMESTAMP | NO | - | Session expiration |
| `created_at` | TIMESTAMP | NO | NOW() | Session creation time |

**Indexes:**
- PRIMARY KEY (`id`)
- INDEX (`user_id`)
- INDEX (`session_token`)
- INDEX (`expires_at`)

---

### `yahoo_tokens`

Yahoo OAuth tokens.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `user_id` | UUID | NO | - | FK to users |
| `access_token` | TEXT | NO | - | Encrypted access token |
| `refresh_token` | TEXT | NO | - | Encrypted refresh token |
| `token_type` | VARCHAR(20) | NO | "bearer" | Token type |
| `expires_at` | TIMESTAMP | NO | - | Access token expiration |
| `scope` | VARCHAR(255) | YES | NULL | OAuth scopes |
| `yahoo_guid` | VARCHAR(50) | YES | NULL | Yahoo user GUID |
| `created_at` | TIMESTAMP | NO | NOW() | Token creation time |
| `updated_at` | TIMESTAMP | NO | NOW() | Last refresh time |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`user_id`)
- INDEX (`expires_at`)

---

## Fantasy Management

### `yahoo_leagues`

Synced Yahoo fantasy leagues.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `user_id` | UUID | NO | - | FK to users |
| `yahoo_league_id` | VARCHAR(50) | NO | - | Yahoo league ID |
| `yahoo_league_key` | VARCHAR(100) | NO | - | Yahoo league key |
| `name` | VARCHAR(200) | NO | - | League name |
| `season` | VARCHAR(10) | NO | - | Season year |
| `num_teams` | INTEGER | NO | - | Number of teams |
| `scoring_type` | VARCHAR(20) | NO | - | head/roto/points |
| `draft_status` | VARCHAR(20) | YES | NULL | Draft status |
| `current_week` | INTEGER | YES | NULL | Current matchup week |
| `start_week` | INTEGER | YES | NULL | Season start week |
| `end_week` | INTEGER | YES | NULL | Season end week |
| `is_active` | BOOLEAN | NO | true | League active flag |
| `settings` | JSONB | YES | '{}' | League settings |
| `last_synced_at` | TIMESTAMP | YES | NULL | Last sync time |
| `created_at` | TIMESTAMP | NO | NOW() | Record creation time |
| `updated_at` | TIMESTAMP | NO | NOW() | Last update time |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`user_id`, `yahoo_league_key`)
- INDEX (`user_id`)
- INDEX (`season`)

---

### `user_teams`

User's fantasy teams.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `user_id` | UUID | NO | - | FK to users |
| `league_id` | UUID | NO | - | FK to yahoo_leagues |
| `yahoo_team_id` | VARCHAR(50) | NO | - | Yahoo team ID |
| `yahoo_team_key` | VARCHAR(100) | NO | - | Yahoo team key |
| `name` | VARCHAR(200) | NO | - | Team name |
| `logo_url` | VARCHAR(500) | YES | NULL | Team logo URL |
| `manager_name` | VARCHAR(100) | YES | NULL | Manager name |
| `waiver_priority` | INTEGER | YES | NULL | Waiver wire priority |
| `faab_balance` | DECIMAL(8,2) | YES | NULL | FAAB budget remaining |
| `moves_made` | INTEGER | YES | 0 | Total moves made |
| `trades_made` | INTEGER | YES | 0 | Total trades made |
| `wins` | INTEGER | NO | 0 | Total wins |
| `losses` | INTEGER | NO | 0 | Total losses |
| `ties` | INTEGER | NO | 0 | Total ties |
| `points_for` | DECIMAL(10,2) | YES | 0 | Total points scored |
| `points_against` | DECIMAL(10,2) | YES | 0 | Total points against |
| `standing_rank` | INTEGER | YES | NULL | Current standing |
| `playoff_seed` | INTEGER | YES | NULL | Playoff seed |
| `is_active` | BOOLEAN | NO | true | Team active flag |
| `last_synced_at` | TIMESTAMP | YES | NULL | Last sync time |
| `created_at` | TIMESTAMP | NO | NOW() | Record creation time |
| `updated_at` | TIMESTAMP | NO | NOW() | Last update time |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`league_id`, `yahoo_team_key`)
- INDEX (`user_id`)
- INDEX (`league_id`)

---

### `team_rosters`

Current team rosters.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `team_id` | UUID | NO | - | FK to user_teams |
| `player_id` | INTEGER | NO | - | FK to players |
| `roster_position` | VARCHAR(10) | NO | - | PG/SG/SF/PF/C/G/F/UTIL/BN/IL |
| `is_starter` | BOOLEAN | NO | false | Starting lineup flag |
| `acquisition_type` | VARCHAR(20) | YES | NULL | draft/trade/waiver/free_agent |
| `acquisition_date` | DATE | YES | NULL | Date acquired |
| `acquisition_cost` | DECIMAL(8,2) | YES | NULL | FAAB cost if applicable |
| `is_droppable` | BOOLEAN | NO | true | Can be dropped flag |
| `created_at` | TIMESTAMP | NO | NOW() | Record creation time |
| `updated_at` | TIMESTAMP | NO | NOW() | Last update time |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`team_id`, `player_id`)
- INDEX (`team_id`)
- INDEX (`player_id`)

---

### `matchups`

Weekly fantasy matchups.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `league_id` | UUID | NO | - | FK to yahoo_leagues |
| `team_id` | UUID | NO | - | FK to user_teams |
| `opponent_team_id` | UUID | YES | NULL | Opponent team (null for bye) |
| `week_number` | INTEGER | NO | - | Matchup week |
| `week_start_date` | DATE | NO | - | Week start date |
| `week_end_date` | DATE | NO | - | Week end date |
| `is_playoff` | BOOLEAN | NO | false | Playoff matchup flag |
| `team_score` | DECIMAL(10,2) | YES | NULL | Team's score |
| `opponent_score` | DECIMAL(10,2) | YES | NULL | Opponent's score |
| `result` | CHAR(1) | YES | NULL | W/L/T |
| `category_wins` | INTEGER | YES | NULL | Categories won (H2H) |
| `category_losses` | INTEGER | YES | NULL | Categories lost |
| `category_ties` | INTEGER | YES | NULL | Categories tied |
| `projected_score` | DECIMAL(10,2) | YES | NULL | Projected team score |
| `projected_opponent` | DECIMAL(10,2) | YES | NULL | Projected opponent score |
| `win_probability` | DECIMAL(5,4) | YES | NULL | Win probability 0-1 |
| `is_final` | BOOLEAN | NO | false | Matchup finalized |
| `created_at` | TIMESTAMP | NO | NOW() | Record creation time |
| `updated_at` | TIMESTAMP | NO | NOW() | Last update time |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`team_id`, `week_number`)
- INDEX (`league_id`, `week_number`)

---

### `recommendations`

AI-generated recommendations.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `team_id` | UUID | NO | - | FK to user_teams |
| `type` | VARCHAR(30) | NO | - | start_sit/waiver_add/waiver_drop/trade |
| `priority` | VARCHAR(10) | NO | "medium" | critical/high/medium/low |
| `player_id` | INTEGER | YES | NULL | Primary player |
| `secondary_player_id` | INTEGER | YES | NULL | Secondary player (over/for) |
| `action` | VARCHAR(20) | YES | NULL | start/sit/add/drop |
| `reasoning` | TEXT | NO | - | Explanation text |
| `detailed_analysis` | TEXT | YES | NULL | Extended analysis |
| `confidence` | DECIMAL(5,4) | NO | - | Confidence score 0-1 |
| `expected_value` | DECIMAL(8,4) | YES | NULL | Expected Z-score impact |
| `factors` | JSONB | YES | '[]' | Contributing factors |
| `valid_from` | TIMESTAMP | NO | NOW() | Recommendation start |
| `valid_until` | TIMESTAMP | NO | - | Recommendation expiration |
| `status` | VARCHAR(20) | NO | "active" | active/accepted/rejected/expired |
| `user_feedback` | VARCHAR(20) | YES | NULL | helpful/not_helpful |
| `action_taken` | VARCHAR(50) | YES | NULL | User's actual action |
| `created_at` | TIMESTAMP | NO | NOW() | Record creation time |
| `updated_at` | TIMESTAMP | NO | NOW() | Last update time |

**Indexes:**
- PRIMARY KEY (`id`)
- INDEX (`team_id`, `status`)
- INDEX (`type`)
- INDEX (`valid_until`)

---

### `waiver_claims`

Waiver wire claim tracking.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `team_id` | UUID | NO | - | FK to user_teams |
| `add_player_id` | INTEGER | NO | - | Player to add |
| `drop_player_id` | INTEGER | YES | NULL | Player to drop |
| `priority` | INTEGER | YES | NULL | Claim priority |
| `faab_bid` | DECIMAL(8,2) | YES | NULL | FAAB bid amount |
| `claim_date` | DATE | NO | - | Waiver process date |
| `status` | VARCHAR(20) | NO | "pending" | pending/successful/failed |
| `failure_reason` | VARCHAR(200) | YES | NULL | Why claim failed |
| `processed_at` | TIMESTAMP | YES | NULL | Processing time |
| `created_at` | TIMESTAMP | NO | NOW() | Record creation time |

**Indexes:**
- PRIMARY KEY (`id`)
- INDEX (`team_id`, `status`)
- INDEX (`claim_date`)

---

## ML & Predictions

### `player_predictions`

ML model predictions.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `player_id` | INTEGER | NO | - | FK to players |
| `game_date` | DATE | NO | - | Prediction target date |
| `opponent_team_id` | INTEGER | YES | NULL | Opponent team |
| `is_home` | BOOLEAN | YES | NULL | Home game flag |
| `pred_minutes` | DECIMAL(5,2) | YES | NULL | Predicted minutes |
| `pred_minutes_low` | DECIMAL(5,2) | YES | NULL | Minutes lower bound |
| `pred_minutes_high` | DECIMAL(5,2) | YES | NULL | Minutes upper bound |
| `pred_points` | DECIMAL(5,2) | YES | NULL | Predicted points |
| `pred_points_low` | DECIMAL(5,2) | YES | NULL | Points lower bound |
| `pred_points_high` | DECIMAL(5,2) | YES | NULL | Points upper bound |
| `pred_rebounds` | DECIMAL(5,2) | YES | NULL | Predicted rebounds |
| `pred_rebounds_low` | DECIMAL(5,2) | YES | NULL | Rebounds lower bound |
| `pred_rebounds_high` | DECIMAL(5,2) | YES | NULL | Rebounds upper bound |
| `pred_assists` | DECIMAL(5,2) | YES | NULL | Predicted assists |
| `pred_assists_low` | DECIMAL(5,2) | YES | NULL | Assists lower bound |
| `pred_assists_high` | DECIMAL(5,2) | YES | NULL | Assists upper bound |
| `pred_steals` | DECIMAL(5,2) | YES | NULL | Predicted steals |
| `pred_blocks` | DECIMAL(5,2) | YES | NULL | Predicted blocks |
| `pred_turnovers` | DECIMAL(5,2) | YES | NULL | Predicted turnovers |
| `pred_fg3m` | DECIMAL(5,2) | YES | NULL | Predicted 3PM |
| `pred_fg_pct` | DECIMAL(5,3) | YES | NULL | Predicted FG% |
| `pred_ft_pct` | DECIMAL(5,3) | YES | NULL | Predicted FT% |
| `pred_fantasy_points` | DECIMAL(6,2) | YES | NULL | Predicted fantasy points |
| `total_z_score` | DECIMAL(8,4) | YES | NULL | Total Z-score |
| `confidence` | DECIMAL(5,4) | NO | - | Overall confidence 0-1 |
| `injury_risk` | DECIMAL(5,4) | YES | 0 | Injury probability |
| `factors` | JSONB | YES | '[]' | Prediction factors |
| `model_version` | VARCHAR(50) | NO | - | Model version used |
| `model_type` | VARCHAR(30) | YES | "ensemble" | xgboost/lightgbm/lstm/ensemble |
| `created_at` | TIMESTAMP | NO | NOW() | Prediction creation time |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`player_id`, `game_date`, `model_version`)
- INDEX (`game_date`)
- INDEX (`model_version`)

---

### `prediction_accuracy`

Model performance tracking.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `prediction_id` | UUID | NO | - | FK to player_predictions |
| `player_id` | INTEGER | NO | - | FK to players |
| `game_date` | DATE | NO | - | Game date |
| `category` | VARCHAR(20) | NO | - | points/rebounds/assists/etc |
| `predicted_value` | DECIMAL(8,4) | NO | - | Predicted value |
| `actual_value` | DECIMAL(8,4) | NO | - | Actual value |
| `error` | DECIMAL(8,4) | NO | - | prediction - actual |
| `absolute_error` | DECIMAL(8,4) | NO | - | |prediction - actual| |
| `percentage_error` | DECIMAL(8,4) | YES | NULL | % error |
| `within_range` | BOOLEAN | NO | - | Within predicted range |
| `model_version` | VARCHAR(50) | NO | - | Model version |
| `created_at` | TIMESTAMP | NO | NOW() | Record creation time |

**Indexes:**
- PRIMARY KEY (`id`)
- INDEX (`prediction_id`)
- INDEX (`game_date`, `category`)
- INDEX (`model_version`)

---

### `ml_features`

Feature store for ML pipeline.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `player_id` | INTEGER | NO | - | FK to players |
| `feature_date` | DATE | NO | - | Feature calculation date |
| `feature_name` | VARCHAR(100) | NO | - | Feature identifier |
| `feature_value` | DECIMAL(12,6) | NO | - | Feature value |
| `feature_type` | VARCHAR(30) | NO | - | numeric/categorical/temporal |
| `version` | INTEGER | NO | 1 | Feature version |
| `created_at` | TIMESTAMP | NO | NOW() | Record creation time |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`player_id`, `feature_date`, `feature_name`, `version`)
- INDEX (`feature_date`)
- INDEX (`feature_name`)

---

### `ml_models`

Model registry.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `name` | VARCHAR(100) | NO | - | Model name |
| `version` | VARCHAR(50) | NO | - | Model version |
| `model_type` | VARCHAR(30) | NO | - | xgboost/lightgbm/lstm/ensemble |
| `category` | VARCHAR(20) | YES | NULL | Prediction category |
| `artifact_path` | VARCHAR(500) | NO | - | Model file path |
| `metrics` | JSONB | YES | '{}' | Performance metrics |
| `parameters` | JSONB | YES | '{}' | Model parameters |
| `training_data_start` | DATE | YES | NULL | Training data start |
| `training_data_end` | DATE | YES | NULL | Training data end |
| `is_active` | BOOLEAN | NO | false | Currently deployed |
| `deployed_at` | TIMESTAMP | YES | NULL | Deployment time |
| `created_at` | TIMESTAMP | NO | NOW() | Record creation time |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`name`, `version`)
- INDEX (`model_type`, `is_active`)

---

## System Tables

### `audit_log`

System audit trail.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `user_id` | UUID | YES | NULL | Acting user |
| `action` | VARCHAR(50) | NO | - | Action performed |
| `resource_type` | VARCHAR(50) | NO | - | Affected resource type |
| `resource_id` | VARCHAR(100) | YES | NULL | Affected resource ID |
| `old_values` | JSONB | YES | NULL | Previous values |
| `new_values` | JSONB | YES | NULL | New values |
| `ip_address` | INET | YES | NULL | Client IP |
| `user_agent` | TEXT | YES | NULL | Client user agent |
| `created_at` | TIMESTAMP | NO | NOW() | Event time |

**Indexes:**
- PRIMARY KEY (`id`)
- INDEX (`user_id`)
- INDEX (`resource_type`, `resource_id`)
- INDEX (`created_at`)

---

### `background_jobs`

Celery job tracking.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `task_id` | VARCHAR(100) | NO | - | Celery task ID |
| `task_name` | VARCHAR(200) | NO | - | Task function name |
| `queue` | VARCHAR(50) | NO | "default" | Task queue |
| `status` | VARCHAR(20) | NO | "pending" | pending/running/success/failed |
| `args` | JSONB | YES | '[]' | Task arguments |
| `kwargs` | JSONB | YES | '{}' | Task keyword arguments |
| `result` | JSONB | YES | NULL | Task result |
| `error` | TEXT | YES | NULL | Error message |
| `retries` | INTEGER | NO | 0 | Retry count |
| `started_at` | TIMESTAMP | YES | NULL | Start time |
| `completed_at` | TIMESTAMP | YES | NULL | Completion time |
| `created_at` | TIMESTAMP | NO | NOW() | Job creation time |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`task_id`)
- INDEX (`status`)
- INDEX (`task_name`)
- INDEX (`created_at`)

---

### `cache_entries`

Application cache (backup to Redis).

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `key` | VARCHAR(255) | NO | - | Cache key |
| `value` | JSONB | NO | - | Cached value |
| `expires_at` | TIMESTAMP | YES | NULL | Expiration time |
| `created_at` | TIMESTAMP | NO | NOW() | Entry creation time |
| `updated_at` | TIMESTAMP | NO | NOW() | Last update time |

**Indexes:**
- PRIMARY KEY (`key`)
- INDEX (`expires_at`)

---

## Relationships

### Entity Relationship Diagram

```
users ─────────────┬──────────────┬────────────────┬────────────────┐
    │              │              │                │                │
    │              │              │                │                │
    ▼              ▼              ▼                ▼                ▼
refresh_tokens  user_sessions  yahoo_tokens  yahoo_leagues ─────┐  audit_log
                                                   │             │
                                                   │             │
                                                   ▼             │
                                              user_teams ────────┤
                                                   │             │
                                    ┌──────────────┼─────────────┤
                                    │              │             │
                                    ▼              ▼             ▼
                              team_rosters    matchups    recommendations
                                    │                           │
                                    │                           │
                                    ▼                           ▼
                               players ◄────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
           player_game_stats  player_season_stats  player_injuries
                    │
                    │
                    ▼
           player_predictions ───────► prediction_accuracy
                    │
                    │
                    ▼
               ml_features ◄─────────── ml_models

nba_teams ◄──────────────────────────── players
```

### Foreign Key Reference

| Table | Column | References |
|-------|--------|------------|
| players | team_id | nba_teams.id |
| player_game_stats | player_id | players.id |
| player_game_stats | team_id | nba_teams.id |
| player_game_stats | opponent_team_id | nba_teams.id |
| player_season_stats | player_id | players.id |
| player_season_stats | team_id | nba_teams.id |
| player_injuries | player_id | players.id |
| refresh_tokens | user_id | users.id |
| user_sessions | user_id | users.id |
| yahoo_tokens | user_id | users.id |
| yahoo_leagues | user_id | users.id |
| user_teams | user_id | users.id |
| user_teams | league_id | yahoo_leagues.id |
| team_rosters | team_id | user_teams.id |
| team_rosters | player_id | players.id |
| matchups | league_id | yahoo_leagues.id |
| matchups | team_id | user_teams.id |
| matchups | opponent_team_id | user_teams.id |
| recommendations | team_id | user_teams.id |
| recommendations | player_id | players.id |
| recommendations | secondary_player_id | players.id |
| waiver_claims | team_id | user_teams.id |
| waiver_claims | add_player_id | players.id |
| waiver_claims | drop_player_id | players.id |
| player_predictions | player_id | players.id |
| player_predictions | opponent_team_id | nba_teams.id |
| prediction_accuracy | prediction_id | player_predictions.id |
| prediction_accuracy | player_id | players.id |
| ml_features | player_id | players.id |
| audit_log | user_id | users.id |

---

## Data Types Reference

### PostgreSQL Type Mappings

| Application Type | PostgreSQL Type | Notes |
|------------------|-----------------|-------|
| UUID | UUID | gen_random_uuid() |
| String (short) | VARCHAR(n) | n = max length |
| String (long) | TEXT | Unlimited |
| Integer | INTEGER | 4 bytes |
| Big Integer | BIGINT | 8 bytes |
| Decimal | DECIMAL(p,s) | Exact numeric |
| Boolean | BOOLEAN | true/false |
| Date | DATE | YYYY-MM-DD |
| Timestamp | TIMESTAMP | Without timezone |
| Timestamp TZ | TIMESTAMPTZ | With timezone |
| JSON | JSONB | Binary JSON |
| Array | TYPE[] | Array of type |
| IP Address | INET | IPv4/IPv6 |

### Default Value Functions

| Function | Description |
|----------|-------------|
| `gen_random_uuid()` | Generate UUID v4 |
| `NOW()` | Current timestamp |
| `CURRENT_DATE` | Current date |
| `'{}'::jsonb` | Empty JSON object |
| `'[]'::jsonb` | Empty JSON array |

---

## Enumerations

### Player Positions

```sql
-- Primary positions
'PG'  -- Point Guard
'SG'  -- Shooting Guard
'SF'  -- Small Forward
'PF'  -- Power Forward
'C'   -- Center

-- Composite positions
'G'   -- Guard (PG/SG)
'F'   -- Forward (SF/PF)
'UTIL'-- Utility (any)
```

### Roster Positions

```sql
'PG'   -- Point Guard starter
'SG'   -- Shooting Guard starter
'SF'   -- Small Forward starter
'PF'   -- Power Forward starter
'C'    -- Center starter
'G'    -- Guard flex
'F'    -- Forward flex
'UTIL' -- Utility flex
'BN'   -- Bench
'IL'   -- Injured List
'IL+'  -- Extended IL
```

### Injury Status

```sql
'HEALTHY'     -- No injury
'QUESTIONABLE'-- Uncertain
'DOUBTFUL'    -- Unlikely to play
'OUT'         -- Will not play
'GTD'         -- Game Time Decision
```

### Recommendation Types

```sql
'start_sit'   -- Start or sit decision
'waiver_add'  -- Add from waivers
'waiver_drop' -- Drop candidate
'trade'       -- Trade suggestion
'matchup_strategy' -- Weekly strategy
```

### Job Status

```sql
'pending'  -- Waiting to run
'running'  -- Currently executing
'success'  -- Completed successfully
'failed'   -- Completed with error
'retrying' -- Retry scheduled
```

---

## ML Feature Engineering

Bu bölüm, tahmin modellerinde kullanılan özelliklerin (features) nasıl hesaplandığını açıklar.

### Feature Kategorileri

| Kategori | Açıklama | Örnek Features |
|----------|----------|----------------|
| **Player** | Oyuncu bazlı istatistikler | avg_fp_last_5, usage_rate |
| **Opponent** | Rakip savunma metrikleri | opp_def_rating, opp_vs_position |
| **Situational** | Maç durumu özellikleri | is_home, rest_days, is_b2b |
| **Team** | Takım dinamikleri | team_pace, teammate_injuries |
| **Temporal** | Zaman bazlı özellikler | day_of_week, season_day |

---

### Player Features

| Feature | Kaynak Tablo | Hesaplama | Açıklama |
|---------|--------------|-----------|----------|
| `avg_fp_last_5` | player_game_stats | `AVG(fantasy_points) WHERE last 5 games` | Son 5 maç FP ortalaması |
| `avg_fp_last_10` | player_game_stats | `AVG(fantasy_points) WHERE last 10 games` | Son 10 maç FP ortalaması |
| `avg_fp_season` | player_season_stats | `fantasy_ppg` | Sezon FP ortalaması |
| `fp_trend` | player_game_stats | `game_1.fp - game_5.fp` | FP trendi (yükseliş/düşüş) |
| `fp_std_dev` | player_game_stats | `STDDEV(fantasy_points) last 10` | FP tutarlılığı |
| `avg_minutes_last_5` | player_game_stats | `AVG(minutes) WHERE last 5 games` | Son 5 maç dakika ortalaması |
| `minutes_trend` | player_game_stats | `game_1.min - game_5.min` | Dakika trendi |
| `usage_rate` | player_season_stats | `usage_rate` | Kullanım oranı |
| `avg_points` | player_game_stats | `AVG(points) WHERE last 5 games` | Son 5 maç sayı ortalaması |
| `avg_rebounds` | player_game_stats | `AVG(rebounds) WHERE last 5 games` | Son 5 maç ribaund ortalaması |
| `avg_assists` | player_game_stats | `AVG(assists) WHERE last 5 games` | Son 5 maç asist ortalaması |
| `avg_steals` | player_game_stats | `AVG(steals) WHERE last 5 games` | Son 5 maç top çalma ortalaması |
| `avg_blocks` | player_game_stats | `AVG(blocks) WHERE last 5 games` | Son 5 maç blok ortalaması |
| `avg_turnovers` | player_game_stats | `AVG(turnovers) WHERE last 5 games` | Son 5 maç top kaybı ortalaması |
| `avg_threes` | player_game_stats | `AVG(fg3m) WHERE last 5 games` | Son 5 maç 3'lük ortalaması |
| `fg_pct_last_5` | player_game_stats | `AVG(fg_pct) WHERE last 5 games` | Son 5 maç şut yüzdesi |
| `injury_history_score` | player_injuries | `COUNT(*) * severity_weight` | Sakatlık risk skoru |

**Hesaplama Örneği:**

```sql
-- avg_fp_last_5 hesaplama
SELECT
    player_id,
    AVG(fantasy_points) as avg_fp_last_5
FROM (
    SELECT player_id, fantasy_points
    FROM player_game_stats
    WHERE player_id = :player_id
    ORDER BY game_date DESC
    LIMIT 5
) subq
GROUP BY player_id;
```

---

### Opponent Features

Bu özellikler için ek tablolar gerekiyor:

#### `team_defense_stats` (YENİ TABLO)

Takım savunma istatistikleri.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `team_id` | INTEGER | NO | - | FK to nba_teams |
| `season` | VARCHAR(10) | NO | - | Season (e.g., "2024-25") |
| `games_played` | INTEGER | NO | 0 | Games played |
| `def_rating` | DECIMAL(5,2) | YES | NULL | Defensive rating |
| `opp_points_pg` | DECIMAL(5,2) | YES | NULL | Opponent PPG allowed |
| `opp_rebounds_pg` | DECIMAL(5,2) | YES | NULL | Opponent RPG allowed |
| `opp_assists_pg` | DECIMAL(5,2) | YES | NULL | Opponent APG allowed |
| `opp_steals_pg` | DECIMAL(5,2) | YES | NULL | Opponent SPG allowed |
| `opp_blocks_pg` | DECIMAL(5,2) | YES | NULL | Opponent BPG allowed |
| `opp_turnovers_pg` | DECIMAL(5,2) | YES | NULL | Opponent TOPG forced |
| `opp_fg_pct` | DECIMAL(5,3) | YES | NULL | Opponent FG% allowed |
| `opp_fg3_pct` | DECIMAL(5,3) | YES | NULL | Opponent 3P% allowed |
| `opp_ft_pct` | DECIMAL(5,3) | YES | NULL | Opponent FT% allowed |
| `opp_fantasy_pg` | DECIMAL(6,2) | YES | NULL | Opponent FP allowed per game |
| `pace` | DECIMAL(5,2) | YES | NULL | Team pace (possessions/game) |
| `def_rank` | INTEGER | YES | NULL | Defensive ranking (1-30) |
| `last_calculated_at` | TIMESTAMP | YES | NULL | Last calculation time |
| `created_at` | TIMESTAMP | NO | NOW() | Record creation time |
| `updated_at` | TIMESTAMP | NO | NOW() | Last update time |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`team_id`, `season`)
- INDEX (`season`)

---

#### `defense_vs_position` (YENİ TABLO)

Pozisyona karşı savunma performansı.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `team_id` | INTEGER | NO | - | FK to nba_teams |
| `season` | VARCHAR(10) | NO | - | Season |
| `position` | VARCHAR(5) | NO | - | PG/SG/SF/PF/C |
| `games_played` | INTEGER | NO | 0 | Sample size |
| `avg_points_allowed` | DECIMAL(5,2) | YES | NULL | PPG allowed to position |
| `avg_rebounds_allowed` | DECIMAL(5,2) | YES | NULL | RPG allowed to position |
| `avg_assists_allowed` | DECIMAL(5,2) | YES | NULL | APG allowed to position |
| `avg_steals_allowed` | DECIMAL(5,2) | YES | NULL | SPG allowed to position |
| `avg_blocks_allowed` | DECIMAL(5,2) | YES | NULL | BPG allowed to position |
| `avg_turnovers_forced` | DECIMAL(5,2) | YES | NULL | TOPG forced vs position |
| `avg_threes_allowed` | DECIMAL(5,2) | YES | NULL | 3PM allowed to position |
| `avg_fantasy_allowed` | DECIMAL(6,2) | YES | NULL | FP allowed to position |
| `fantasy_rank` | INTEGER | YES | NULL | Rank vs position (1=hardest, 30=easiest) |
| `matchup_factor` | DECIMAL(4,3) | YES | 1.0 | Multiplier (0.8=hard, 1.2=easy) |
| `last_calculated_at` | TIMESTAMP | YES | NULL | Last calculation time |
| `created_at` | TIMESTAMP | NO | NOW() | Record creation time |
| `updated_at` | TIMESTAMP | NO | NOW() | Last update time |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`team_id`, `season`, `position`)
- INDEX (`season`, `position`)
- INDEX (`fantasy_rank`)

---

#### `nba_schedule` (YENİ TABLO)

NBA maç programı.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | gen_random_uuid() | Unique identifier |
| `game_id` | VARCHAR(20) | NO | - | NBA game ID |
| `season` | VARCHAR(10) | NO | - | Season |
| `game_date` | DATE | NO | - | Game date |
| `game_time` | TIME | YES | NULL | Game start time (ET) |
| `home_team_id` | INTEGER | NO | - | FK to nba_teams |
| `away_team_id` | INTEGER | NO | - | FK to nba_teams |
| `arena` | VARCHAR(100) | YES | NULL | Arena name |
| `is_national_tv` | BOOLEAN | NO | false | National TV game |
| `status` | VARCHAR(20) | NO | "scheduled" | scheduled/in_progress/final/postponed |
| `home_score` | INTEGER | YES | NULL | Home team final score |
| `away_score` | INTEGER | YES | NULL | Away team final score |
| `created_at` | TIMESTAMP | NO | NOW() | Record creation time |
| `updated_at` | TIMESTAMP | NO | NOW() | Last update time |

**Indexes:**
- PRIMARY KEY (`id`)
- UNIQUE (`game_id`)
- INDEX (`game_date`)
- INDEX (`home_team_id`)
- INDEX (`away_team_id`)
- INDEX (`season`)

---

### Opponent Feature Hesaplamaları

| Feature | Kaynak Tablo | Hesaplama | Açıklama |
|---------|--------------|-----------|----------|
| `opp_def_rating` | team_defense_stats | `def_rating WHERE team_id = opponent` | Rakip savunma rating'i |
| `opp_vs_position` | defense_vs_position | `matchup_factor WHERE team_id = opponent AND position = player.position` | Pozisyona karşı savunma |
| `opp_pace` | team_defense_stats | `pace WHERE team_id = opponent` | Rakip oyun temposu |
| `opp_fantasy_allowed` | defense_vs_position | `avg_fantasy_allowed` | Pozisyona verilen FP |
| `vs_opponent_avg` | player_game_stats | `AVG(fp) WHERE opponent = X` | Bu rakibe karşı ortalama |
| `opp_def_rank` | team_defense_stats | `def_rank` | Rakip savunma sıralaması |

**Hesaplama Örneği:**

```sql
-- matchup_factor hesaplama (opponent ne kadar kolay/zor?)
SELECT
    dvp.matchup_factor,
    dvp.fantasy_rank,
    dvp.avg_fantasy_allowed
FROM defense_vs_position dvp
WHERE dvp.team_id = :opponent_team_id
  AND dvp.season = :current_season
  AND dvp.position = :player_position;

-- matchup_factor yorumu:
-- 0.85 = Çok zor rakip (fantasy puanı %15 düşür)
-- 1.00 = Ortalama rakip
-- 1.15 = Çok kolay rakip (fantasy puanı %15 artır)
```

---

### Situational Features

| Feature | Kaynak | Hesaplama | Açıklama |
|---------|--------|-----------|----------|
| `is_home` | nba_schedule | `1 if home_team_id = player.team_id else 0` | Ev sahibi mi? |
| `rest_days` | player_game_stats + schedule | `game_date - last_game_date` | Son maçtan bu yana gün |
| `is_back_to_back` | nba_schedule | `1 if rest_days = 1 else 0` | Art arda maç mı? |
| `is_3_in_4` | nba_schedule | `1 if 3 games in 4 days else 0` | 4 günde 3 maç mı? |
| `days_since_injury` | player_injuries | `game_date - actual_return` | Sakatlıktan dönüş süresi |
| `games_since_return` | player_game_stats | `COUNT(*) since return` | Dönüşten beri maç sayısı |

**Hesaplama Örneği:**

```sql
-- rest_days hesaplama
SELECT
    :game_date - MAX(game_date) as rest_days
FROM player_game_stats
WHERE player_id = :player_id
  AND game_date < :game_date;

-- is_back_to_back
SELECT
    CASE WHEN rest_days = 1 THEN 1 ELSE 0 END as is_back_to_back
FROM (above query);
```

---

### Team Features

| Feature | Kaynak | Hesaplama | Açıklama |
|---------|--------|-----------|----------|
| `team_pace` | team_defense_stats | `pace WHERE team_id = player.team_id` | Takım temposu |
| `teammate_injuries` | player_injuries | `COUNT(*) WHERE team AND is_active` | Takımdaki sakatlar |
| `team_win_pct_last_10` | nba_schedule | `SUM(wins) / 10.0` | Son 10 maç galibiyet % |
| `team_offensive_rating` | team_stats | `off_rating` | Hücum rating |
| `star_player_out` | player_injuries | `1 if usage_rate > 25 AND out` | Yıldız oyuncu sakat mı? |

**Hesaplama Örneği:**

```sql
-- teammate_injuries (daha fazla fırsat?)
SELECT
    COUNT(*) as injured_teammates,
    SUM(pss.usage_rate) as missing_usage
FROM player_injuries pi
JOIN player_season_stats pss ON pi.player_id = pss.player_id
WHERE pi.is_active = true
  AND pi.status IN ('OUT', 'DOUBTFUL')
  AND pss.team_id = :player_team_id
  AND pss.season = :current_season
  AND pi.player_id != :player_id;
```

---

### Temporal Features

| Feature | Kaynak | Hesaplama | Açıklama |
|---------|--------|-----------|----------|
| `day_of_week` | game_date | `EXTRACT(DOW FROM game_date)` | Haftanın günü (0-6) |
| `month` | game_date | `EXTRACT(MONTH FROM game_date)` | Ay |
| `season_day` | game_date | `game_date - season_start_date` | Sezonun kaçıncı günü |
| `is_weekend` | game_date | `1 if DOW in (0, 6) else 0` | Hafta sonu mu? |
| `is_primetime` | nba_schedule | `1 if game_time >= 19:30 else 0` | Prime time maç mı? |
| `games_this_week` | nba_schedule | `COUNT(*) this week` | Bu haftaki maç sayısı |

---

### Feature Importance (Örnek XGBoost Sonuçları)

| Rank | Feature | Importance | Kategori |
|------|---------|------------|----------|
| 1 | `avg_fp_last_5` | 0.142 | Player |
| 2 | `avg_minutes_last_5` | 0.118 | Player |
| 3 | `usage_rate` | 0.095 | Player |
| 4 | `opp_vs_position` | 0.087 | Opponent |
| 5 | `is_home` | 0.072 | Situational |
| 6 | `rest_days` | 0.068 | Situational |
| 7 | `avg_fp_season` | 0.064 | Player |
| 8 | `opp_pace` | 0.058 | Opponent |
| 9 | `teammate_injuries` | 0.052 | Team |
| 10 | `fp_trend` | 0.048 | Player |
| 11 | `is_back_to_back` | 0.045 | Situational |
| 12 | `opp_def_rating` | 0.041 | Opponent |
| ... | ... | ... | ... |

---

### Feature Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FEATURE PIPELINE                              │
│                                                                      │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │  Raw Data   │────▶│  Transform  │────▶│   Feature   │           │
│  │   Tables    │     │  & Compute  │     │    Store    │           │
│  └─────────────┘     └─────────────┘     └─────────────┘           │
│        │                   │                   │                    │
│        │                   │                   │                    │
│        ▼                   ▼                   ▼                    │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │player_game_ │     │  Aggregated │     │ ml_features │           │
│  │   stats     │     │  last 5/10  │     │   table     │           │
│  │             │     │   games     │     │             │           │
│  │team_defense_│     │  Opponent   │     │ Ready for   │           │
│  │   stats     │     │  matchup    │     │   Model     │           │
│  │             │     │   factors   │     │             │           │
│  │nba_schedule │     │ Situational │     │             │           │
│  └─────────────┘     │  features   │     └─────────────┘           │
│                      └─────────────┘                                │
│                                                                      │
│  Çalışma zamanı: Her gece 02:00 (günlük) + Maç öncesi (anlık)      │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Feature Güncelleme Sıklığı

| Feature Grubu | Güncelleme | Trigger |
|---------------|------------|---------|
| Player averages | Maç sonrası | Game completed |
| Opponent stats | Günlük | Nightly batch |
| Defense vs position | Günlük | Nightly batch |
| Rest days | Maç öncesi | On prediction request |
| Injury status | Saatlik | Hourly job |
| Schedule features | Haftalık | Monday batch |

---

## Data Retention

### Retention Policies

| Data Type | Retention | Archive Strategy |
|-----------|-----------|------------------|
| Game Stats | Forever | Partition by season |
| Predictions | 1 year | Archive to cold storage |
| Accuracy Metrics | 2 years | Aggregate older data |
| User Sessions | 30 days | Delete expired |
| Audit Logs | 1 year | Archive to S3 |
| Background Jobs | 90 days | Delete completed |
| Cache Entries | TTL-based | Auto-expire |

### Partitioning Strategy

```sql
-- Partition player_game_stats by season
CREATE TABLE player_game_stats (
    ...
) PARTITION BY LIST (season);

CREATE TABLE player_game_stats_2024_25
    PARTITION OF player_game_stats
    FOR VALUES IN ('2024-25');
```

---

**Questions?** See [TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md) for schema implementation details.
