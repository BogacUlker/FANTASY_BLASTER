# Technical Specification - Fantasy Basketball Analyzer

**Version:** 2.0
**Last Updated:** 2025-01-11
**Purpose:** Complete technical specification for AI-powered fantasy basketball platform

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Database Schema](#database-schema)
5. [API Design](#api-design)
6. [Machine Learning Pipeline](#machine-learning-pipeline)
7. [Real-Time Data Integration](#real-time-data-integration)
8. [Notification System](#notification-system)
9. [Security](#security)
10. [Performance & Scaling](#performance--scaling)
11. [Development Roadmap](#development-roadmap)

---

## System Overview

### Product Vision

Fantasy Basketball Analyzer is an AI-powered SaaS platform providing:

- **Real-time NBA Statistics**: Live game data, player stats, injury updates
- **ML-Powered Predictions**: XGBoost/LightGBM ensemble predictions with confidence intervals
- **Smart Recommendations**: Start/sit, waiver wire, trade analysis with explainability
- **Yahoo Integration**: Full league sync via OAuth 2.0
- **Multi-Format Support**: H2H Categories, Points Leagues, Roto, Dynasty/Keeper
- **Real-Time Alerts**: Push notifications, injury alerts, game-time decisions

### Key Differentiators

| Feature | Our Platform | Competitors |
|---------|--------------|-------------|
| ML Models | XGBoost Ensemble + LSTM | Rule-based / Simple regression |
| Real-time Data | WebSocket live updates | Polling (5-15 min delay) |
| Injury Integration | Live Twitter/ESPN feed | Manual updates |
| Prediction Transparency | Full explainability + confidence | Black box |
| Multi-format Support | All formats Day 1 | Limited |
| Mobile Experience | PWA + React Native | Web only |

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                   │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   Web App   │  │  Mobile App │  │     PWA     │  │  Admin UI   │   │
│  │  (Next.js)  │  │(React Native│  │             │  │             │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │
│         │                │                │                │           │
│         └────────────────┴────────────────┴────────────────┘           │
│                                   │                                     │
│                          HTTPS / WebSocket                              │
└───────────────────────────────────┼─────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────┐
│                           EDGE LAYER                                     │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Cloudflare / AWS CloudFront                   │   │
│  │                    (CDN + WAF + DDoS Protection)                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                   │                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    API Gateway (Kong / AWS)                      │   │
│  │          Rate Limiting | Auth | Request Routing                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────┼─────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────┐
│                         APPLICATION LAYER                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │   Auth API   │  │  Player API  │  │    ML API    │  │ WebSocket  │  │
│  │   Service    │  │   Service    │  │   Service    │  │   Server   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬─────┘  │
│         │                 │                 │                 │         │
│  ┌──────┴─────────────────┴─────────────────┴─────────────────┴──────┐  │
│  │                    FastAPI Application Core                        │  │
│  │         Middleware | Dependency Injection | Error Handling         │  │
│  └───────────────────────────────┬───────────────────────────────────┘  │
│                                  │                                       │
└──────────────────────────────────┼───────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼───────────────────────────────────────┐
│                          DATA LAYER                                       │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────────┐ │
│  │ PostgreSQL │  │   Redis    │  │   Kafka    │  │    S3 / MinIO      │ │
│  │  Primary   │  │   Cache    │  │   Queue    │  │   Model Storage    │ │
│  │  Database  │  │  + Pub/Sub │  │            │  │                    │ │
│  └────────────┘  └────────────┘  └────────────┘  └────────────────────┘ │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼───────────────────────────────────────┐
│                       BACKGROUND PROCESSING                               │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────────┐ │
│  │ Celery Workers │  │  Celery Beat   │  │     ML Training Pipeline   │ │
│  │                │  │  (Scheduler)   │  │     (Airflow / Prefect)    │ │
│  │ • Data Ingest  │  │                │  │                            │ │
│  │ • Predictions  │  │ • Hourly stats │  │ • Daily model retraining   │ │
│  │ • Yahoo Sync   │  │ • Daily models │  │ • Feature engineering      │ │
│  │ • Alerts       │  │ • Weekly reports│ │ • Model evaluation         │ │
│  └────────────────┘  └────────────────┘  └────────────────────────────┘ │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼───────────────────────────────────────┐
│                        EXTERNAL INTEGRATIONS                              │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────────┐ │
│  │  NBA API   │  │ Yahoo API  │  │ Twitter/X  │  │  ESPN / BBRef      │ │
│  │  (Primary) │  │  (OAuth)   │  │  (Injuries)│  │  (Backup Data)     │ │
│  └────────────┘  └────────────┘  └────────────┘  └────────────────────┘ │
│                                                                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────────┐ │
│  │   Sentry   │  │  DataDog   │  │  SendGrid  │  │   Firebase FCM     │ │
│  │  (Errors)  │  │ (Metrics)  │  │  (Email)   │  │ (Push Notifications)│ │
│  └────────────┘  └────────────┘  └────────────┘  └────────────────────┘ │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

### Service Communication

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SERVICE COMMUNICATION PATTERNS                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Synchronous (REST)              Asynchronous (Event-Driven)        │
│   ─────────────────              ────────────────────────────        │
│                                                                      │
│   Client → API Gateway           Kafka Topics:                       │
│         → Auth Service           • player.stats.updated              │
│         → Player Service         • prediction.generated              │
│         → Response               • injury.reported                   │
│                                  • recommendation.ready              │
│                                  • yahoo.sync.completed              │
│                                                                      │
│   WebSocket (Real-time)          Redis Pub/Sub:                      │
│   ─────────────────────          ──────────────                      │
│                                                                      │
│   • Live game scores             • Cache invalidation                │
│   • Injury alerts                • Session updates                   │
│   • Prediction updates           • Rate limit sync                   │
│   • Roster changes                                                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | FastAPI | 0.109+ | Async REST API |
| **Language** | Python | 3.11+ | Backend logic |
| **ORM** | SQLAlchemy | 2.0+ | Database operations |
| **Database** | PostgreSQL | 15+ | Primary data store |
| **Cache** | Redis | 7+ | Caching, pub/sub, sessions |
| **Queue** | Celery + Redis | 5.3+ | Background jobs |
| **Message Broker** | Kafka | 3.6+ | Event streaming |
| **WebSocket** | FastAPI WebSocket | - | Real-time updates |
| **API Docs** | OpenAPI/Swagger | 3.1 | Auto-generated docs |

### Machine Learning

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Gradient Boosting** | XGBoost | 2.0+ | Primary prediction model |
| **Alternative GB** | LightGBM | 4.3+ | Fast inference, ensemble |
| **Deep Learning** | PyTorch | 2.1+ | LSTM for sequences |
| **ML Framework** | Scikit-learn | 1.4+ | Preprocessing, evaluation |
| **Feature Store** | Feast | 0.35+ | Feature management |
| **Model Registry** | MLflow | 2.10+ | Model versioning |
| **Orchestration** | Prefect | 2.14+ | ML pipeline automation |
| **Data Processing** | Pandas/Polars | - | Data manipulation |

### Frontend

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | Next.js | 14+ | React SSR/SSG |
| **Language** | TypeScript | 5.3+ | Type safety |
| **State Management** | React Query + Zustand | 5.x / 4.x | Server + client state |
| **Styling** | Tailwind CSS | 3.4+ | Utility-first CSS |
| **UI Components** | shadcn/ui | - | Accessible components |
| **Charts** | Recharts | 2.10+ | Data visualization |
| **WebSocket Client** | Socket.io-client | 4.6+ | Real-time connection |
| **Mobile** | React Native | 0.73+ | Native mobile apps |

### Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Container** | Docker | Containerization |
| **Orchestration** | Kubernetes / Railway | Container management |
| **CI/CD** | GitHub Actions | Automated pipelines |
| **Monitoring** | DataDog + Sentry | Metrics + Errors |
| **Logging** | ELK Stack / Loki | Centralized logs |
| **CDN** | Cloudflare | Edge caching, WAF |
| **Storage** | AWS S3 / MinIO | Object storage |

### External APIs

| Service | Purpose | Fallback |
|---------|---------|----------|
| **nba_api** | Primary NBA data | Basketball-Reference scraper |
| **ESPN API** | Backup stats + injuries | RSS feeds |
| **Yahoo Fantasy API** | League integration | Manual entry |
| **Twitter/X API** | Injury news | ESPN injury feed |
| **Sportradar** | Premium live data | nba_api polling |

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     users       │       │   yahoo_tokens  │       │  yahoo_leagues  │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK)         │──┐    │ id (PK)         │       │ id (PK)         │
│ email           │  │    │ user_id (FK)────│───────│ user_id (FK)────│───┐
│ username        │  │    │ access_token    │       │ yahoo_league_id │   │
│ password_hash   │  │    │ refresh_token   │       │ name            │   │
│ is_premium      │  │    │ expires_at      │       │ scoring_type    │   │
│ tier            │  │    └─────────────────┘       │ num_teams       │   │
│ created_at      │  │                              │ season          │   │
└─────────────────┘  │                              └─────────────────┘   │
                     │                                       │            │
                     │    ┌─────────────────┐                │            │
                     │    │   user_teams    │                │            │
                     │    ├─────────────────┤                │            │
                     └────│ user_id (FK)    │                │            │
                          │ league_id (FK)──│────────────────┘            │
                          │ yahoo_team_id   │                             │
                          │ team_name       │                             │
                          │ is_active       │                             │
                          └────────┬────────┘                             │
                                   │                                      │
┌─────────────────┐               │                                      │
│     teams       │               │    ┌─────────────────┐               │
├─────────────────┤               │    │  team_rosters   │               │
│ id (PK)         │               │    ├─────────────────┤               │
│ full_name       │               └────│ user_team_id(FK)│               │
│ abbreviation    │                    │ player_id (FK)──│───┐           │
│ city            │                    │ roster_position │   │           │
│ conference      │                    │ is_starter      │   │           │
│ division        │                    │ acquired_date   │   │           │
└────────┬────────┘                    └─────────────────┘   │           │
         │                                                    │           │
         │    ┌─────────────────┐                            │           │
         │    │    players      │                            │           │
         │    ├─────────────────┤                            │           │
         │    │ id (PK)         │◄───────────────────────────┘           │
         └────│ team_id (FK)    │                                        │
              │ full_name       │                                        │
              │ position        │    ┌─────────────────┐                 │
              │ jersey_number   │    │ player_injuries │                 │
              │ height          │    ├─────────────────┤                 │
              │ weight          │    │ id (PK)         │                 │
              │ is_active       │◄───│ player_id (FK)  │                 │
              │ injury_status   │    │ injury_type     │                 │
              └────────┬────────┘    │ status          │                 │
                       │             │ expected_return │                 │
                       │             │ source          │                 │
                       │             │ reported_at     │                 │
                       │             └─────────────────┘                 │
                       │                                                  │
         ┌─────────────┼─────────────┬────────────────┐                  │
         │             │             │                │                  │
         ▼             ▼             ▼                ▼                  │
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐     │
│player_game_ │ │player_season│ │player_pred  │ │ recommendations │     │
│   stats     │ │   _stats    │ │  ictions    │ ├─────────────────┤     │
├─────────────┤ ├─────────────┤ ├─────────────┤ │ id (PK)         │     │
│ id (PK)     │ │ id (PK)     │ │ id (PK)     │ │ user_team_id(FK)│◄────┘
│ player_id   │ │ player_id   │ │ player_id   │ │ type            │
│ game_id     │ │ season      │ │ game_date   │ │ player_id (FK)  │
│ game_date   │ │ games_played│ │ predictions │ │ action          │
│ minutes     │ │ minutes_pg  │ │ confidence  │ │ reasoning       │
│ points      │ │ points_pg   │ │ model_version│ │ confidence     │
│ rebounds    │ │ rebounds_pg │ │ factors     │ │ expected_value  │
│ assists     │ │ assists_pg  │ │ created_at  │ │ valid_until     │
│ steals      │ │ steals_pg   │ └─────────────┘ │ feedback        │
│ blocks      │ │ blocks_pg   │                 └─────────────────┘
│ turnovers   │ │ turnovers_pg│
│ fg_made     │ │ fg_pct      │   ┌─────────────────┐
│ fg_attempted│ │ ft_pct      │   │   matchups      │
│ fg3_made    │ │ fg3_pct     │   ├─────────────────┤
│ ft_made     │ │ z_score_total   │ id (PK)         │
│ plus_minus  │ │ rank        │   │ user_team_id(FK)│
└─────────────┘ └─────────────┘   │ opponent_team_id│
                                   │ week_number     │
┌─────────────────┐               │ win_probability │
│prediction_accuracy              │ projected_wins  │
├─────────────────┤               │ category_breakdown
│ id (PK)         │               │ created_at      │
│ prediction_id   │               └─────────────────┘
│ actual_values   │
│ error_metrics   │   ┌─────────────────┐
│ model_version   │   │ scoring_settings│
│ evaluated_at    │   ├─────────────────┤
└─────────────────┘   │ id (PK)         │
                      │ league_id (FK)  │
┌─────────────────┐   │ format          │ ← H2H_CATEGORIES, POINTS, ROTO
│ user_alerts     │   │ categories      │ ← JSONB
├─────────────────┤   │ point_values    │ ← JSONB (for points leagues)
│ id (PK)         │   │ roster_positions│
│ user_id (FK)    │   │ max_acquisitions│
│ type            │   └─────────────────┘
│ player_id (FK)  │
│ conditions      │   ┌─────────────────┐
│ channels        │   │ model_registry  │
│ is_active       │   ├─────────────────┤
│ last_triggered  │   │ id (PK)         │
└─────────────────┘   │ model_name      │
                      │ version         │
                      │ metrics         │
                      │ artifact_path   │
                      │ is_production   │
                      │ created_at      │
                      └─────────────────┘
```

### Core Tables SQL

```sql
-- Users table with tier support
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    tier VARCHAR(20) DEFAULT 'free' CHECK (tier IN ('free', 'pro', 'premium')),
    api_calls_today INTEGER DEFAULT 0,
    api_calls_reset_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Players table with injury status
CREATE TABLE players (
    id INTEGER PRIMARY KEY, -- NBA API player ID
    full_name VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    position VARCHAR(10),
    team_id INTEGER REFERENCES teams(id),
    team_abbreviation VARCHAR(10),
    jersey_number VARCHAR(10),
    height VARCHAR(10),
    weight VARCHAR(10),
    birth_date DATE,
    country VARCHAR(100),
    draft_year INTEGER,
    draft_round INTEGER,
    draft_number INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    injury_status VARCHAR(20) DEFAULT 'healthy', -- healthy, questionable, doubtful, out
    injury_detail TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Player game stats
CREATE TABLE player_game_stats (
    id BIGSERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES players(id),
    game_id VARCHAR(20) NOT NULL,
    game_date DATE NOT NULL,
    season VARCHAR(10) NOT NULL,
    opponent_team_id INTEGER REFERENCES teams(id),
    is_home BOOLEAN,

    -- Minutes
    minutes_played DECIMAL(5,2),

    -- Scoring
    points INTEGER,
    fgm INTEGER,
    fga INTEGER,
    fg_pct DECIMAL(5,3),
    fg3m INTEGER,
    fg3a INTEGER,
    fg3_pct DECIMAL(5,3),
    ftm INTEGER,
    fta INTEGER,
    ft_pct DECIMAL(5,3),

    -- Rebounds
    offensive_rebounds INTEGER,
    defensive_rebounds INTEGER,
    rebounds INTEGER,

    -- Other stats
    assists INTEGER,
    steals INTEGER,
    blocks INTEGER,
    turnovers INTEGER,
    personal_fouls INTEGER,
    plus_minus INTEGER,

    -- Fantasy points (calculated)
    fantasy_points_standard DECIMAL(6,2),
    fantasy_points_ppr DECIMAL(6,2),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(player_id, game_id)
);

-- Player predictions with confidence intervals
CREATE TABLE player_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id INTEGER NOT NULL REFERENCES players(id),
    game_date DATE NOT NULL,
    opponent_team_id INTEGER REFERENCES teams(id),
    is_home BOOLEAN,

    -- Predictions (JSONB for flexibility)
    predictions JSONB NOT NULL,
    /*
    {
        "minutes": {"value": 32.5, "low": 28.0, "high": 37.0, "z_score": 0.5},
        "points": {"value": 24.3, "low": 18.0, "high": 31.0, "z_score": 1.2},
        "rebounds": {"value": 7.1, "low": 4.0, "high": 10.0, "z_score": 0.8},
        "assists": {"value": 5.2, "low": 3.0, "high": 8.0, "z_score": 0.3},
        ...
    }
    */

    total_z_score DECIMAL(5,2),
    fantasy_points_projected DECIMAL(6,2),
    confidence DECIMAL(3,2), -- 0.00 to 1.00

    -- Model info
    model_name VARCHAR(100),
    model_version VARCHAR(50),

    -- Factors affecting prediction
    factors JSONB,
    /*
    [
        {"factor": "opponent_defense_rank", "impact": -0.3, "description": "Playing against #3 defense"},
        {"factor": "rest_days", "impact": 0.1, "description": "2 days rest"},
        {"factor": "recent_form", "impact": 0.2, "description": "Averaging 28 PPG last 5 games"}
    ]
    */

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(player_id, game_date, model_version)
);

-- Scoring settings for different league formats
CREATE TABLE scoring_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    league_id UUID REFERENCES yahoo_leagues(id),

    format VARCHAR(20) NOT NULL CHECK (format IN ('h2h_categories', 'h2h_points', 'roto', 'points')),

    -- For category leagues
    categories JSONB,
    /*
    ["points", "rebounds", "assists", "steals", "blocks", "fg_pct", "ft_pct", "fg3m", "turnovers"]
    */

    -- For points leagues
    point_values JSONB,
    /*
    {
        "points": 1,
        "rebounds": 1.2,
        "assists": 1.5,
        "steals": 3,
        "blocks": 3,
        "turnovers": -1,
        "fg_made": 0.5,
        "fg_missed": -0.5,
        "ft_made": 0.5,
        "ft_missed": -0.5,
        "fg3_made": 0.5,
        "double_double": 3,
        "triple_double": 5
    }
    */

    -- Roster settings
    roster_positions JSONB,
    /*
    {
        "PG": 1, "SG": 1, "SF": 1, "PF": 1, "C": 1,
        "G": 1, "F": 1, "UTIL": 2, "BN": 3, "IR": 2
    }
    */

    max_acquisitions INTEGER,
    max_trades INTEGER,
    trade_deadline DATE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Player injuries tracking
CREATE TABLE player_injuries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id INTEGER NOT NULL REFERENCES players(id),

    injury_type VARCHAR(100), -- ankle, knee, illness, rest, etc.
    status VARCHAR(20) NOT NULL, -- questionable, doubtful, out, day-to-day
    description TEXT,

    expected_return DATE,
    games_missed INTEGER DEFAULT 0,

    source VARCHAR(50), -- twitter, espn, yahoo, official
    source_url TEXT,

    reported_at TIMESTAMP WITH TIME ZONE NOT NULL,
    resolved_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User alerts configuration
CREATE TABLE user_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),

    alert_type VARCHAR(50) NOT NULL,
    -- injury_update, game_start, prediction_change, waiver_target, trade_suggestion

    player_id INTEGER REFERENCES players(id),
    team_id INTEGER REFERENCES teams(id),

    conditions JSONB,
    /*
    {
        "injury_status_change": true,
        "projection_change_pct": 15,
        "ownership_below": 50,
        "z_score_above": 2.0
    }
    */

    channels JSONB DEFAULT '["in_app"]',
    -- ["in_app", "email", "push", "sms"]

    is_active BOOLEAN DEFAULT TRUE,
    last_triggered_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Model registry for ML versioning
CREATE TABLE model_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,

    -- Model metadata
    algorithm VARCHAR(50), -- xgboost, lightgbm, ensemble, lstm
    features_used JSONB,
    hyperparameters JSONB,

    -- Performance metrics
    metrics JSONB,
    /*
    {
        "mae": 3.2,
        "rmse": 4.5,
        "r2": 0.82,
        "category_accuracies": {
            "points": 0.85,
            "rebounds": 0.78,
            ...
        }
    }
    */

    -- Artifact location
    artifact_path TEXT NOT NULL,

    -- Status
    is_production BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,

    -- Timestamps
    training_started_at TIMESTAMP WITH TIME ZONE,
    training_completed_at TIMESTAMP WITH TIME ZONE,
    promoted_to_production_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_players_team ON players(team_id);
CREATE INDEX idx_players_position ON players(position);
CREATE INDEX idx_players_active ON players(is_active);
CREATE INDEX idx_players_injury ON players(injury_status);

CREATE INDEX idx_game_stats_player ON player_game_stats(player_id);
CREATE INDEX idx_game_stats_date ON player_game_stats(game_date);
CREATE INDEX idx_game_stats_season ON player_game_stats(season);
CREATE INDEX idx_game_stats_player_date ON player_game_stats(player_id, game_date);

CREATE INDEX idx_predictions_player ON player_predictions(player_id);
CREATE INDEX idx_predictions_date ON player_predictions(game_date);
CREATE INDEX idx_predictions_player_date ON player_predictions(player_id, game_date);

CREATE INDEX idx_injuries_player ON player_injuries(player_id);
CREATE INDEX idx_injuries_status ON player_injuries(status);
CREATE INDEX idx_injuries_active ON player_injuries(resolved_at) WHERE resolved_at IS NULL;

CREATE INDEX idx_alerts_user ON user_alerts(user_id);
CREATE INDEX idx_alerts_active ON user_alerts(is_active) WHERE is_active = TRUE;

-- Partial indexes for performance
CREATE INDEX idx_active_players ON players(id) WHERE is_active = TRUE;
CREATE INDEX idx_recent_predictions ON player_predictions(game_date)
    WHERE game_date >= CURRENT_DATE - INTERVAL '7 days';
```

---

## API Design

### API Versioning Strategy

```
/api/v1/... → Current stable version
/api/v2/... → New features, breaking changes
/api/beta/... → Experimental features

Deprecation Policy:
- 6 months notice before version sunset
- X-API-Deprecation header on deprecated endpoints
- Migration guide provided
```

### Authentication Endpoints

```yaml
# POST /api/v1/auth/register
Request:
  email: string (required, valid email)
  username: string (required, 3-50 chars, alphanumeric)
  password: string (required, min 8 chars, complexity rules)

Response 201:
  user_id: string
  message: "User created successfully. Please verify your email."

# POST /api/v1/auth/login
Request:
  email: string (required)
  password: string (required)
  remember_me: boolean (optional, extends token expiry)

Response 200:
  access_token: string
  refresh_token: string
  token_type: "Bearer"
  expires_in: number (seconds)
  user:
    id: string
    email: string
    username: string
    tier: string

# POST /api/v1/auth/refresh
Headers:
  Authorization: Bearer {refresh_token}

Response 200:
  access_token: string
  expires_in: number

# POST /api/v1/auth/logout
Headers:
  Authorization: Bearer {access_token}

Response 200:
  message: "Successfully logged out"

# POST /api/v1/auth/revoke-all
Description: Revoke all tokens for the user (all devices)
Response 200:
  message: "All sessions revoked"
```

### Player Endpoints

```yaml
# GET /api/v1/players
Query Parameters:
  name: string (optional, search by name)
  position: string (optional, PG|SG|SF|PF|C)
  team: string (optional, team abbreviation)
  injury_status: string (optional, healthy|questionable|doubtful|out)
  is_active: boolean (optional, default true)
  min_games: number (optional, minimum games played)
  sort_by: string (optional, name|points_pg|z_score)
  sort_order: string (optional, asc|desc)
  limit: number (optional, default 20, max 100)
  offset: number (optional, default 0)

Response 200:
  players: Player[]
  total: number
  limit: number
  offset: number

# GET /api/v1/players/{player_id}
Response 200:
  id: number
  full_name: string
  position: string
  team:
    id: number
    name: string
    abbreviation: string
  injury_status: string
  injury_detail: string | null
  current_season_stats:
    games_played: number
    points_pg: number
    rebounds_pg: number
    assists_pg: number
    ...
  z_scores:
    total: number
    by_category: object
  next_game:
    date: string
    opponent: string
    is_home: boolean

# GET /api/v1/players/{player_id}/stats
Query Parameters:
  season: string (optional, default current, e.g., "2024-25")
  stat_type: string (optional, per_game|totals|per_36)

Response 200:
  player_id: number
  season: string
  stat_type: string
  stats:
    games_played: number
    minutes_pg: number
    points_pg: number
    ...

# GET /api/v1/players/{player_id}/game-log
Query Parameters:
  season: string (optional)
  last_n: number (optional, last N games)
  opponent: string (optional, filter by opponent)
  home_away: string (optional, home|away|all)
  limit: number (optional, default 10)

Response 200:
  player_id: number
  games: GameLog[]

# GET /api/v1/players/{player_id}/splits
Query Parameters:
  season: string (optional)
  split_type: string (required, home_away|monthly|vs_team|last_n)

Response 200:
  splits:
    - split_name: string
      games: number
      stats: object

# GET /api/v1/players/trending
Query Parameters:
  timeframe: string (optional, 7d|14d|30d)
  category: string (optional, points|rebounds|assists|all)
  direction: string (optional, up|down)
  limit: number (optional, default 20)

Response 200:
  trending_players:
    - player: Player
      trend_direction: string
      trend_magnitude: number
      comparison:
        recent_avg: number
        season_avg: number
        pct_change: number

# GET /api/v1/players/compare
Query Parameters:
  player_ids: string (required, comma-separated IDs)
  categories: string (optional, comma-separated categories)
  timeframe: string (optional, season|last30|last14|last7)

Response 200:
  comparison:
    - player_id: number
      player_name: string
      stats: object
      z_scores: object
      rank: number
```

### Predictions Endpoints

```yaml
# GET /api/v1/predictions/player/{player_id}
Query Parameters:
  game_date: string (optional, default next game)
  include_factors: boolean (optional, default true)

Response 200:
  player_id: number
  player_name: string
  game_date: string
  opponent:
    team_id: number
    team_name: string
    abbreviation: string
    defense_rank: number
  is_home: boolean
  predictions:
    minutes:
      value: number
      low: number
      high: number
      z_score: number
    points:
      value: number
      low: number
      high: number
      z_score: number
    ...
  total_z_score: number
  fantasy_points_projected: number
  confidence: number
  model_info:
    name: string
    version: string
  factors:
    - factor: string
      impact: number
      description: string
  uncertainty_note: string | null

# GET /api/v1/predictions/daily
Query Parameters:
  date: string (optional, default today)
  min_confidence: number (optional, 0-1)
  position: string (optional)
  sort_by: string (optional, z_score|fantasy_points|confidence)

Response 200:
  date: string
  games_count: number
  predictions:
    - player: Player
      prediction: PredictionDetail
      game_info: GameInfo

# GET /api/v1/predictions/batch
Request Body:
  player_ids: number[]
  game_date: string (optional)

Response 200:
  predictions: PlayerPrediction[]

# GET /api/v1/predictions/accuracy
Query Parameters:
  start_date: string (required)
  end_date: string (required)
  player_id: number (optional)
  category: string (optional)

Response 200:
  period:
    start_date: string
    end_date: string
  overall_metrics:
    mae: number
    rmse: number
    r2: number
    predictions_count: number
  category_breakdown:
    points:
      mae: number
      accuracy_within_10pct: number
    ...
  confidence_calibration:
    - confidence_bucket: string
      actual_accuracy: number
      prediction_count: number
```

### Rankings Endpoints

```yaml
# GET /api/v1/rankings/players
Query Parameters:
  format: string (required, h2h_categories|points|roto)
  timeframe: string (optional, ros|last30|last14)
  position: string (optional)
  punting: string (optional, comma-separated categories to punt)
  limit: number (optional, default 100)

Response 200:
  rankings:
    - rank: number
      player: Player
      z_score_total: number
      z_scores_by_category: object
      trend: string (up|down|stable)
      ros_projection: number

# POST /api/v1/rankings/custom
Request Body:
  scoring_settings:
    format: string
    categories: string[] | null
    point_values: object | null
  filters:
    position: string | null
    min_games: number | null
    teams: string[] | null
  weights:
    points: number
    rebounds: number
    ...

Response 200:
  custom_rankings: RankedPlayer[]
  settings_hash: string (for caching)

# GET /api/v1/rankings/ros-projections
Query Parameters:
  format: string (required)
  position: string (optional)
  include_rookies: boolean (optional)

Response 200:
  projections:
    - player: Player
      games_remaining: number
      projected_stats: object
      projected_z_score: number
      upside_score: number
      consistency_score: number
```

### Recommendations Endpoints

```yaml
# GET /api/v1/recommendations/{team_id}
Query Parameters:
  type: string (optional, all|start_sit|waiver|trade|streaming)
  game_date: string (optional)
  limit: number (optional)

Response 200:
  team_id: string
  generated_at: string
  recommendations:
    - id: string
      type: string
      priority: string (high|medium|low)
      action: string
      player: Player
      over_player: Player | null
      reasoning: string
      confidence: number
      expected_value: number
      valid_until: string
      supporting_data:
        matchup_info: object | null
        recent_performance: object | null

# GET /api/v1/recommendations/{team_id}/start-sit
Query Parameters:
  game_date: string (optional, default today)
  position: string (optional)

Response 200:
  date: string
  roster_decisions:
    starters:
      - player: Player
        reasoning: string
        confidence: number
    bench:
      - player: Player
        reasoning: string
        confidence: number
    must_start:
      - player: Player
        reasoning: string
    borderline:
      - player: Player
        start_confidence: number
        sit_confidence: number

# GET /api/v1/recommendations/{team_id}/waiver
Query Parameters:
  available_only: boolean (optional, default true)
  max_ownership: number (optional, default 50)
  position: string (optional)

Response 200:
  waiver_targets:
    - player: Player
      ownership_pct: number
      ros_z_score: number
      trending: string
      reasoning: string
      drop_candidates:
        - player: Player
          impact_analysis: string

# POST /api/v1/recommendations/{team_id}/trade-analyzer
Request Body:
  giving:
    - player_id: number
  receiving:
    - player_id: number

Response 200:
  trade_analysis:
    fairness_score: number (-100 to +100)
    winner: string (you|them|fair)
    giving_value:
      total_z_score: number
      ros_projection: number
    receiving_value:
      total_z_score: number
      ros_projection: number
    category_impact:
      - category: string
        current: number
        after_trade: number
        change: number
    recommendation: string
    warnings: string[]

# POST /api/v1/recommendations/{team_id}/feedback
Request Body:
  recommendation_id: string
  action_taken: string (followed|ignored|modified)
  outcome: string | null (success|failure|neutral)
  was_helpful: boolean
  comments: string | null

Response 200:
  message: "Feedback recorded"
```

### WebSocket Endpoints

```yaml
# WebSocket /ws/live
Authentication: Bearer token as query param or first message

Events (Server → Client):
  - type: "game_update"
    data:
      game_id: string
      status: string
      scores: object
      player_stats: object[]

  - type: "injury_alert"
    data:
      player_id: number
      player_name: string
      status: string
      description: string
      source: string

  - type: "prediction_update"
    data:
      player_id: number
      game_date: string
      old_prediction: object
      new_prediction: object
      reason: string

  - type: "recommendation_ready"
    data:
      team_id: string
      recommendation_type: string
      preview: string

Subscriptions (Client → Server):
  - action: "subscribe"
    channels: string[]
    # ["games:live", "injuries:all", "predictions:player:{id}", "team:{team_id}"]

  - action: "unsubscribe"
    channels: string[]
```

### Alert Endpoints

```yaml
# GET /api/v1/alerts
Query Parameters:
  is_active: boolean (optional)

Response 200:
  alerts: UserAlert[]

# POST /api/v1/alerts
Request Body:
  alert_type: string (required)
  player_id: number | null
  team_id: number | null
  conditions: object
  channels: string[]

Response 201:
  alert: UserAlert

# PUT /api/v1/alerts/{alert_id}
Request Body:
  conditions: object | null
  channels: string[] | null
  is_active: boolean | null

Response 200:
  alert: UserAlert

# DELETE /api/v1/alerts/{alert_id}
Response 204
```

### Error Response Format

```yaml
Error Response:
  error:
    code: string
    message: string
    details: object | null
    request_id: string
    timestamp: string
    documentation_url: string | null

HTTP Status Codes:
  200: Success
  201: Created
  204: No Content
  400: Bad Request (validation error)
  401: Unauthorized (invalid/expired token)
  403: Forbidden (insufficient permissions/tier)
  404: Not Found
  409: Conflict (duplicate resource)
  422: Unprocessable Entity (business logic error)
  429: Too Many Requests (rate limited)
  500: Internal Server Error
  503: Service Unavailable (maintenance)
```

### Rate Limiting

```yaml
Rate Limits by Tier:
  Free:
    requests_per_minute: 30
    requests_per_hour: 500
    requests_per_day: 5000
    websocket_connections: 1

  Pro:
    requests_per_minute: 100
    requests_per_hour: 3000
    requests_per_day: 30000
    websocket_connections: 3

  Premium:
    requests_per_minute: 300
    requests_per_hour: 10000
    requests_per_day: 100000
    websocket_connections: 10

Rate Limit Headers:
  X-RateLimit-Limit: number
  X-RateLimit-Remaining: number
  X-RateLimit-Reset: timestamp

Exceeded Response (429):
  error:
    code: "RATE_LIMIT_EXCEEDED"
    message: "Rate limit exceeded. Please upgrade your plan or try again later."
    retry_after: number (seconds)
```

---

## Machine Learning Pipeline

### ML Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ML PIPELINE ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                     DATA COLLECTION LAYER                           │ │
│  ├────────────────────────────────────────────────────────────────────┤ │
│  │                                                                     │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │ │
│  │  │   NBA API    │  │  ESPN Feed   │  │  Historical DB Backup    │ │ │
│  │  │  (Primary)   │  │  (Backup)    │  │  (Basketball-Reference)  │ │ │
│  │  └──────┬───────┘  └──────┬───────┘  └────────────┬─────────────┘ │ │
│  │         │                 │                       │                │ │
│  │         └─────────────────┴───────────────────────┘                │ │
│  │                           │                                         │ │
│  │                           ▼                                         │ │
│  │                  ┌─────────────────┐                               │ │
│  │                  │   Data Lake     │                               │ │
│  │                  │   (S3/MinIO)    │                               │ │
│  │                  └────────┬────────┘                               │ │
│  └───────────────────────────┼────────────────────────────────────────┘ │
│                              │                                           │
│  ┌───────────────────────────▼────────────────────────────────────────┐ │
│  │                    FEATURE ENGINEERING LAYER                        │ │
│  ├────────────────────────────────────────────────────────────────────┤ │
│  │                                                                     │ │
│  │  ┌───────────────────────────────────────────────────────────────┐ │ │
│  │  │                    Feature Store (Feast)                       │ │ │
│  │  ├───────────────────────────────────────────────────────────────┤ │ │
│  │  │                                                                │ │ │
│  │  │  Player Features:                                              │ │ │
│  │  │  • Rolling averages (3, 5, 10, 20 games)                      │ │ │
│  │  │  • Trend indicators (improving/declining)                     │ │ │
│  │  │  • Minutes trend and usage rate                               │ │ │
│  │  │  • Home/Away splits                                           │ │ │
│  │  │  • Back-to-back performance                                   │ │ │
│  │  │  • Rest days impact                                           │ │ │
│  │  │  • Injury history recurrence                                  │ │ │
│  │  │                                                                │ │ │
│  │  │  Opponent Features:                                            │ │ │
│  │  │  • Defense vs Position rank                                   │ │ │
│  │  │  • Pace factor                                                │ │ │
│  │  │  • Recent defensive performance                               │ │ │
│  │  │  • Key defender matchups                                      │ │ │
│  │  │                                                                │ │ │
│  │  │  Context Features:                                             │ │ │
│  │  │  • Home/Away                                                  │ │ │
│  │  │  • Days since last game                                       │ │ │
│  │  │  • Travel distance                                            │ │ │
│  │  │  • Time zone changes                                          │ │ │
│  │  │  • Altitude (Denver factor)                                   │ │ │
│  │  │  • Teammate injury impact                                     │ │ │
│  │  │  • Trade deadline impact                                      │ │ │
│  │  │  • Load management flags                                      │ │ │
│  │  │                                                                │ │ │
│  │  │  Temporal Features:                                            │ │ │
│  │  │  • Day of week                                                │ │ │
│  │  │  • Month of season                                            │ │ │
│  │  │  • Days until All-Star break                                  │ │ │
│  │  │  • Playoff race intensity                                     │ │ │
│  │  │                                                                │ │ │
│  │  └───────────────────────────────────────────────────────────────┘ │ │
│  │                              │                                      │ │
│  └──────────────────────────────┼──────────────────────────────────────┘ │
│                                 │                                        │
│  ┌──────────────────────────────▼──────────────────────────────────────┐ │
│  │                      MODEL TRAINING LAYER                            │ │
│  ├──────────────────────────────────────────────────────────────────────┤ │
│  │                                                                       │ │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │ │
│  │  │                    Ensemble Model Architecture                   │ │ │
│  │  ├─────────────────────────────────────────────────────────────────┤ │ │
│  │  │                                                                  │ │ │
│  │  │    ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │ │ │
│  │  │    │   XGBoost   │  │  LightGBM   │  │   LSTM (PyTorch)    │   │ │ │
│  │  │    │             │  │             │  │                     │   │ │ │
│  │  │    │ • Points    │  │ • Points    │  │ • Sequence-based    │   │ │ │
│  │  │    │ • Rebounds  │  │ • Rebounds  │  │   predictions       │   │ │ │
│  │  │    │ • Assists   │  │ • Assists   │  │ • Hot/cold streaks  │   │ │ │
│  │  │    │ • Steals    │  │ • Steals    │  │ • Injury return     │   │ │ │
│  │  │    │ • Blocks    │  │ • Blocks    │  │   ramp-up           │   │ │ │
│  │  │    │ • Turnovers │  │ • Turnovers │  │                     │   │ │ │
│  │  │    │ • FG%       │  │ • FG%       │  │                     │   │ │ │
│  │  │    │ • FT%       │  │ • FT%       │  │                     │   │ │ │
│  │  │    │ • 3PM       │  │ • 3PM       │  │                     │   │ │ │
│  │  │    └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘   │ │ │
│  │  │           │                │                    │              │ │ │
│  │  │           └────────────────┴────────────────────┘              │ │ │
│  │  │                            │                                    │ │ │
│  │  │                            ▼                                    │ │ │
│  │  │                   ┌─────────────────┐                          │ │ │
│  │  │                   │  Meta-Learner   │                          │ │ │
│  │  │                   │  (Stacking)     │                          │ │ │
│  │  │                   │                 │                          │ │ │
│  │  │                   │ Weights models  │                          │ │ │
│  │  │                   │ by context      │                          │ │ │
│  │  │                   └────────┬────────┘                          │ │ │
│  │  │                            │                                    │ │ │
│  │  └────────────────────────────┼────────────────────────────────────┘ │ │
│  │                               │                                       │ │
│  └───────────────────────────────┼───────────────────────────────────────┘ │
│                                  │                                         │
│  ┌───────────────────────────────▼───────────────────────────────────────┐ │
│  │                      MODEL EVALUATION & REGISTRY                       │ │
│  ├───────────────────────────────────────────────────────────────────────┤ │
│  │                                                                        │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────┐  │ │
│  │  │   MLflow       │  │  Backtesting   │  │   A/B Testing          │  │ │
│  │  │                │  │                │  │                        │  │ │
│  │  │ • Version ctrl │  │ • Walk-forward │  │ • Shadow mode          │  │ │
│  │  │ • Experiment   │  │   validation   │  │ • Champion/Challenger  │  │ │
│  │  │   tracking     │  │ • Out-of-time  │  │ • Gradual rollout      │  │ │
│  │  │ • Model        │  │   testing      │  │                        │  │ │
│  │  │   registry     │  │ • Seasonal     │  │                        │  │ │
│  │  │ • Artifact     │  │   holdout      │  │                        │  │ │
│  │  │   storage      │  │                │  │                        │  │ │
│  │  └────────────────┘  └────────────────┘  └────────────────────────┘  │ │
│  │                                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                        INFERENCE LAYER                                  │ │
│  ├────────────────────────────────────────────────────────────────────────┤ │
│  │                                                                         │ │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────────┐  │ │
│  │  │  Batch        │  │  Real-time    │  │  Explainability           │  │ │
│  │  │  Inference    │  │  Inference    │  │  (SHAP)                   │  │ │
│  │  │               │  │               │  │                           │  │ │
│  │  │ • Nightly     │  │ • On-demand   │  │ • Feature importance      │  │ │
│  │  │   predictions │  │   API calls   │  │ • Individual explanations │  │ │
│  │  │ • All players │  │ • Sub-second  │  │ • Factor descriptions     │  │ │
│  │  │ • All games   │  │   latency     │  │                           │  │ │
│  │  └───────────────┘  └───────────────┘  └───────────────────────────┘  │ │
│  │                                                                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Feature Engineering Details

```python
# Feature engineering categories and implementation

class FeatureEngineer:
    """
    Comprehensive feature engineering for fantasy basketball predictions.
    """

    # Rolling window features
    ROLLING_WINDOWS = [3, 5, 10, 20]

    # Target statistics
    TARGET_STATS = [
        'points', 'rebounds', 'assists', 'steals', 'blocks',
        'turnovers', 'fg3m', 'fg_pct', 'ft_pct', 'minutes'
    ]

    def compute_rolling_features(self, player_games: pd.DataFrame) -> pd.DataFrame:
        """Compute rolling averages and trends."""
        features = pd.DataFrame()

        for stat in self.TARGET_STATS:
            for window in self.ROLLING_WINDOWS:
                # Rolling average
                features[f'{stat}_avg_{window}g'] = (
                    player_games[stat].rolling(window).mean()
                )

                # Rolling std (volatility)
                features[f'{stat}_std_{window}g'] = (
                    player_games[stat].rolling(window).std()
                )

                # Trend (slope of rolling window)
                features[f'{stat}_trend_{window}g'] = (
                    player_games[stat].rolling(window).apply(self._calculate_trend)
                )

        return features

    def compute_opponent_features(self, player_id: int, opponent_id: int) -> dict:
        """Compute opponent-specific features."""
        return {
            'opp_def_rating': self._get_opponent_def_rating(opponent_id),
            'opp_pace': self._get_opponent_pace(opponent_id),
            'opp_vs_position_rank': self._get_dvp_rank(opponent_id, player_position),
            'opp_recent_def_trend': self._get_recent_defense_trend(opponent_id),
            'historical_vs_opponent': self._get_historical_matchup(player_id, opponent_id),
        }

    def compute_context_features(self, game_info: dict) -> dict:
        """Compute contextual features."""
        return {
            'is_home': game_info['is_home'],
            'rest_days': game_info['rest_days'],
            'is_back_to_back': game_info['rest_days'] == 0,
            'is_second_of_b2b': game_info.get('is_second_of_b2b', False),
            'travel_distance': self._calculate_travel_distance(game_info),
            'timezone_change': game_info.get('timezone_change', 0),
            'altitude_factor': 1.0 if game_info['venue'] == 'Denver' else 0.0,
            'days_since_injury_return': game_info.get('days_since_return'),
            'teammate_injuries': len(game_info.get('injured_teammates', [])),
            'key_teammate_out': game_info.get('key_teammate_out', False),
        }

    def compute_temporal_features(self, game_date: date) -> dict:
        """Compute time-based features."""
        season_start = date(game_date.year if game_date.month >= 10 else game_date.year - 1, 10, 1)
        days_into_season = (game_date - season_start).days

        return {
            'day_of_week': game_date.weekday(),
            'month': game_date.month,
            'days_into_season': days_into_season,
            'is_pre_allstar': days_into_season < 120,
            'is_playoff_push': days_into_season > 150,
            'is_load_management_risk': days_into_season > 140 and game_date.weekday() in [1, 3],  # B2B days
        }
```

### Model Training Configuration

```yaml
# XGBoost Configuration
xgboost_config:
  per_category_models: true
  base_params:
    objective: "reg:squarederror"
    eval_metric: "rmse"
    tree_method: "hist"
    device: "cuda"  # GPU acceleration

  hyperparameter_search:
    method: "optuna"
    n_trials: 100

    param_space:
      max_depth: [3, 10]
      learning_rate: [0.01, 0.3]
      n_estimators: [100, 1000]
      subsample: [0.6, 1.0]
      colsample_bytree: [0.6, 1.0]
      min_child_weight: [1, 10]
      reg_alpha: [0, 1]
      reg_lambda: [0, 1]

# LightGBM Configuration
lightgbm_config:
  base_params:
    objective: "regression"
    metric: "rmse"
    boosting_type: "gbdt"
    device: "gpu"

  hyperparameter_search:
    method: "optuna"
    n_trials: 100

    param_space:
      num_leaves: [20, 100]
      learning_rate: [0.01, 0.3]
      n_estimators: [100, 1000]
      feature_fraction: [0.6, 1.0]
      bagging_fraction: [0.6, 1.0]
      min_child_samples: [5, 100]

# LSTM Configuration
lstm_config:
  sequence_length: 10  # Last 10 games
  hidden_size: 128
  num_layers: 2
  dropout: 0.2
  bidirectional: true

  training:
    epochs: 100
    batch_size: 32
    learning_rate: 0.001
    early_stopping_patience: 10

# Ensemble Configuration
ensemble_config:
  method: "stacking"
  meta_learner: "ridge"

  base_model_weights:
    xgboost: 0.4
    lightgbm: 0.35
    lstm: 0.25

  context_weighting:
    # LSTM gets more weight for returning from injury
    injury_return: {xgboost: 0.3, lightgbm: 0.3, lstm: 0.4}
    # XGBoost for normal situations
    normal: {xgboost: 0.45, lightgbm: 0.35, lstm: 0.2}
    # More LSTM weight for hot/cold streaks
    streak: {xgboost: 0.3, lightgbm: 0.3, lstm: 0.4}
```

### Backtesting Framework

```python
class BacktestEngine:
    """
    Walk-forward validation for fantasy basketball predictions.
    """

    def __init__(self, config: BacktestConfig):
        self.train_window_days = config.train_window_days  # 365
        self.test_window_days = config.test_window_days    # 7
        self.step_days = config.step_days                   # 7

    def run_backtest(
        self,
        model: BaseModel,
        start_date: date,
        end_date: date
    ) -> BacktestResults:
        """
        Run walk-forward backtesting.

        Train on [t-365, t], test on [t+1, t+7], step forward by 7 days.
        """
        results = []
        current_date = start_date

        while current_date < end_date:
            # Training period
            train_start = current_date - timedelta(days=self.train_window_days)
            train_end = current_date

            # Test period
            test_start = current_date + timedelta(days=1)
            test_end = min(
                current_date + timedelta(days=self.test_window_days),
                end_date
            )

            # Train model
            train_data = self.get_data(train_start, train_end)
            model.fit(train_data)

            # Generate predictions
            test_data = self.get_data(test_start, test_end)
            predictions = model.predict(test_data)

            # Calculate metrics
            metrics = self.calculate_metrics(predictions, test_data.actuals)
            results.append({
                'test_period_start': test_start,
                'test_period_end': test_end,
                'metrics': metrics
            })

            # Step forward
            current_date += timedelta(days=self.step_days)

        return BacktestResults(results)

    def calculate_metrics(self, predictions: pd.DataFrame, actuals: pd.DataFrame) -> dict:
        """Calculate comprehensive evaluation metrics."""
        return {
            'mae': mean_absolute_error(actuals, predictions),
            'rmse': np.sqrt(mean_squared_error(actuals, predictions)),
            'r2': r2_score(actuals, predictions),
            'mape': mean_absolute_percentage_error(actuals, predictions),
            'within_5pct': (abs(predictions - actuals) / actuals < 0.05).mean(),
            'within_10pct': (abs(predictions - actuals) / actuals < 0.10).mean(),
            'within_20pct': (abs(predictions - actuals) / actuals < 0.20).mean(),
            'directional_accuracy': (np.sign(predictions - predictions.shift(1)) ==
                                    np.sign(actuals - actuals.shift(1))).mean(),
        }
```

### Confidence Interval Calculation

```python
class ConfidenceCalculator:
    """
    Calculate prediction confidence intervals and uncertainty estimates.
    """

    def calculate_confidence(
        self,
        predictions: np.ndarray,
        player_id: int,
        context: dict
    ) -> ConfidenceResult:
        """
        Calculate confidence interval and overall confidence score.

        Uses:
        - Model uncertainty (prediction variance across ensemble)
        - Historical accuracy for this player
        - Context-specific adjustments
        """

        # 1. Model uncertainty from ensemble
        ensemble_std = np.std(predictions)

        # 2. Historical accuracy for player
        historical_accuracy = self._get_player_accuracy(player_id)

        # 3. Context adjustments
        context_multiplier = self._get_context_multiplier(context)

        # Calculate confidence interval
        mean_pred = np.mean(predictions)
        margin = 1.96 * ensemble_std * context_multiplier

        # Overall confidence score (0-1)
        base_confidence = 1 - (ensemble_std / mean_pred) if mean_pred > 0 else 0
        confidence = base_confidence * historical_accuracy * (1 / context_multiplier)
        confidence = np.clip(confidence, 0.1, 0.95)

        return ConfidenceResult(
            value=mean_pred,
            low=mean_pred - margin,
            high=mean_pred + margin,
            confidence=confidence
        )

    def _get_context_multiplier(self, context: dict) -> float:
        """
        Increase uncertainty for specific contexts.
        """
        multiplier = 1.0

        # Injury return increases uncertainty
        if context.get('days_since_injury_return', float('inf')) < 5:
            multiplier *= 1.5

        # First game with new team
        if context.get('games_with_team', float('inf')) < 3:
            multiplier *= 1.4

        # Back-to-back increases uncertainty
        if context.get('is_back_to_back'):
            multiplier *= 1.2

        # Playing top defense increases uncertainty
        if context.get('opp_def_rank', 15) <= 5:
            multiplier *= 1.15

        return multiplier
```

### Z-Score Calculation

```python
class ZScoreCalculator:
    """
    Calculate fantasy z-scores for player valuations.

    Uses robust statistics to handle non-normal distributions.
    """

    def __init__(self, league_settings: LeagueSettings):
        self.format = league_settings.format
        self.categories = league_settings.categories or [
            'points', 'rebounds', 'assists', 'steals', 'blocks',
            'fg_pct', 'ft_pct', 'fg3m', 'turnovers'
        ]
        self.punting = league_settings.punting or []

    def calculate_player_z_scores(
        self,
        player_stats: pd.Series,
        population_stats: pd.DataFrame,
        replacement_level: str = 'median'
    ) -> dict:
        """
        Calculate z-scores for each category using robust methods.
        """
        z_scores = {}

        for category in self.categories:
            if category in self.punting:
                z_scores[category] = 0.0
                continue

            player_value = player_stats[category]

            # Use median and MAD for robustness against outliers
            pop_median = population_stats[category].median()
            pop_mad = self._median_absolute_deviation(population_stats[category])

            # Convert MAD to standard deviation equivalent
            pop_std_robust = pop_mad * 1.4826

            if pop_std_robust == 0:
                z_scores[category] = 0.0
            else:
                z = (player_value - pop_median) / pop_std_robust

                # Turnovers are negative (invert)
                if category == 'turnovers':
                    z = -z

                z_scores[category] = round(z, 2)

        z_scores['total'] = round(sum(z_scores.values()), 2)

        return z_scores

    def _median_absolute_deviation(self, x: pd.Series) -> float:
        """Calculate MAD for robust standard deviation."""
        return np.median(np.abs(x - np.median(x)))

    def calculate_points_league_value(
        self,
        player_stats: pd.Series,
        point_values: dict
    ) -> float:
        """
        Calculate projected fantasy points for points leagues.
        """
        total_points = 0.0

        for stat, value in point_values.items():
            if stat in player_stats:
                total_points += player_stats[stat] * value

        # Handle double-double and triple-double bonuses
        counting_stats = [
            player_stats.get('points', 0),
            player_stats.get('rebounds', 0),
            player_stats.get('assists', 0),
            player_stats.get('steals', 0),
            player_stats.get('blocks', 0),
        ]
        doubles = sum(1 for s in counting_stats if s >= 10)

        if doubles >= 3 and 'triple_double' in point_values:
            total_points += point_values['triple_double']
        elif doubles >= 2 and 'double_double' in point_values:
            total_points += point_values['double_double']

        return round(total_points, 2)
```

---

## Real-Time Data Integration

### Data Source Failover Strategy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DATA SOURCE FAILOVER ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Primary: nba_api                                                        │
│  ┌─────────────────┐                                                    │
│  │ Health Check    │◄── Every 60 seconds                                │
│  │ Rate: 100/min   │                                                    │
│  └────────┬────────┘                                                    │
│           │                                                              │
│           ▼ Success                                                      │
│  ┌─────────────────┐         ┌─────────────────┐                       │
│  │   Use nba_api   │────────►│  Update Cache   │                       │
│  └─────────────────┘         └─────────────────┘                       │
│           │                                                              │
│           ▼ Failure (3 retries)                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     FAILOVER CHAIN                               │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │                                                                  │   │
│  │  Level 1: ESPN Hidden API                                        │   │
│  │  ┌─────────────────┐                                            │   │
│  │  │ Try ESPN API    │──► Success ──► Update Cache                │   │
│  │  │ (Unofficial)    │                                            │   │
│  │  └────────┬────────┘                                            │   │
│  │           │ Failure                                              │   │
│  │           ▼                                                      │   │
│  │  Level 2: Basketball-Reference Scraper                          │   │
│  │  ┌─────────────────┐                                            │   │
│  │  │ Scrape BBRef    │──► Success ──► Update Cache                │   │
│  │  │ (Respect ToS)   │                                            │   │
│  │  └────────┬────────┘                                            │   │
│  │           │ Failure                                              │   │
│  │           ▼                                                      │   │
│  │  Level 3: Cached Data + Alert                                   │   │
│  │  ┌─────────────────┐                                            │   │
│  │  │ Serve Stale     │──► Alert Team                              │   │
│  │  │ Cache + Warning │                                            │   │
│  │  └─────────────────┘                                            │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  Circuit Breaker Settings:                                               │
│  • Failure threshold: 5 failures in 1 minute                            │
│  • Open state duration: 30 seconds                                       │
│  • Half-open test: 1 request                                            │
│  • Reset on success: Full reset                                         │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### NBA API Wrapper with Resilience

```python
class ResilientNBAClient:
    """
    NBA API client with retry, circuit breaker, and failover.
    """

    def __init__(self):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=30,
            expected_exception=Exception
        )
        self.rate_limiter = RateLimiter(max_calls=100, period=60)
        self.cache = RedisCache(ttl=300)  # 5 minute default TTL

    @circuit_breaker
    @rate_limited
    async def get_player_stats(
        self,
        player_id: int,
        season: str = "2024-25"
    ) -> PlayerStats:
        """Get player stats with full resilience."""

        cache_key = f"player_stats:{player_id}:{season}"

        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        # Try primary source (nba_api)
        try:
            stats = await self._fetch_from_nba_api(player_id, season)
            await self.cache.set(cache_key, stats, ttl=300)
            return stats
        except NBAAPIError as e:
            logger.warning(f"NBA API failed: {e}")

        # Failover to ESPN
        try:
            stats = await self._fetch_from_espn(player_id, season)
            await self.cache.set(cache_key, stats, ttl=300)
            return stats
        except ESPNAPIError as e:
            logger.warning(f"ESPN API failed: {e}")

        # Final failover to Basketball-Reference
        try:
            stats = await self._fetch_from_bbref(player_id, season)
            await self.cache.set(cache_key, stats, ttl=600)  # Longer TTL for scraped data
            return stats
        except Exception as e:
            logger.error(f"All sources failed: {e}")

        # Return stale cache if available
        stale = await self.cache.get(cache_key, allow_stale=True)
        if stale:
            logger.warning(f"Serving stale data for player {player_id}")
            return stale

        raise DataUnavailableError(f"Cannot fetch stats for player {player_id}")
```

### Injury Feed Integration

```python
class InjuryMonitor:
    """
    Real-time injury monitoring from multiple sources.
    """

    def __init__(self):
        self.sources = [
            TwitterInjuryFeed(),
            ESPNInjuryFeed(),
            YahooInjuryFeed(),
            OfficialNBAFeed(),
        ]
        self.alert_system = AlertSystem()

    async def start_monitoring(self):
        """Start real-time injury monitoring."""
        tasks = [
            asyncio.create_task(source.stream_updates(self.process_update))
            for source in self.sources
        ]
        await asyncio.gather(*tasks)

    async def process_update(self, update: InjuryUpdate):
        """Process incoming injury update."""

        # Deduplicate across sources
        if await self._is_duplicate(update):
            return

        # Validate and enrich
        enriched = await self._enrich_update(update)

        # Store in database
        await self._store_injury(enriched)

        # Update player status
        await self._update_player_status(enriched.player_id, enriched.status)

        # Trigger re-predictions if significant
        if enriched.is_significant_change:
            await self._trigger_prediction_refresh(enriched.player_id)

        # Send alerts to subscribed users
        await self.alert_system.send_injury_alert(enriched)

        # Publish to WebSocket
        await self._broadcast_to_websocket(enriched)


class TwitterInjuryFeed:
    """
    Monitor NBA reporters on Twitter/X for injury updates.
    """

    TRUSTED_ACCOUNTS = [
        'ShamsCharania',
        'wojespn',
        'FantasyLabsNBA',
        'Underdog__NBA',
    ]

    INJURY_KEYWORDS = [
        'OUT', 'questionable', 'doubtful', 'injury', 'injured',
        'day-to-day', 'DNP', 'rest', 'load management', 'ruled out'
    ]

    async def stream_updates(self, callback):
        """Stream filtered tweets from trusted accounts."""
        # Twitter API v2 filtered stream implementation
        ...
```

### WebSocket Real-Time Updates

```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio

class ConnectionManager:
    """Manage WebSocket connections and subscriptions."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, Set[str]] = {}  # channel -> connection_ids

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
        for channel in list(self.subscriptions.keys()):
            self.subscriptions[channel].discard(user_id)

    async def subscribe(self, user_id: str, channels: list[str]):
        for channel in channels:
            if channel not in self.subscriptions:
                self.subscriptions[channel] = set()
            self.subscriptions[channel].add(user_id)

    async def broadcast_to_channel(self, channel: str, message: dict):
        if channel not in self.subscriptions:
            return

        disconnected = []
        for user_id in self.subscriptions[channel]:
            ws = self.active_connections.get(user_id)
            if ws:
                try:
                    await ws.send_json(message)
                except:
                    disconnected.append(user_id)

        for user_id in disconnected:
            self.disconnect(user_id)


manager = ConnectionManager()


@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket, token: str):
    # Validate token
    user = await verify_token(token)
    if not user:
        await websocket.close(code=4001)
        return

    await manager.connect(websocket, user.id)

    try:
        while True:
            data = await websocket.receive_json()

            if data.get('action') == 'subscribe':
                await manager.subscribe(user.id, data.get('channels', []))
                await websocket.send_json({
                    'type': 'subscription_confirmed',
                    'channels': data.get('channels')
                })

            elif data.get('action') == 'unsubscribe':
                # Handle unsubscribe
                pass

    except WebSocketDisconnect:
        manager.disconnect(user.id)


# Broadcasting updates
async def broadcast_injury_update(injury: InjuryUpdate):
    """Broadcast injury update to relevant channels."""
    message = {
        'type': 'injury_alert',
        'data': {
            'player_id': injury.player_id,
            'player_name': injury.player_name,
            'team': injury.team_abbreviation,
            'status': injury.status,
            'description': injury.description,
            'source': injury.source,
            'timestamp': injury.reported_at.isoformat()
        }
    }

    # Broadcast to general injuries channel
    await manager.broadcast_to_channel('injuries:all', message)

    # Broadcast to player-specific channel
    await manager.broadcast_to_channel(f'player:{injury.player_id}', message)

    # Broadcast to team-specific channel
    await manager.broadcast_to_channel(f'team:{injury.team_id}', message)
```

---

## Notification System

### Alert Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      NOTIFICATION SYSTEM ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                      TRIGGER SOURCES                                │ │
│  ├────────────────────────────────────────────────────────────────────┤ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────────┐ │ │
│  │  │ Injury   │  │ Pred.    │  │ Game     │  │ Recommendation     │ │ │
│  │  │ Updates  │  │ Changes  │  │ Events   │  │ Ready              │ │ │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────┬─────────┘ │ │
│  │       │             │             │                   │            │ │
│  │       └─────────────┴─────────────┴───────────────────┘            │ │
│  │                              │                                      │ │
│  └──────────────────────────────┼──────────────────────────────────────┘ │
│                                 │                                        │
│                                 ▼                                        │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                      NOTIFICATION ENGINE                            │ │
│  ├────────────────────────────────────────────────────────────────────┤ │
│  │                                                                     │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐│ │
│  │  │  Alert Matcher  │  │  User Prefs     │  │  Rate Limiter       ││ │
│  │  │                 │  │  Checker        │  │                     ││ │
│  │  │  Match events   │  │                 │  │  Prevent spam       ││ │
│  │  │  to user alerts │  │  Check channels │  │  Max 10/hour        ││ │
│  │  └────────┬────────┘  └────────┬────────┘  └──────────┬──────────┘│ │
│  │           │                    │                      │           │ │
│  │           └────────────────────┴──────────────────────┘           │ │
│  │                              │                                     │ │
│  └──────────────────────────────┼─────────────────────────────────────┘ │
│                                 │                                        │
│                                 ▼                                        │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                      DELIVERY CHANNELS                              │ │
│  ├────────────────────────────────────────────────────────────────────┤ │
│  │                                                                     │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────┐│ │
│  │  │   In-App     │  │    Email     │  │    Push      │  │   SMS   ││ │
│  │  │  (WebSocket) │  │  (SendGrid)  │  │  (Firebase)  │  │(Twilio) ││ │
│  │  │              │  │              │  │              │  │         ││ │
│  │  │  Instant     │  │  Batched     │  │  Instant     │  │ Urgent  ││ │
│  │  │  Real-time   │  │  Digest opt  │  │  Mobile      │  │ Only    ││ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └─────────┘│ │
│  │                                                                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Notification Types and Configuration

```python
class NotificationType(Enum):
    INJURY_UPDATE = "injury_update"
    GAME_START = "game_start"
    PREDICTION_CHANGE = "prediction_change"
    WAIVER_TARGET = "waiver_target"
    TRADE_SUGGESTION = "trade_suggestion"
    LINEUP_REMINDER = "lineup_reminder"
    WEEKLY_REPORT = "weekly_report"

class NotificationConfig:
    """Default notification configurations."""

    DEFAULTS = {
        NotificationType.INJURY_UPDATE: {
            'channels': ['in_app', 'push'],
            'priority': 'high',
            'rate_limit': 20,  # per hour
            'conditions': {
                'status_change': True,  # OUT -> healthy, etc.
                'owned_players_only': True,
            }
        },
        NotificationType.GAME_START: {
            'channels': ['push'],
            'priority': 'medium',
            'timing': 'minutes_before=30',
            'conditions': {
                'owned_players_only': True,
            }
        },
        NotificationType.PREDICTION_CHANGE: {
            'channels': ['in_app'],
            'priority': 'low',
            'rate_limit': 10,
            'conditions': {
                'change_pct_threshold': 15,  # >15% change
                'owned_players_only': True,
            }
        },
        NotificationType.WAIVER_TARGET: {
            'channels': ['in_app', 'email'],
            'priority': 'medium',
            'timing': 'daily_digest',
            'conditions': {
                'ownership_below': 50,
                'z_score_above': 1.5,
            }
        },
        NotificationType.LINEUP_REMINDER: {
            'channels': ['push'],
            'priority': 'high',
            'timing': 'hours_before=1',
            'conditions': {
                'has_empty_slots': True,
            }
        },
    }
```

### Push Notification Implementation

```python
from firebase_admin import messaging, credentials
import firebase_admin

class PushNotificationService:
    """Firebase Cloud Messaging for push notifications."""

    def __init__(self):
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(cred)

    async def send_notification(
        self,
        user_id: str,
        title: str,
        body: str,
        data: dict = None,
        priority: str = 'high'
    ):
        """Send push notification to user's devices."""

        # Get user's device tokens
        tokens = await self._get_user_tokens(user_id)

        if not tokens:
            return

        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            tokens=tokens,
            android=messaging.AndroidConfig(
                priority='high' if priority == 'high' else 'normal',
                notification=messaging.AndroidNotification(
                    icon='notification_icon',
                    color='#4F46E5',
                    click_action='FLUTTER_NOTIFICATION_CLICK',
                )
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        badge=1,
                        sound='default',
                    )
                )
            )
        )

        response = messaging.send_multicast(message)

        # Handle failed tokens (unregister invalid ones)
        if response.failure_count > 0:
            await self._handle_failed_tokens(tokens, response.responses)

    async def send_injury_alert(self, injury: InjuryUpdate, user_ids: list[str]):
        """Send injury alert to multiple users."""

        title = f"🚨 {injury.player_name} - {injury.status.upper()}"
        body = injury.description or f"{injury.player_name} status changed to {injury.status}"

        data = {
            'type': 'injury_alert',
            'player_id': str(injury.player_id),
            'screen': 'player_detail',
        }

        # Batch send for efficiency
        for user_id in user_ids:
            await self.send_notification(user_id, title, body, data)
```

---

## Security

### Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       AUTHENTICATION FLOW                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. Registration                                                         │
│  ┌──────────┐         ┌──────────┐         ┌──────────┐                │
│  │  Client  │────────►│   API    │────────►│   DB     │                │
│  │          │  POST   │          │  Hash   │          │                │
│  │          │ /register│         │ password│  Store   │                │
│  └──────────┘         └──────────┘         └──────────┘                │
│                              │                                          │
│                              ▼                                          │
│                       Send verification email                           │
│                                                                          │
│  2. Login                                                               │
│  ┌──────────┐         ┌──────────┐         ┌──────────┐                │
│  │  Client  │────────►│   API    │────────►│   DB     │                │
│  │          │  POST   │          │ Verify  │          │                │
│  │          │ /login  │          │ password│  Lookup  │                │
│  └────┬─────┘         └────┬─────┘         └──────────┘                │
│       │                    │                                            │
│       │◄───────────────────┘                                            │
│       │  {access_token, refresh_token}                                  │
│       │                                                                  │
│       ▼                                                                  │
│  Store tokens (httpOnly cookie or localStorage)                         │
│                                                                          │
│  3. Authenticated Request                                               │
│  ┌──────────┐         ┌──────────┐         ┌──────────┐                │
│  │  Client  │────────►│   API    │────────►│ Resource │                │
│  │          │  GET    │          │ Verify  │          │                │
│  │  + Auth  │ /data   │ JWT      │ Token   │  Return  │                │
│  │  Header  │         │ Check    │         │  Data    │                │
│  └──────────┘         └──────────┘         └──────────┘                │
│                                                                          │
│  4. Token Refresh                                                       │
│  ┌──────────┐         ┌──────────┐         ┌──────────┐                │
│  │  Client  │────────►│   API    │────────►│   DB     │                │
│  │          │  POST   │          │ Verify  │          │                │
│  │+ Refresh │ /refresh│ refresh  │ token   │ Generate │                │
│  │  Token   │         │ token    │ valid   │ new pair │                │
│  └────┬─────┘         └────┬─────┘         └──────────┘                │
│       │                    │                                            │
│       │◄───────────────────┘                                            │
│       │  {new_access_token, new_refresh_token}                          │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### JWT Configuration

```python
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow(),
        "jti": str(uuid.uuid4()),  # Unique token ID for revocation
    })
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token."""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow(),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

async def verify_token(token: str, token_type: str = "access") -> TokenData:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

        if payload.get("type") != token_type:
            raise InvalidTokenError("Invalid token type")

        # Check if token is revoked (stored in Redis)
        if await is_token_revoked(payload.get("jti")):
            raise TokenRevokedError("Token has been revoked")

        return TokenData(**payload)

    except JWTError:
        raise InvalidTokenError("Invalid token")

async def revoke_token(jti: str, expires_at: datetime):
    """Add token to revocation list."""
    ttl = (expires_at - datetime.utcnow()).total_seconds()
    await redis.setex(f"revoked_token:{jti}", int(ttl), "1")

async def revoke_all_user_tokens(user_id: str):
    """Revoke all tokens for a user."""
    # Store user's token revocation timestamp
    await redis.set(f"user_tokens_revoked:{user_id}", datetime.utcnow().isoformat())
```

### API Security Middleware

```python
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time

class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware."""

    async def dispatch(self, request: Request, call_next):
        # 1. Rate limiting (in addition to API gateway)
        if not await self._check_rate_limit(request):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        # 2. Request validation
        if not self._validate_request(request):
            raise HTTPException(status_code=400, detail="Invalid request")

        # 3. Add security headers
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        # 4. Add request ID for tracing
        response.headers["X-Request-ID"] = request.state.request_id

        return response

    def _validate_request(self, request: Request) -> bool:
        """Validate request for common attacks."""
        # Check for SQL injection patterns
        # Check for XSS patterns
        # Validate content-type
        return True
```

### Data Encryption

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class EncryptionService:
    """Encrypt sensitive data at rest."""

    def __init__(self):
        self.key = self._derive_key(settings.ENCRYPTION_KEY)
        self.fernet = Fernet(self.key)

    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=settings.ENCRYPTION_SALT.encode(),
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def encrypt(self, data: str) -> str:
        """Encrypt string data."""
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data."""
        return self.fernet.decrypt(encrypted_data.encode()).decode()

# Usage for sensitive fields
class YahooToken(Base):
    __tablename__ = "yahoo_tokens"

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    _access_token = Column("access_token", String)  # Encrypted
    _refresh_token = Column("refresh_token", String)  # Encrypted

    @property
    def access_token(self) -> str:
        return encryption_service.decrypt(self._access_token)

    @access_token.setter
    def access_token(self, value: str):
        self._access_token = encryption_service.encrypt(value)
```

---

## Performance & Scaling

### Caching Strategy

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CACHING ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Layer 1: CDN Cache (Cloudflare)                                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  • Static assets: 1 year                                         │   │
│  │  • API responses: Configurable by endpoint                       │   │
│  │  • Stale-while-revalidate for API calls                         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  Layer 2: Application Cache (Redis)                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                  │   │
│  │  Hot Data (TTL: 5 min)              Warm Data (TTL: 1 hour)     │   │
│  │  ├─ Live game scores                ├─ Player season stats      │   │
│  │  ├─ Current injury status           ├─ Team standings           │   │
│  │  ├─ Today's predictions             ├─ Z-score rankings         │   │
│  │  └─ Active WebSocket sessions       └─ Defense vs Position      │   │
│  │                                                                  │   │
│  │  Cold Data (TTL: 24 hours)          Computed Data (TTL: 1 hour) │   │
│  │  ├─ Historical game logs            ├─ Custom rankings          │   │
│  │  ├─ Player bio information          ├─ Trade analysis           │   │
│  │  ├─ Team schedules                  └─ Matchup projections      │   │
│  │  └─ News articles                                                │   │
│  │                                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  Layer 3: Database Query Cache (PostgreSQL)                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  • Materialized views for rankings                               │   │
│  │  • Prepared statements                                           │   │
│  │  • Connection pooling (PgBouncer)                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

Cache Invalidation Strategy:
• Event-driven invalidation via Kafka
• Time-based expiration
• Manual invalidation API for admin
• Pattern-based invalidation (player:* when team trades)
```

### Database Optimization

```sql
-- Materialized view for player rankings (refreshed hourly)
CREATE MATERIALIZED VIEW mv_player_rankings AS
SELECT
    p.id,
    p.full_name,
    p.position,
    p.team_abbreviation,
    s.games_played,
    s.points_pg,
    s.rebounds_pg,
    s.assists_pg,
    s.steals_pg,
    s.blocks_pg,
    s.fg_pct,
    s.ft_pct,
    s.fg3m_pg,
    s.turnovers_pg,
    -- Z-scores calculated
    (s.points_pg - avg_stats.avg_points) / NULLIF(avg_stats.std_points, 0) as z_points,
    (s.rebounds_pg - avg_stats.avg_rebounds) / NULLIF(avg_stats.std_rebounds, 0) as z_rebounds,
    -- ... more z-scores
    -- Total z-score
    COALESCE(z_points, 0) + COALESCE(z_rebounds, 0) + ... as z_score_total,
    RANK() OVER (ORDER BY z_score_total DESC) as overall_rank,
    RANK() OVER (PARTITION BY p.position ORDER BY z_score_total DESC) as position_rank
FROM players p
JOIN player_season_stats s ON p.id = s.player_id
CROSS JOIN (
    SELECT
        AVG(points_pg) as avg_points,
        STDDEV(points_pg) as std_points,
        AVG(rebounds_pg) as avg_rebounds,
        STDDEV(rebounds_pg) as std_rebounds,
        -- ... more averages
    FROM player_season_stats
    WHERE season = '2024-25' AND games_played >= 10
) avg_stats
WHERE s.season = '2024-25' AND p.is_active = TRUE;

CREATE UNIQUE INDEX idx_mv_rankings_id ON mv_player_rankings(id);
CREATE INDEX idx_mv_rankings_position ON mv_player_rankings(position);
CREATE INDEX idx_mv_rankings_rank ON mv_player_rankings(overall_rank);

-- Refresh function
CREATE OR REPLACE FUNCTION refresh_rankings_view()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_player_rankings;
END;
$$ LANGUAGE plpgsql;

-- Schedule refresh (via pg_cron or Celery)
-- Every hour during season
```

### Horizontal Scaling Configuration

```yaml
# Kubernetes deployment example
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fantasy-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fantasy-api
  template:
    metadata:
      labels:
        app: fantasy-api
    spec:
      containers:
      - name: api
        image: fantasy-api:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: fantasy-secrets
              key: database-url
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fantasy-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fantasy-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Pods
        value: 4
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

### Performance Benchmarks

```yaml
Performance Targets:
  API Latency:
    p50: < 50ms
    p95: < 200ms
    p99: < 500ms

  Prediction Generation:
    single_player: < 100ms
    batch_100_players: < 2s

  Database Queries:
    simple_lookup: < 10ms
    complex_aggregation: < 100ms
    ranking_calculation: < 500ms

  WebSocket:
    connection_establish: < 100ms
    message_delivery: < 50ms

  Cache Hit Rate:
    target: > 90%

  Throughput:
    api_requests: 10,000 req/min
    websocket_connections: 50,000 concurrent

Load Testing Scenarios:
  - scenario: "Normal day"
    users: 5000
    requests_per_user: 20/hour

  - scenario: "Game night peak"
    users: 15000
    requests_per_user: 60/hour
    websocket_messages: 1000/min

  - scenario: "Season start spike"
    users: 30000
    requests_per_user: 100/hour
```

---

## Development Roadmap

### Phase 1: Foundation (Weeks 1-4)

**Week 1-2: Infrastructure Setup**
- [ ] PostgreSQL database with schema
- [ ] Redis cache configuration
- [ ] FastAPI application scaffold
- [ ] Docker Compose development environment
- [ ] CI/CD pipeline (GitHub Actions)

**Week 3-4: Data Pipeline**
- [ ] nba_api integration with resilience
- [ ] ESPN backup data source
- [ ] Data ingestion Celery tasks
- [ ] Historical data backfill
- [ ] Data quality monitoring

### Phase 2: Core Backend (Weeks 5-8)

**Week 5-6: Authentication & Users**
- [ ] JWT authentication system
- [ ] User registration/login
- [ ] Token refresh mechanism
- [ ] Password reset flow
- [ ] Email verification

**Week 7-8: Core API Endpoints**
- [ ] Player CRUD endpoints
- [ ] Stats endpoints with caching
- [ ] Basic rankings endpoint
- [ ] Health/status endpoints
- [ ] OpenAPI documentation

### Phase 3: ML Pipeline (Weeks 9-12)

**Week 9-10: Feature Engineering**
- [ ] Feature store setup (Feast)
- [ ] Rolling average features
- [ ] Opponent features
- [ ] Context features
- [ ] Feature validation pipeline

**Week 11-12: Model Training**
- [ ] XGBoost model implementation
- [ ] LightGBM model implementation
- [ ] Ensemble configuration
- [ ] Backtesting framework
- [ ] MLflow tracking setup

### Phase 4: Yahoo Integration (Weeks 13-15)

**Week 13: OAuth Flow**
- [ ] Yahoo OAuth 2.0 implementation
- [ ] Token storage with encryption
- [ ] Token refresh automation
- [ ] Connection status tracking

**Week 14-15: League Sync**
- [ ] League discovery
- [ ] Roster synchronization
- [ ] Scoring settings parsing
- [ ] Matchup data fetching
- [ ] Waiver wire integration

### Phase 5: Predictions & Recommendations (Weeks 16-19)

**Week 16-17: Prediction System**
- [ ] Real-time prediction API
- [ ] Batch prediction jobs
- [ ] Confidence intervals
- [ ] SHAP explanations
- [ ] Accuracy tracking

**Week 18-19: Recommendations**
- [ ] Start/sit algorithm
- [ ] Waiver wire recommendations
- [ ] Trade analyzer
- [ ] Streaming suggestions
- [ ] Recommendation feedback system

### Phase 6: Real-Time & Notifications (Weeks 20-22)

**Week 20: WebSocket Implementation**
- [ ] WebSocket server setup
- [ ] Subscription management
- [ ] Real-time game updates
- [ ] Injury alert broadcasting

**Week 21-22: Notification System**
- [ ] Push notification setup (Firebase)
- [ ] Email notifications (SendGrid)
- [ ] Alert configuration API
- [ ] Notification preferences
- [ ] Rate limiting for notifications

### Phase 7: Frontend Development (Weeks 23-28)

**Week 23-24: Core UI**
- [ ] Next.js project setup
- [ ] Authentication UI
- [ ] Dashboard layout
- [ ] Player search/browse

**Week 25-26: Feature Pages**
- [ ] Player detail pages
- [ ] Prediction displays
- [ ] Rankings views
- [ ] Team management

**Week 27-28: Advanced Features**
- [ ] WebSocket integration
- [ ] Mobile responsiveness
- [ ] Push notification handling
- [ ] PWA configuration

### Phase 8: Production & Scale (Weeks 29-32)

**Week 29-30: Production Hardening**
- [ ] Security audit
- [ ] Performance optimization
- [ ] Load testing (Locust)
- [ ] Error handling review

**Week 31-32: Launch**
- [ ] Staging environment
- [ ] Production deployment
- [ ] Monitoring setup
- [ ] Documentation finalization
- [ ] Beta user onboarding

---

## Appendix

### A. Environment Variables Reference

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/fantasy_bball
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Redis
REDIS_URL=redis://host:6379/0
REDIS_CACHE_TTL_DEFAULT=300

# Security
JWT_SECRET_KEY=<32-byte-hex>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=30
ENCRYPTION_KEY=<32-byte-key>

# Yahoo OAuth
YAHOO_CLIENT_ID=<client-id>
YAHOO_CLIENT_SECRET=<client-secret>
YAHOO_REDIRECT_URI=https://api.yourdomain.com/api/v1/yahoo/callback

# External APIs
NBA_API_TIMEOUT=30
ESPN_API_KEY=<if-needed>
TWITTER_BEARER_TOKEN=<bearer-token>

# Notifications
SENDGRID_API_KEY=<api-key>
FIREBASE_CREDENTIALS=<path-to-json>

# Monitoring
SENTRY_DSN=<sentry-dsn>
DATADOG_API_KEY=<api-key>

# Feature Flags
FEATURE_TRADE_ANALYZER=true
FEATURE_LIVE_SCORES=true
FEATURE_PUSH_NOTIFICATIONS=true

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

### B. API Rate Limits by Endpoint

| Endpoint Category | Free Tier | Pro Tier | Premium Tier |
|------------------|-----------|----------|--------------|
| `/auth/*` | 10/min | 20/min | 50/min |
| `/players/*` | 30/min | 100/min | 300/min |
| `/predictions/*` | 20/min | 60/min | 200/min |
| `/rankings/*` | 10/min | 30/min | 100/min |
| `/recommendations/*` | 10/min | 30/min | 100/min |
| `/yahoo/*` | 20/min | 60/min | 200/min |
| WebSocket connections | 1 | 3 | 10 |
| Batch operations | 10 items | 50 items | 200 items |

### C. Monitoring Dashboards

```yaml
Key Metrics to Track:
  Application:
    - Request rate (req/sec)
    - Error rate (4xx, 5xx)
    - Response latency (p50, p95, p99)
    - Active users (DAU, MAU)

  Infrastructure:
    - CPU utilization
    - Memory usage
    - Database connections
    - Cache hit rate
    - Queue depth

  Business:
    - Prediction accuracy (by category)
    - Recommendation adoption rate
    - User engagement (sessions/user)
    - Feature usage breakdown

  ML Pipeline:
    - Model inference latency
    - Feature freshness
    - Model drift detection
    - Training job success rate

Alerting Thresholds:
  Critical:
    - Error rate > 5%
    - P99 latency > 2s
    - Database connections > 80%
    - Cache hit rate < 70%

  Warning:
    - Error rate > 1%
    - P95 latency > 500ms
    - CPU > 70%
    - Memory > 80%
```

---

**Document Version:** 2.0
**Last Updated:** 2025-01-11
**Maintainer:** Development Team
