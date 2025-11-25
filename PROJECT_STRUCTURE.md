# Project Structure & Organization

**Version:** 2.0
**Last Updated:** 2025-01-11
**Purpose:** Complete project folder structure and organization guide for enhanced architecture

---

## Repository Structure

```
fantasy-basketball-analyzer/
├── backend/                          # Python FastAPI backend
│   ├── app/                         # Main application code
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI application entry point
│   │   ├── config.py                # Configuration management
│   │   ├── database.py              # Database connection and session
│   │   │
│   │   ├── api/                     # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── v1/                  # API version 1
│   │   │   │   ├── __init__.py
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── auth.py              # Authentication endpoints
│   │   │   │   │   ├── players.py           # Player endpoints
│   │   │   │   │   ├── predictions.py       # Prediction endpoints
│   │   │   │   │   ├── rankings.py          # Rankings endpoints
│   │   │   │   │   ├── teams.py             # Team endpoints
│   │   │   │   │   ├── matchups.py          # Matchup endpoints
│   │   │   │   │   ├── recommendations.py   # Recommendation endpoints
│   │   │   │   │   ├── yahoo.py             # Yahoo API integration
│   │   │   │   │   ├── injuries.py          # Injury tracking endpoints (NEW)
│   │   │   │   │   ├── notifications.py     # Notification preferences (NEW)
│   │   │   │   │   └── export.py            # Data export endpoints (NEW)
│   │   │   │   ├── dependencies.py      # Shared dependencies
│   │   │   │   └── router.py            # Main API router
│   │   │   │
│   │   │   ├── v2/                  # API version 2 (GraphQL) (NEW)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schema.py            # GraphQL schema
│   │   │   │   ├── resolvers/
│   │   │   │   │   ├── player_resolver.py
│   │   │   │   │   ├── prediction_resolver.py
│   │   │   │   │   └── matchup_resolver.py
│   │   │   │   └── router.py
│   │   │   │
│   │   │   └── gateway/             # API Gateway (NEW)
│   │   │       ├── __init__.py
│   │   │       ├── rate_limiter.py      # Rate limiting logic
│   │   │       ├── request_validator.py # Request validation
│   │   │       └── response_transformer.py
│   │   │
│   │   ├── models/                  # SQLAlchemy models (database tables)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── player.py
│   │   │   ├── team.py
│   │   │   ├── game_stats.py
│   │   │   ├── prediction.py
│   │   │   ├── league.py
│   │   │   ├── roster.py
│   │   │   ├── matchup.py
│   │   │   ├── recommendation.py
│   │   │   ├── injury.py                # Injury tracking (NEW)
│   │   │   ├── notification.py          # Notification preferences (NEW)
│   │   │   ├── scoring_settings.py      # Points league settings (NEW)
│   │   │   ├── token_blacklist.py       # JWT token blacklist (NEW)
│   │   │   ├── audit_log.py             # Audit logging (NEW)
│   │   │   └── feature_store.py         # ML feature metadata (NEW)
│   │   │
│   │   ├── schemas/                 # Pydantic schemas (API request/response)
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── player.py
│   │   │   ├── prediction.py
│   │   │   ├── team.py
│   │   │   ├── matchup.py
│   │   │   ├── recommendation.py
│   │   │   ├── injury.py                # Injury schemas (NEW)
│   │   │   ├── notification.py          # Notification schemas (NEW)
│   │   │   ├── websocket.py             # WebSocket message schemas (NEW)
│   │   │   └── export.py                # Export format schemas (NEW)
│   │   │
│   │   ├── services/                # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── nba_ingestion_service.py      # NBA API data fetching
│   │   │   ├── prediction_service.py         # ML prediction generation
│   │   │   ├── recommendation_service.py     # AI recommendations
│   │   │   ├── yahoo_service.py              # Yahoo API integration
│   │   │   ├── z_score_service.py            # Z-score calculations
│   │   │   ├── evaluation_service.py         # Model evaluation
│   │   │   ├── injury_service.py             # Injury monitoring (NEW)
│   │   │   ├── notification_service.py       # Push/Email notifications (NEW)
│   │   │   ├── websocket_service.py          # WebSocket management (NEW)
│   │   │   ├── data_failover_service.py      # Data source failover (NEW)
│   │   │   ├── token_service.py              # Token refresh/revocation (NEW)
│   │   │   ├── export_service.py             # Data export service (NEW)
│   │   │   └── cache_service.py              # Advanced caching (NEW)
│   │   │
│   │   ├── ml/                      # Machine learning components
│   │   │   ├── __init__.py
│   │   │   ├── models/              # ML model files
│   │   │   │   ├── __init__.py
│   │   │   │   └── registry/        # MLflow model registry (NEW)
│   │   │   │       ├── production/
│   │   │   │       ├── staging/
│   │   │   │       └── archive/
│   │   │   │
│   │   │   ├── ensemble/            # Ensemble models (NEW)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── xgboost_model.py
│   │   │   │   ├── lightgbm_model.py
│   │   │   │   ├── lstm_model.py        # Sequence predictions
│   │   │   │   └── ensemble_predictor.py
│   │   │   │
│   │   │   ├── feature_store/       # Feast feature store (NEW)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── feature_definitions.py
│   │   │   │   ├── feature_views.py
│   │   │   │   └── offline_store.py
│   │   │   │
│   │   │   ├── training/            # Model training (NEW)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── trainer.py
│   │   │   │   ├── hyperparameter_tuning.py
│   │   │   │   ├── cross_validation.py
│   │   │   │   └── backtesting.py       # Walk-forward validation
│   │   │   │
│   │   │   ├── inference/           # Prediction inference (NEW)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── predictor.py
│   │   │   │   ├── confidence_calculator.py
│   │   │   │   └── batch_predictor.py
│   │   │   │
│   │   │   ├── monitoring/          # Model monitoring (NEW)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── drift_detector.py
│   │   │   │   ├── performance_tracker.py
│   │   │   │   └── alerting.py
│   │   │   │
│   │   │   ├── feature_engineering.py   # Feature creation
│   │   │   └── evaluator.py             # Model evaluation
│   │   │
│   │   ├── websocket/               # WebSocket server (NEW)
│   │   │   ├── __init__.py
│   │   │   ├── connection_manager.py    # Connection handling
│   │   │   ├── handlers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── injury_handler.py    # Real-time injury updates
│   │   │   │   ├── score_handler.py     # Live game scores
│   │   │   │   ├── prediction_handler.py # Prediction updates
│   │   │   │   └── lineup_handler.py    # Lineup lock alerts
│   │   │   ├── subscriptions.py         # Subscription management
│   │   │   └── broadcaster.py           # Message broadcasting
│   │   │
│   │   ├── data_sources/            # Data source integrations (NEW)
│   │   │   ├── __init__.py
│   │   │   ├── base_source.py           # Abstract base class
│   │   │   ├── nba_api_source.py        # Primary: NBA API
│   │   │   ├── espn_source.py           # Fallback 1: ESPN API
│   │   │   ├── bbref_source.py          # Fallback 2: Basketball Reference
│   │   │   ├── twitter_source.py        # Injury feeds
│   │   │   ├── rotoworld_source.py      # News feeds
│   │   │   ├── failover_manager.py      # Failover orchestration
│   │   │   └── circuit_breaker.py       # Circuit breaker pattern
│   │   │
│   │   ├── notifications/           # Notification system (NEW)
│   │   │   ├── __init__.py
│   │   │   ├── push_service.py          # Firebase Cloud Messaging
│   │   │   ├── email_service.py         # SendGrid/SES integration
│   │   │   ├── sms_service.py           # Twilio integration
│   │   │   ├── in_app_service.py        # In-app notifications
│   │   │   └── notification_router.py   # Route to appropriate channel
│   │   │
│   │   ├── core/                    # Core utilities
│   │   │   ├── __init__.py
│   │   │   ├── security.py              # JWT, password hashing
│   │   │   ├── cache.py                 # Redis caching utilities
│   │   │   ├── exceptions.py            # Custom exceptions
│   │   │   ├── logging.py               # Logging configuration
│   │   │   ├── encryption.py            # Data encryption (NEW)
│   │   │   ├── middleware.py            # Custom middleware (NEW)
│   │   │   └── rate_limiting.py         # Rate limiting (NEW)
│   │   │
│   │   └── utils/                   # Helper utilities
│   │       ├── __init__.py
│   │       ├── date_utils.py
│   │       ├── validators.py
│   │       ├── constants.py
│   │       ├── metrics.py               # Prometheus metrics (NEW)
│   │       └── health_checks.py         # Health check utilities (NEW)
│   │
│   ├── alembic/                     # Database migrations
│   │   ├── versions/                # Migration files
│   │   ├── env.py
│   │   └── script.py.mako
│   │
│   ├── tasks/                       # Celery background tasks
│   │   ├── __init__.py
│   │   ├── celery_app.py            # Celery configuration
│   │   ├── nba_tasks.py             # NBA data ingestion tasks
│   │   ├── prediction_tasks.py      # Prediction generation tasks
│   │   ├── yahoo_tasks.py           # Yahoo sync tasks
│   │   ├── evaluation_tasks.py      # Model evaluation tasks
│   │   ├── injury_tasks.py          # Injury monitoring tasks (NEW)
│   │   ├── notification_tasks.py    # Notification dispatch tasks (NEW)
│   │   ├── training_tasks.py        # Model retraining tasks (NEW)
│   │   └── cleanup_tasks.py         # Data cleanup tasks (NEW)
│   │
│   ├── kafka/                       # Kafka event streaming (NEW)
│   │   ├── __init__.py
│   │   ├── producer.py              # Event producer
│   │   ├── consumer.py              # Event consumer
│   │   ├── topics.py                # Topic definitions
│   │   └── handlers/
│   │       ├── injury_event_handler.py
│   │       ├── game_event_handler.py
│   │       └── prediction_event_handler.py
│   │
│   ├── tests/                       # Test suite
│   │   ├── __init__.py
│   │   ├── conftest.py              # Pytest fixtures
│   │   ├── unit/                    # Unit tests
│   │   │   ├── test_auth.py
│   │   │   ├── test_predictions.py
│   │   │   ├── test_z_scores.py
│   │   │   ├── test_recommendations.py
│   │   │   ├── test_injury_service.py       # NEW
│   │   │   ├── test_notification_service.py # NEW
│   │   │   ├── test_failover_service.py     # NEW
│   │   │   └── test_ensemble_models.py      # NEW
│   │   ├── integration/             # Integration tests
│   │   │   ├── test_api_endpoints.py
│   │   │   ├── test_nba_ingestion.py
│   │   │   ├── test_yahoo_integration.py
│   │   │   ├── test_websocket.py            # NEW
│   │   │   ├── test_kafka_events.py         # NEW
│   │   │   └── test_data_failover.py        # NEW
│   │   ├── e2e/                     # End-to-end tests
│   │   │   └── test_user_flows.py
│   │   ├── ml/                      # ML-specific tests (NEW)
│   │   │   ├── test_backtesting.py
│   │   │   ├── test_feature_engineering.py
│   │   │   └── test_drift_detection.py
│   │   └── performance/             # Performance tests (NEW)
│   │       ├── test_api_latency.py
│   │       ├── test_prediction_throughput.py
│   │       └── test_concurrent_users.py
│   │
│   ├── scripts/                     # Utility scripts
│   │   ├── seed_nba_data.py         # Seed database with NBA data
│   │   ├── train_models.py          # Train ML models
│   │   ├── init_db.sql              # Database initialization
│   │   ├── backup_db.sh             # Database backup script
│   │   ├── migrate_data.py          # Data migration utilities (NEW)
│   │   ├── benchmark_models.py      # Model performance benchmarking (NEW)
│   │   ├── export_metrics.py        # Export prediction metrics (NEW)
│   │   └── health_check.py          # System health verification (NEW)
│   │
│   ├── mlflow/                      # MLflow configuration (NEW)
│   │   ├── mlflow_config.py
│   │   ├── tracking_server.py
│   │   └── model_registry.py
│   │
│   ├── feast/                       # Feast feature store (NEW)
│   │   ├── feature_repo/
│   │   │   ├── features.py
│   │   │   └── feature_store.yaml
│   │   └── materialize.py
│   │
│   ├── .env.example                 # Example environment variables
│   ├── .gitignore
│   ├── alembic.ini                  # Alembic configuration
│   ├── requirements.txt             # Python dependencies
│   ├── requirements-dev.txt         # Development dependencies
│   ├── requirements-ml.txt          # ML-specific dependencies (NEW)
│   ├── Dockerfile                   # Docker configuration
│   ├── Dockerfile.ml                # ML service Dockerfile (NEW)
│   ├── docker-compose.yml           # Local development setup
│   ├── docker-compose.prod.yml      # Production setup (NEW)
│   ├── railway.toml                 # Railway deployment config
│   ├── pyproject.toml               # Python project configuration
│   ├── pytest.ini                   # Pytest configuration
│   ├── prometheus.yml               # Prometheus config (NEW)
│   └── README.md                    # Backend documentation
│
├── frontend/                        # React/Next.js frontend
│   ├── app/                         # Next.js app directory
│   │   ├── (auth)/                  # Authentication routes
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   ├── register/
│   │   │   │   └── page.tsx
│   │   │   ├── forgot-password/     # NEW
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx
│   │   │
│   │   ├── (dashboard)/             # Protected dashboard routes
│   │   │   ├── page.tsx             # Dashboard home
│   │   │   ├── players/             # Player pages
│   │   │   │   ├── page.tsx                 # Player search
│   │   │   │   └── [playerId]/
│   │   │   │       ├── page.tsx             # Player profile
│   │   │   │       ├── stats/
│   │   │   │       │   └── page.tsx
│   │   │   │       └── predictions/
│   │   │   │           └── page.tsx
│   │   │   │
│   │   │   ├── teams/               # Team pages
│   │   │   │   ├── page.tsx                 # Teams list
│   │   │   │   └── [teamId]/
│   │   │   │       ├── page.tsx             # Team overview
│   │   │   │       ├── roster/
│   │   │   │       │   └── page.tsx
│   │   │   │       ├── matchup/
│   │   │   │       │   └── page.tsx
│   │   │   │       └── recommendations/
│   │   │   │           └── page.tsx
│   │   │   │
│   │   │   ├── predictions/         # Predictions pages
│   │   │   │   ├── page.tsx                 # Daily predictions
│   │   │   │   └── accuracy/
│   │   │   │       └── page.tsx
│   │   │   │
│   │   │   ├── rankings/            # Rankings pages
│   │   │   │   ├── page.tsx
│   │   │   │   └── custom/          # Custom rankings (NEW)
│   │   │   │       └── page.tsx
│   │   │   │
│   │   │   ├── injuries/            # Injury tracking (NEW)
│   │   │   │   ├── page.tsx
│   │   │   │   └── alerts/
│   │   │   │       └── page.tsx
│   │   │   │
│   │   │   ├── trade/               # Trade analyzer (NEW)
│   │   │   │   ├── page.tsx
│   │   │   │   └── simulator/
│   │   │   │       └── page.tsx
│   │   │   │
│   │   │   ├── streaming/           # Streaming tool (NEW)
│   │   │   │   └── page.tsx
│   │   │   │
│   │   │   ├── settings/            # User settings (NEW)
│   │   │   │   ├── page.tsx
│   │   │   │   ├── notifications/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── league/
│   │   │   │       └── page.tsx
│   │   │   │
│   │   │   └── layout.tsx           # Dashboard layout
│   │   │
│   │   ├── api/                     # API routes (if needed)
│   │   │   ├── route.ts
│   │   │   └── websocket/           # WebSocket proxy (NEW)
│   │   │       └── route.ts
│   │   │
│   │   ├── layout.tsx               # Root layout
│   │   ├── page.tsx                 # Landing page
│   │   ├── manifest.json            # PWA manifest (NEW)
│   │   ├── sw.ts                    # Service worker (NEW)
│   │   └── globals.css              # Global styles
│   │
│   ├── components/                  # React components
│   │   ├── ui/                      # Base UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Table.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Skeleton.tsx
│   │   │   ├── Toast.tsx            # NEW
│   │   │   ├── Badge.tsx            # NEW
│   │   │   ├── Tabs.tsx             # NEW
│   │   │   └── Drawer.tsx           # Mobile drawer (NEW)
│   │   │
│   │   ├── layout/                  # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Navigation.tsx
│   │   │   ├── MobileNav.tsx        # Mobile navigation (NEW)
│   │   │   └── BottomNav.tsx        # Mobile bottom nav (NEW)
│   │   │
│   │   ├── players/                 # Player-specific components
│   │   │   ├── PlayerCard.tsx
│   │   │   ├── PlayerSearch.tsx
│   │   │   ├── PlayerStats.tsx
│   │   │   ├── PlayerPredictions.tsx
│   │   │   └── PlayerComparison.tsx # NEW
│   │   │
│   │   ├── teams/                   # Team-specific components
│   │   │   ├── TeamCard.tsx
│   │   │   ├── RosterTable.tsx
│   │   │   ├── MatchupAnalysis.tsx
│   │   │   └── LineupOptimizer.tsx  # NEW
│   │   │
│   │   ├── predictions/             # Prediction components
│   │   │   ├── PredictionCard.tsx
│   │   │   ├── DailyPredictions.tsx
│   │   │   ├── AccuracyTracker.tsx
│   │   │   └── ConfidenceIndicator.tsx # NEW
│   │   │
│   │   ├── recommendations/         # Recommendation components
│   │   │   ├── StartSitCard.tsx
│   │   │   ├── WaiverTargets.tsx
│   │   │   └── TradeAnalyzer.tsx
│   │   │
│   │   ├── injuries/                # Injury components (NEW)
│   │   │   ├── InjuryAlert.tsx
│   │   │   ├── InjuryTimeline.tsx
│   │   │   └── InjuryImpact.tsx
│   │   │
│   │   ├── realtime/                # Real-time components (NEW)
│   │   │   ├── LiveScores.tsx
│   │   │   ├── LiveUpdates.tsx
│   │   │   ├── ConnectionStatus.tsx
│   │   │   └── NotificationBell.tsx
│   │   │
│   │   ├── charts/                  # Data visualization (NEW)
│   │   │   ├── LineChart.tsx
│   │   │   ├── BarChart.tsx
│   │   │   ├── RadarChart.tsx
│   │   │   └── TrendChart.tsx
│   │   │
│   │   ├── mobile/                  # Mobile-specific components (NEW)
│   │   │   ├── SwipeableCard.tsx
│   │   │   ├── PullToRefresh.tsx
│   │   │   └── TouchCarousel.tsx
│   │   │
│   │   └── common/                  # Shared components
│   │       ├── ErrorBoundary.tsx
│   │       ├── LoadingSpinner.tsx
│   │       ├── ErrorMessage.tsx
│   │       ├── EmptyState.tsx
│   │       ├── OfflineIndicator.tsx # NEW
│   │       └── InstallPrompt.tsx    # PWA install (NEW)
│   │
│   ├── hooks/                       # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── usePlayerStats.ts
│   │   ├── usePredictions.ts
│   │   ├── useRecommendations.ts
│   │   ├── useMatchup.ts
│   │   ├── useYahooAuth.ts
│   │   ├── useWebSocket.ts          # WebSocket connection (NEW)
│   │   ├── useNotifications.ts      # Push notifications (NEW)
│   │   ├── useOffline.ts            # Offline detection (NEW)
│   │   ├── useSwipe.ts              # Touch gestures (NEW)
│   │   └── usePWA.ts                # PWA utilities (NEW)
│   │
│   ├── lib/                         # Libraries and utilities
│   │   ├── api-client.ts            # Axios configuration
│   │   ├── react-query-client.ts
│   │   ├── websocket-client.ts      # WebSocket client (NEW)
│   │   ├── push-notifications.ts    # Push notification setup (NEW)
│   │   ├── offline-storage.ts       # IndexedDB wrapper (NEW)
│   │   ├── utils.ts                 # Helper functions
│   │   └── constants.ts
│   │
│   ├── types/                       # TypeScript type definitions
│   │   ├── api.ts                   # API response types
│   │   ├── models.ts                # Data model types
│   │   ├── websocket.ts             # WebSocket message types (NEW)
│   │   └── index.ts
│   │
│   ├── store/                       # State management
│   │   ├── useAppStore.ts
│   │   ├── useTeamStore.ts
│   │   ├── useNotificationStore.ts  # NEW
│   │   └── useOfflineStore.ts       # NEW
│   │
│   ├── workers/                     # Web workers (NEW)
│   │   ├── sw.ts                    # Service worker
│   │   ├── prediction-worker.ts     # Background predictions
│   │   └── sync-worker.ts           # Background sync
│   │
│   ├── public/                      # Static assets
│   │   ├── images/
│   │   ├── icons/
│   │   │   ├── icon-72x72.png       # PWA icons (NEW)
│   │   │   ├── icon-96x96.png
│   │   │   ├── icon-128x128.png
│   │   │   ├── icon-144x144.png
│   │   │   ├── icon-152x152.png
│   │   │   ├── icon-192x192.png
│   │   │   ├── icon-384x384.png
│   │   │   └── icon-512x512.png
│   │   └── favicon.ico
│   │
│   ├── .env.example
│   ├── .env.local
│   ├── .gitignore
│   ├── next.config.js
│   ├── next-pwa.config.js           # PWA configuration (NEW)
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── README.md
│
├── infrastructure/                  # Infrastructure as Code (NEW)
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── modules/
│   │   │   ├── eks/
│   │   │   ├── rds/
│   │   │   ├── elasticache/
│   │   │   └── msk/                 # Managed Kafka
│   │   └── environments/
│   │       ├── dev/
│   │       ├── staging/
│   │       └── prod/
│   │
│   ├── kubernetes/
│   │   ├── base/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   ├── ingress.yaml
│   │   │   ├── hpa.yaml             # Horizontal Pod Autoscaler
│   │   │   └── configmap.yaml
│   │   ├── overlays/
│   │   │   ├── dev/
│   │   │   ├── staging/
│   │   │   └── production/
│   │   └── helm/
│   │       └── fantasy-basketball/
│   │           ├── Chart.yaml
│   │           ├── values.yaml
│   │           └── templates/
│   │
│   └── ansible/
│       ├── playbooks/
│       │   ├── deploy.yaml
│       │   ├── rollback.yaml
│       │   └── maintenance.yaml
│       └── inventory/
│
├── monitoring/                      # Monitoring stack (NEW)
│   ├── grafana/
│   │   ├── dashboards/
│   │   │   ├── api-performance.json
│   │   │   ├── ml-metrics.json
│   │   │   ├── business-metrics.json
│   │   │   └── infrastructure.json
│   │   └── provisioning/
│   │
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   ├── alerts/
│   │   │   ├── api-alerts.yml
│   │   │   ├── ml-alerts.yml
│   │   │   └── infrastructure-alerts.yml
│   │   └── rules/
│   │
│   ├── alertmanager/
│   │   └── alertmanager.yml
│   │
│   └── logging/
│       ├── elasticsearch/
│       ├── logstash/
│       │   └── pipeline.conf
│       └── kibana/
│
├── docs/                            # Documentation
│   ├── TECHNICAL_SPECIFICATION.md
│   ├── LOVABLE_INTEGRATION_GUIDE.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── PROJECT_STRUCTURE.md
│   ├── API_DOCUMENTATION.md
│   ├── USER_GUIDE.md
│   ├── DATA_DICTIONARY.md           # NEW
│   ├── ERROR_CODES.md               # NEW
│   ├── RUNBOOK.md                   # NEW
│   └── ARCHITECTURE_DECISIONS.md    # ADR records (NEW)
│
├── .github/                         # GitHub configuration
│   ├── workflows/
│   │   ├── deploy.yml               # CI/CD pipeline
│   │   ├── test.yml                 # Test automation
│   │   ├── lint.yml                 # Code linting (NEW)
│   │   ├── security.yml             # Security scanning (NEW)
│   │   └── ml-training.yml          # ML pipeline (NEW)
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── CODEOWNERS                   # NEW
│   └── dependabot.yml               # NEW
│
├── .gitignore                       # Git ignore rules
├── .pre-commit-config.yaml          # Pre-commit hooks
├── docker-compose.yml               # Local development setup
├── docker-compose.prod.yml          # Production setup (NEW)
├── Makefile                         # Build automation (NEW)
├── LICENSE
└── README.md                        # Project overview
```

---

## New Component Details

### WebSocket Server Structure

```
websocket/
├── connection_manager.py    # Manages WebSocket connections
│   - ConnectionManager class with connect/disconnect methods
│   - User-to-connection mapping
│   - Connection health monitoring
│
├── handlers/                # Event-specific handlers
│   ├── injury_handler.py    # Processes injury updates
│   │   - Monitors Twitter feeds
│   │   - Parses injury reports
│   │   - Broadcasts to subscribed users
│   │
│   ├── score_handler.py     # Live game score updates
│   │   - Real-time box scores
│   │   - Fantasy point calculations
│   │
│   ├── prediction_handler.py # Prediction updates
│   │   - Recalculated predictions
│   │   - Confidence changes
│   │
│   └── lineup_handler.py    # Lineup lock alerts
│       - Lock time reminders
│       - Last-minute changes
│
├── subscriptions.py         # Topic subscription management
│   - Player subscriptions
│   - Team subscriptions
│   - League subscriptions
│
└── broadcaster.py           # Message distribution
    - Batch message sending
    - Priority message handling
```

### ML Pipeline Structure

```
ml/
├── ensemble/                # Ensemble model implementations
│   ├── xgboost_model.py
│   │   - Per-category XGBoost models
│   │   - Hyperparameter configuration
│   │   - SHAP explainability
│   │
│   ├── lightgbm_model.py
│   │   - LightGBM implementations
│   │   - Categorical feature handling
│   │
│   ├── lstm_model.py
│   │   - Sequence-based predictions
│   │   - Hot/cold streak detection
│   │   - Injury return projections
│   │
│   └── ensemble_predictor.py
│       - Model weight configuration
│       - Prediction aggregation
│       - Confidence calculation
│
├── feature_store/           # Feast feature management
│   ├── feature_definitions.py
│   │   - Entity definitions (player, team, game)
│   │   - Feature views
│   │   - Online/offline stores
│   │
│   └── feature_views.py
│       - Player features (rolling averages, trends)
│       - Team features (pace, defense rating)
│       - Matchup features (DvP ratings)
│
├── training/                # Model training pipeline
│   ├── trainer.py
│   │   - Training orchestration
│   │   - Cross-validation setup
│   │   - Early stopping
│   │
│   ├── hyperparameter_tuning.py
│   │   - Optuna integration
│   │   - Search space definitions
│   │   - Bayesian optimization
│   │
│   └── backtesting.py
│       - Walk-forward validation
│       - Out-of-sample testing
│       - Performance metrics
│
├── inference/               # Prediction serving
│   ├── predictor.py
│   │   - Single prediction serving
│   │   - Feature retrieval
│   │   - Model loading
│   │
│   ├── confidence_calculator.py
│   │   - Prediction intervals
│   │   - Uncertainty quantification
│   │
│   └── batch_predictor.py
│       - Bulk prediction generation
│       - Daily batch processing
│
└── monitoring/              # Model health monitoring
    ├── drift_detector.py
    │   - Feature drift detection
    │   - Prediction drift monitoring
    │   - Alert generation
    │
    ├── performance_tracker.py
    │   - Accuracy metrics
    │   - Category-wise performance
    │   - A/B test tracking
    │
    └── alerting.py
        - Performance degradation alerts
        - Retraining triggers
```

### Data Source Failover Structure

```
data_sources/
├── base_source.py           # Abstract base class
│   class DataSource:
│       @abstractmethod
│       def fetch_player_stats()
│       @abstractmethod
│       def fetch_game_log()
│       @abstractmethod
│       def health_check()
│
├── nba_api_source.py        # Primary source
│   - Official NBA API integration
│   - Rate limiting handling
│   - Response parsing
│
├── espn_source.py           # Fallback 1
│   - ESPN API integration
│   - Data format normalization
│
├── bbref_source.py          # Fallback 2
│   - Basketball Reference scraping
│   - Selenium integration
│
├── failover_manager.py      # Orchestration
│   class FailoverManager:
│       - Source priority ordering
│       - Health monitoring
│       - Automatic failover
│       - Recovery detection
│
└── circuit_breaker.py       # Resilience pattern
    class CircuitBreaker:
        - CLOSED/OPEN/HALF_OPEN states
        - Failure threshold tracking
        - Recovery attempts
```

### Notification System Structure

```
notifications/
├── push_service.py          # Firebase Cloud Messaging
│   - Device token management
│   - Topic subscriptions
│   - Message formatting
│
├── email_service.py         # Email notifications
│   - SendGrid/SES integration
│   - Template management
│   - Batch sending
│
├── sms_service.py           # SMS notifications
│   - Twilio integration
│   - Rate limiting
│   - Cost management
│
├── in_app_service.py        # In-app notifications
│   - WebSocket delivery
│   - Notification storage
│   - Read status tracking
│
└── notification_router.py   # Channel selection
    - User preference lookup
    - Priority-based routing
    - Fallback channels
```

---

## File Templates

### Backend: `main.py` (Enhanced)

```python
"""
FastAPI application entry point with WebSocket support.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import settings
from app.core.logging import setup_logging
from app.database import engine
from app.api.v1.router import api_router
from app.api.v2.router import graphql_router
from app.websocket.connection_manager import connection_manager
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    setup_logging()
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    await connection_manager.disconnect_all()


# Initialize Sentry (error tracking)
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
        environment=settings.ENVIRONMENT,
    )

# Initialize FastAPI app
app = FastAPI(
    title="Fantasy Basketball Analyzer API",
    description="AI-powered fantasy basketball statistics and predictions",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(graphql_router, prefix="/api/v2")


# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket connection handler."""
    await connection_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            await connection_manager.handle_message(user_id, data)
    except WebSocketDisconnect:
        connection_manager.disconnect(user_id)


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Fantasy Basketball Analyzer API",
        "version": "2.0.0",
        "docs": "/docs",
        "graphql": "/api/v2/graphql",
        "health": "/health",
        "metrics": "/metrics",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
```

### Backend: `config.py` (Enhanced)

```python
"""
Application configuration management with enhanced settings.
"""

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30

    # Redis
    REDIS_URL: str
    REDIS_MAX_CONNECTIONS: int = 50

    # Security
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Encryption
    ENCRYPTION_KEY: str

    # Yahoo OAuth
    YAHOO_CLIENT_ID: str
    YAHOO_CLIENT_SECRET: str
    YAHOO_REDIRECT_URI: str

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://app.yourdomain.com",
    ]

    # Rate Limiting
    RATE_LIMIT_FREE_TIER: int = 100  # requests per hour
    RATE_LIMIT_PREMIUM_TIER: int = 1000
    RATE_LIMIT_ENTERPRISE_TIER: int = 10000

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 10000

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_CONSUMER_GROUP: str = "fantasy-basketball"

    # Notifications
    FIREBASE_CREDENTIALS_PATH: str = ""
    SENDGRID_API_KEY: str = ""
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""

    # ML Configuration
    MLFLOW_TRACKING_URI: str = "mlruns"
    FEAST_REPO_PATH: str = "feast/feature_repo"
    MODEL_REGISTRY_PATH: str = "ml/models/registry"

    # Data Sources
    ESPN_API_KEY: str = ""
    TWITTER_BEARER_TOKEN: str = ""

    # Circuit Breaker
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = 60

    # Monitoring
    SENTRY_DSN: str | None = None
    PROMETHEUS_ENABLED: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
```

### Backend: WebSocket Connection Manager

```python
"""
WebSocket connection management with subscription support.
"""

from fastapi import WebSocket
from typing import Dict, Set, Optional
import asyncio
import json
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections and subscriptions."""

    def __init__(self):
        # user_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # topic -> set of user_ids
        self.subscriptions: Dict[str, Set[str]] = {}
        # user_id -> set of topics
        self.user_subscriptions: Dict[str, Set[str]] = {}
        # Connection health tracking
        self.last_heartbeat: Dict[str, datetime] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_subscriptions[user_id] = set()
        self.last_heartbeat[user_id] = datetime.utcnow()

        # Send connection confirmation
        await self.send_personal_message(
            user_id,
            {"type": "connected", "user_id": user_id}
        )

    def disconnect(self, user_id: str):
        """Remove a WebSocket connection."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

        # Clean up subscriptions
        if user_id in self.user_subscriptions:
            for topic in self.user_subscriptions[user_id]:
                if topic in self.subscriptions:
                    self.subscriptions[topic].discard(user_id)
            del self.user_subscriptions[user_id]

        if user_id in self.last_heartbeat:
            del self.last_heartbeat[user_id]

    async def disconnect_all(self):
        """Disconnect all connections gracefully."""
        for user_id in list(self.active_connections.keys()):
            try:
                await self.active_connections[user_id].close()
            except Exception:
                pass
            self.disconnect(user_id)

    def subscribe(self, user_id: str, topic: str):
        """Subscribe a user to a topic."""
        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()
        self.subscriptions[topic].add(user_id)

        if user_id in self.user_subscriptions:
            self.user_subscriptions[user_id].add(topic)

    def unsubscribe(self, user_id: str, topic: str):
        """Unsubscribe a user from a topic."""
        if topic in self.subscriptions:
            self.subscriptions[topic].discard(user_id)

        if user_id in self.user_subscriptions:
            self.user_subscriptions[user_id].discard(topic)

    async def send_personal_message(self, user_id: str, message: dict):
        """Send a message to a specific user."""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception:
                self.disconnect(user_id)

    async def broadcast_to_topic(self, topic: str, message: dict):
        """Broadcast a message to all subscribers of a topic."""
        if topic not in self.subscriptions:
            return

        disconnected = []
        for user_id in self.subscriptions[topic]:
            if user_id in self.active_connections:
                try:
                    await self.active_connections[user_id].send_json(message)
                except Exception:
                    disconnected.append(user_id)

        # Clean up disconnected users
        for user_id in disconnected:
            self.disconnect(user_id)

    async def broadcast_all(self, message: dict):
        """Broadcast a message to all connected users."""
        disconnected = []
        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(user_id)

        for user_id in disconnected:
            self.disconnect(user_id)

    async def handle_message(self, user_id: str, data: dict):
        """Handle incoming WebSocket messages."""
        message_type = data.get("type")

        if message_type == "subscribe":
            topic = data.get("topic")
            if topic:
                self.subscribe(user_id, topic)
                await self.send_personal_message(
                    user_id,
                    {"type": "subscribed", "topic": topic}
                )

        elif message_type == "unsubscribe":
            topic = data.get("topic")
            if topic:
                self.unsubscribe(user_id, topic)
                await self.send_personal_message(
                    user_id,
                    {"type": "unsubscribed", "topic": topic}
                )

        elif message_type == "heartbeat":
            self.last_heartbeat[user_id] = datetime.utcnow()
            await self.send_personal_message(
                user_id,
                {"type": "heartbeat_ack"}
            )

    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)

    def get_subscription_count(self, topic: str) -> int:
        """Get the number of subscribers for a topic."""
        return len(self.subscriptions.get(topic, set()))


# Global connection manager instance
connection_manager = ConnectionManager()
```

### Backend: Ensemble Predictor

```python
"""
Ensemble model predictor combining XGBoost, LightGBM, and LSTM.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass
import mlflow
from app.core.config import settings


@dataclass
class PredictionResult:
    """Prediction result with confidence intervals."""
    predicted_value: float
    lower_bound: float
    upper_bound: float
    confidence: float
    model_contributions: Dict[str, float]


class EnsemblePredictor:
    """Ensemble predictor combining multiple models."""

    def __init__(self):
        self.models: Dict[str, Dict] = {}
        self.weights = {
            "xgboost": 0.45,
            "lightgbm": 0.35,
            "lstm": 0.20,
        }
        self.categories = [
            "points", "rebounds", "assists", "steals",
            "blocks", "threes", "fg_pct", "ft_pct", "turnovers"
        ]

    def load_models(self, version: str = "production"):
        """Load models from MLflow registry."""
        for category in self.categories:
            self.models[category] = {}
            for model_type in ["xgboost", "lightgbm"]:
                model_name = f"{category}_{model_type}"
                try:
                    model = mlflow.pyfunc.load_model(
                        f"models:/{model_name}/{version}"
                    )
                    self.models[category][model_type] = model
                except Exception as e:
                    print(f"Failed to load {model_name}: {e}")

    def predict(
        self,
        player_id: int,
        features: Dict[str, float],
        category: str,
    ) -> PredictionResult:
        """Generate ensemble prediction for a category."""
        if category not in self.models:
            raise ValueError(f"Unknown category: {category}")

        predictions = {}
        feature_array = self._prepare_features(features)

        # Get predictions from each model
        for model_type, model in self.models[category].items():
            if model is not None:
                try:
                    pred = model.predict(feature_array)[0]
                    predictions[model_type] = pred
                except Exception:
                    continue

        if not predictions:
            raise RuntimeError(f"No models available for {category}")

        # Calculate weighted ensemble prediction
        weighted_sum = 0.0
        total_weight = 0.0
        contributions = {}

        for model_type, pred in predictions.items():
            weight = self.weights.get(model_type, 0.0)
            weighted_sum += pred * weight
            total_weight += weight
            contributions[model_type] = pred

        predicted_value = weighted_sum / total_weight if total_weight > 0 else 0.0

        # Calculate confidence intervals using prediction variance
        pred_values = list(predictions.values())
        std_dev = np.std(pred_values) if len(pred_values) > 1 else 0.0

        # 90% confidence interval
        z_score = 1.645
        margin = z_score * std_dev

        # Calculate confidence score based on model agreement
        cv = std_dev / abs(predicted_value) if predicted_value != 0 else 1.0
        confidence = max(0.0, min(1.0, 1.0 - cv))

        return PredictionResult(
            predicted_value=round(predicted_value, 2),
            lower_bound=round(max(0, predicted_value - margin), 2),
            upper_bound=round(predicted_value + margin, 2),
            confidence=round(confidence, 3),
            model_contributions=contributions,
        )

    def predict_all_categories(
        self,
        player_id: int,
        features: Dict[str, float],
    ) -> Dict[str, PredictionResult]:
        """Generate predictions for all categories."""
        results = {}
        for category in self.categories:
            try:
                results[category] = self.predict(player_id, features, category)
            except Exception as e:
                print(f"Prediction failed for {category}: {e}")
        return results

    def _prepare_features(self, features: Dict[str, float]) -> np.ndarray:
        """Prepare feature array for model input."""
        feature_order = [
            "rolling_avg_5", "rolling_avg_10", "rolling_avg_20",
            "opponent_def_rating", "home_away", "rest_days",
            "minutes_avg", "usage_rate", "pace_factor",
            "injury_history", "back_to_back", "travel_distance",
        ]
        return np.array([[features.get(f, 0.0) for f in feature_order]])

    def update_weights(self, new_weights: Dict[str, float]):
        """Update model weights based on recent performance."""
        total = sum(new_weights.values())
        self.weights = {k: v / total for k, v in new_weights.items()}


# Global ensemble predictor instance
ensemble_predictor = EnsemblePredictor()
```

### Frontend: WebSocket Hook

```typescript
// hooks/useWebSocket.ts

import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuth } from './useAuth';

interface WebSocketMessage {
  type: string;
  topic?: string;
  data?: any;
}

interface UseWebSocketOptions {
  autoReconnect?: boolean;
  reconnectInterval?: number;
  heartbeatInterval?: number;
}

export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const {
    autoReconnect = true,
    reconnectInterval = 5000,
    heartbeatInterval = 30000,
  } = options;

  const { user, accessToken } = useAuth();
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const heartbeatIntervalRef = useRef<NodeJS.Timeout>();

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  // Message handlers for different types
  const messageHandlers = useRef<Map<string, Set<(data: any) => void>>>(
    new Map()
  );

  const connect = useCallback(() => {
    if (!user?.id || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL}/ws/${user.id}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setIsConnected(true);
      setConnectionError(null);

      // Start heartbeat
      heartbeatIntervalRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'heartbeat' }));
        }
      }, heartbeatInterval);
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        setLastMessage(message);

        // Call registered handlers
        const handlers = messageHandlers.current.get(message.type);
        if (handlers) {
          handlers.forEach((handler) => handler(message.data));
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      clearInterval(heartbeatIntervalRef.current);

      if (autoReconnect) {
        reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval);
      }
    };

    ws.onerror = (error) => {
      setConnectionError('WebSocket connection error');
      console.error('WebSocket error:', error);
    };

    wsRef.current = ws;
  }, [user?.id, autoReconnect, reconnectInterval, heartbeatInterval]);

  const disconnect = useCallback(() => {
    clearTimeout(reconnectTimeoutRef.current);
    clearInterval(heartbeatIntervalRef.current);

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const subscribe = useCallback((topic: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'subscribe', topic }));
    }
  }, []);

  const unsubscribe = useCallback((topic: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'unsubscribe', topic }));
    }
  }, []);

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  const addMessageHandler = useCallback(
    (type: string, handler: (data: any) => void) => {
      if (!messageHandlers.current.has(type)) {
        messageHandlers.current.set(type, new Set());
      }
      messageHandlers.current.get(type)!.add(handler);

      // Return cleanup function
      return () => {
        messageHandlers.current.get(type)?.delete(handler);
      };
    },
    []
  );

  // Connect on mount
  useEffect(() => {
    if (user?.id) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [user?.id, connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    connectionError,
    subscribe,
    unsubscribe,
    sendMessage,
    addMessageHandler,
    connect,
    disconnect,
  };
};
```

### Frontend: Push Notifications Hook

```typescript
// hooks/useNotifications.ts

import { useEffect, useState, useCallback } from 'react';
import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, onMessage, Messaging } from 'firebase/messaging';
import apiClient from '@/lib/api-client';

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

interface NotificationPreferences {
  injuries: boolean;
  lineupLocks: boolean;
  predictions: boolean;
  matchupAlerts: boolean;
  tradeAlerts: boolean;
}

export const useNotifications = () => {
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [token, setToken] = useState<string | null>(null);
  const [messaging, setMessaging] = useState<Messaging | null>(null);
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    injuries: true,
    lineupLocks: true,
    predictions: false,
    matchupAlerts: true,
    tradeAlerts: false,
  });

  // Initialize Firebase
  useEffect(() => {
    if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
      const app = initializeApp(firebaseConfig);
      const messagingInstance = getMessaging(app);
      setMessaging(messagingInstance);

      // Listen for foreground messages
      onMessage(messagingInstance, (payload) => {
        console.log('Foreground message:', payload);

        // Show notification using Notification API
        if (Notification.permission === 'granted' && payload.notification) {
          new Notification(payload.notification.title || 'New notification', {
            body: payload.notification.body,
            icon: '/icons/icon-192x192.png',
          });
        }
      });
    }
  }, []);

  const requestPermission = useCallback(async () => {
    if (!messaging) return false;

    try {
      const result = await Notification.requestPermission();
      setPermission(result);

      if (result === 'granted') {
        const fcmToken = await getToken(messaging, {
          vapidKey: process.env.NEXT_PUBLIC_FIREBASE_VAPID_KEY,
        });

        if (fcmToken) {
          setToken(fcmToken);

          // Register token with backend
          await apiClient.post('/api/v1/notifications/register-device', {
            token: fcmToken,
            platform: 'web',
          });

          return true;
        }
      }

      return false;
    } catch (error) {
      console.error('Failed to get notification permission:', error);
      return false;
    }
  }, [messaging]);

  const updatePreferences = useCallback(
    async (newPreferences: Partial<NotificationPreferences>) => {
      try {
        const updated = { ...preferences, ...newPreferences };

        await apiClient.put('/api/v1/notifications/preferences', updated);
        setPreferences(updated);

        return true;
      } catch (error) {
        console.error('Failed to update notification preferences:', error);
        return false;
      }
    },
    [preferences]
  );

  const subscribeToPlayer = useCallback(
    async (playerId: number) => {
      try {
        await apiClient.post(`/api/v1/notifications/subscribe/player/${playerId}`);
        return true;
      } catch (error) {
        console.error('Failed to subscribe to player:', error);
        return false;
      }
    },
    []
  );

  const unsubscribeFromPlayer = useCallback(
    async (playerId: number) => {
      try {
        await apiClient.delete(`/api/v1/notifications/subscribe/player/${playerId}`);
        return true;
      } catch (error) {
        console.error('Failed to unsubscribe from player:', error);
        return false;
      }
    },
    []
  );

  return {
    permission,
    token,
    preferences,
    requestPermission,
    updatePreferences,
    subscribeToPlayer,
    unsubscribeFromPlayer,
  };
};
```

### Frontend: Offline Storage Utility

```typescript
// lib/offline-storage.ts

import { openDB, DBSchema, IDBPDatabase } from 'idb';

interface FantasyDBSchema extends DBSchema {
  players: {
    key: number;
    value: {
      id: number;
      full_name: string;
      position: string;
      team_abbreviation: string;
      updated_at: number;
    };
    indexes: { 'by-team': string };
  };
  predictions: {
    key: string;
    value: {
      id: string;
      player_id: number;
      category: string;
      predicted_value: number;
      confidence: number;
      date: string;
      updated_at: number;
    };
    indexes: { 'by-player': number; 'by-date': string };
  };
  pendingSync: {
    key: number;
    value: {
      id: number;
      type: string;
      data: any;
      created_at: number;
    };
  };
}

const DB_NAME = 'fantasy-basketball-offline';
const DB_VERSION = 1;

let dbPromise: Promise<IDBPDatabase<FantasyDBSchema>> | null = null;

export const getDB = async () => {
  if (!dbPromise) {
    dbPromise = openDB<FantasyDBSchema>(DB_NAME, DB_VERSION, {
      upgrade(db) {
        // Players store
        const playerStore = db.createObjectStore('players', {
          keyPath: 'id',
        });
        playerStore.createIndex('by-team', 'team_abbreviation');

        // Predictions store
        const predictionStore = db.createObjectStore('predictions', {
          keyPath: 'id',
        });
        predictionStore.createIndex('by-player', 'player_id');
        predictionStore.createIndex('by-date', 'date');

        // Pending sync store
        db.createObjectStore('pendingSync', {
          keyPath: 'id',
          autoIncrement: true,
        });
      },
    });
  }
  return dbPromise;
};

export const offlineStorage = {
  // Players
  async savePlayer(player: FantasyDBSchema['players']['value']) {
    const db = await getDB();
    player.updated_at = Date.now();
    await db.put('players', player);
  },

  async savePlayers(players: FantasyDBSchema['players']['value'][]) {
    const db = await getDB();
    const tx = db.transaction('players', 'readwrite');
    const now = Date.now();

    await Promise.all([
      ...players.map((player) =>
        tx.store.put({ ...player, updated_at: now })
      ),
      tx.done,
    ]);
  },

  async getPlayer(id: number) {
    const db = await getDB();
    return db.get('players', id);
  },

  async getAllPlayers() {
    const db = await getDB();
    return db.getAll('players');
  },

  async getPlayersByTeam(team: string) {
    const db = await getDB();
    return db.getAllFromIndex('players', 'by-team', team);
  },

  // Predictions
  async savePrediction(prediction: FantasyDBSchema['predictions']['value']) {
    const db = await getDB();
    prediction.updated_at = Date.now();
    await db.put('predictions', prediction);
  },

  async getPredictionsByPlayer(playerId: number) {
    const db = await getDB();
    return db.getAllFromIndex('predictions', 'by-player', playerId);
  },

  async getPredictionsByDate(date: string) {
    const db = await getDB();
    return db.getAllFromIndex('predictions', 'by-date', date);
  },

  // Pending sync
  async addPendingSync(type: string, data: any) {
    const db = await getDB();
    await db.add('pendingSync', {
      type,
      data,
      created_at: Date.now(),
    } as any);
  },

  async getPendingSync() {
    const db = await getDB();
    return db.getAll('pendingSync');
  },

  async removePendingSync(id: number) {
    const db = await getDB();
    await db.delete('pendingSync', id);
  },

  async clearPendingSync() {
    const db = await getDB();
    await db.clear('pendingSync');
  },

  // Utility
  async clearAll() {
    const db = await getDB();
    await Promise.all([
      db.clear('players'),
      db.clear('predictions'),
      db.clear('pendingSync'),
    ]);
  },

  async isStale(storeName: 'players' | 'predictions', maxAge: number) {
    const db = await getDB();
    const items = await db.getAll(storeName);

    if (items.length === 0) return true;

    const now = Date.now();
    const oldest = Math.min(...items.map((item) => item.updated_at));

    return now - oldest > maxAge;
  },
};
```

---

## Configuration Files

### `requirements.txt` (Enhanced)

```
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
gunicorn==21.2.0
websockets==12.0

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1
asyncpg==0.29.0

# Redis
redis==5.0.1
aioredis==2.0.1

# Kafka
aiokafka==0.10.0
confluent-kafka==2.3.0

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
cryptography==41.0.7

# Background Jobs
celery==5.3.6
celery-beat==2.6.0
flower==2.0.1

# Data & ML
numpy==1.26.3
pandas==2.1.4
scikit-learn==1.4.0
xgboost==2.0.3
lightgbm==4.3.0
tensorflow==2.15.0
joblib==1.3.2

# ML Ops
mlflow==2.10.0
feast==0.36.0
optuna==3.5.0
shap==0.44.0

# NBA API
nba-api==1.4.1

# Yahoo API
requests==2.31.0
requests-oauthlib==1.4.0

# Notifications
firebase-admin==6.3.0
sendgrid==6.11.0
twilio==8.11.0

# Utilities
python-dotenv==1.0.1
pydantic==2.5.3
pydantic-settings==2.1.0
httpx==0.26.0

# Monitoring
sentry-sdk[fastapi]==1.40.0
prometheus-fastapi-instrumentator==6.1.0
python-json-logger==2.0.7
structlog==24.1.0

# Rate Limiting
slowapi==0.1.9

# GraphQL (optional)
strawberry-graphql[fastapi]==0.217.1
```

### `requirements-ml.txt`

```
# Core ML
numpy==1.26.3
pandas==2.1.4
scikit-learn==1.4.0

# Gradient Boosting
xgboost==2.0.3
lightgbm==4.3.0
catboost==1.2.2

# Deep Learning
tensorflow==2.15.0
keras==3.0.2

# ML Operations
mlflow==2.10.0
feast==0.36.0
optuna==3.5.0
ray[tune]==2.9.0

# Explainability
shap==0.44.0
lime==0.2.0.1

# Data Processing
pyarrow==15.0.0
polars==0.20.5

# Model Serving
onnx==1.15.0
onnxruntime==1.16.3

# Validation
evidently==0.4.13
great-expectations==0.18.8
```

### `docker-compose.prod.yml`

```yaml
version: '3.8'

services:
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
    ports:
      - '8000:8000'
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - KAFKA_BOOTSTRAP_SERVERS=${KAFKA_BOOTSTRAP_SERVERS}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - ENVIRONMENT=production
    depends_on:
      - db
      - redis
      - kafka
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 2G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  websocket:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: uvicorn websocket_server:app --host 0.0.0.0 --port 8001
    ports:
      - '8001:8001'
    environment:
      - REDIS_URL=${REDIS_URL}
      - KAFKA_BOOTSTRAP_SERVERS=${KAFKA_BOOTSTRAP_SERVERS}
    depends_on:
      - redis
      - kafka
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 1G

  ml_service:
    build:
      context: ./backend
      dockerfile: Dockerfile.ml
    command: python -m ml.inference.server
    ports:
      - '8002:8002'
    environment:
      - MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI}
      - FEAST_REPO_PATH=/app/feast/feature_repo
    volumes:
      - ml_models:/app/ml/models
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2'
          memory: 4G

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A tasks.celery_app worker --loglevel=info --concurrency=8
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - KAFKA_BOOTSTRAP_SERVERS=${KAFKA_BOOTSTRAP_SERVERS}
    depends_on:
      - db
      - redis
      - kafka
    deploy:
      replicas: 4
      resources:
        limits:
          cpus: '1'
          memory: 2G

  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A tasks.celery_app beat --loglevel=info
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    depends_on:
      - zookeeper
    volumes:
      - kafka_data:/var/lib/kafka/data

  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    volumes:
      - zookeeper_data:/var/lib/zookeeper/data

  nginx:
    image: nginx:alpine
    ports:
      - '80:80'
      - '443:443'
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - api
      - websocket

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - '9090:9090'

  grafana:
    image: grafana/grafana:latest
    volumes:
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
      - grafana_data:/var/lib/grafana
    ports:
      - '3001:3000'
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}

volumes:
  postgres_data:
  redis_data:
  kafka_data:
  zookeeper_data:
  ml_models:
  prometheus_data:
  grafana_data:
```

### `package.json` (Enhanced)

```json
{
  "name": "fantasy-basketball-frontend",
  "version": "2.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "e2e": "playwright test",
    "analyze": "ANALYZE=true next build"
  },
  "dependencies": {
    "next": "^14.1.0",
    "next-pwa": "^5.6.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^5.17.19",
    "axios": "^1.6.5",
    "zustand": "^4.5.0",
    "firebase": "^10.7.2",
    "idb": "^8.0.0",
    "framer-motion": "^11.0.3",
    "recharts": "^2.10.4",
    "date-fns": "^3.3.1",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-toast": "^1.1.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6"
  },
  "devDependencies": {
    "@types/node": "^20.11.5",
    "@types/react": "^18.2.48",
    "@types/react-dom": "^18.2.18",
    "typescript": "^5.3.3",
    "tailwindcss": "^3.4.1",
    "postcss": "^8.4.33",
    "autoprefixer": "^10.4.17",
    "eslint": "^8.56.0",
    "eslint-config-next": "^14.1.0",
    "jest": "^29.7.0",
    "@testing-library/react": "^14.1.2",
    "@testing-library/jest-dom": "^6.2.0",
    "@playwright/test": "^1.41.0",
    "@next/bundle-analyzer": "^14.1.0"
  }
}
```

---

## Best Practices

### Backend Organization

1. **Separation of Concerns**: Keep models, schemas, services separate
2. **Dependency Injection**: Use FastAPI's Depends for database sessions, auth
3. **Service Layer**: Business logic in services, not endpoints
4. **Type Hints**: Use Python type hints everywhere
5. **Error Handling**: Custom exceptions with proper HTTP status codes
6. **Event-Driven**: Use Kafka for async communication between services
7. **Circuit Breakers**: Implement resilience patterns for external APIs
8. **Feature Flags**: Use feature flags for gradual rollouts

### ML Pipeline Organization

1. **Feature Store**: Use Feast for consistent feature engineering
2. **Model Registry**: Use MLflow for model versioning and deployment
3. **Ensemble Models**: Combine multiple models for better predictions
4. **Monitoring**: Track model performance and data drift
5. **A/B Testing**: Test model improvements before full rollout
6. **Explainability**: Use SHAP for prediction explanations

### Frontend Organization

1. **Component Composition**: Small, reusable components
2. **Custom Hooks**: Extract logic into hooks for reusability
3. **Type Safety**: Use TypeScript for all components
4. **API Abstraction**: Centralized API client with interceptors
5. **State Management**: React Query for server state, Zustand for client state
6. **Offline Support**: IndexedDB for offline data persistence
7. **PWA Features**: Service workers for caching and background sync
8. **Mobile-First**: Responsive design with touch-optimized interactions

### Testing Organization

1. **Unit Tests**: Test individual functions/components
2. **Integration Tests**: Test API endpoints with test database
3. **E2E Tests**: Test complete user flows with Playwright
4. **ML Tests**: Test model performance and backtesting
5. **Performance Tests**: Load testing and latency benchmarks
6. **Test Coverage**: Aim for >80% coverage
7. **Fixtures**: Reusable test data in conftest.py

### Infrastructure Organization

1. **Infrastructure as Code**: Use Terraform for cloud resources
2. **Kubernetes**: Container orchestration with auto-scaling
3. **GitOps**: Use ArgoCD or Flux for deployments
4. **Monitoring**: Prometheus + Grafana for observability
5. **Logging**: ELK stack for centralized logging
6. **Secrets Management**: Use Vault or cloud-native solutions

---

## Quick Start

```bash
# Clone repository
git clone <your-repo-url>
cd fantasy-basketball-analyzer

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -r requirements-ml.txt
cp .env.example .env
# Edit .env with your settings

# Frontend setup
cd ../frontend
npm install
cp .env.example .env.local
# Edit .env.local with API URL

# Start with Docker Compose (recommended)
cd ..
docker-compose up -d

# Or start manually (backend)
cd backend
uvicorn main:app --reload

# Start manually (frontend)
cd frontend
npm run dev

# Run ML training
cd backend
python scripts/train_models.py

# Run tests
cd backend
pytest --cov=app

cd ../frontend
npm test
```

---

This enhanced structure supports the full feature set including WebSocket real-time updates, ensemble ML models, data source failover, push notifications, PWA support, and comprehensive monitoring.
