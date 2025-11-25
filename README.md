# Fantasy Basketball Analyzer SaaS

**AI-Powered Fantasy Basketball Statistics, Predictions, and Team Recommendations**

**Version:** 2.0 | **Last Updated:** 2025-01-15

---

## Overview

Fantasy Basketball Analyzer is an enterprise-grade SaaS platform delivering:

- **Real-Time Statistics**: Live NBA stats with WebSocket streaming
- **Ensemble ML Predictions**: XGBoost, LightGBM, and LSTM-based projections
- **Smart Recommendations**: AI-driven start/sit, waiver, and trade advice
- **Yahoo Integration**: Full OAuth 2.0 sync with leagues and rosters
- **Matchup Analysis**: Weekly H2H predictions with category breakdowns
- **Z-Score Rankings**: Industry-standard player valuations
- **Injury Tracking**: Real-time injury alerts and impact analysis
- **Mobile-First PWA**: Offline support with push notifications

---

## Documentation

| Document | Description | Key Topics |
|----------|-------------|------------|
| [TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md) | System architecture & ML pipeline | Database schema, API specs, algorithms |
| [LOVABLE_INTEGRATION_GUIDE.md](LOVABLE_INTEGRATION_GUIDE.md) | Frontend integration guide | WebSocket, PWA, mobile-first patterns |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Production deployment | Kubernetes, CI/CD, monitoring |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Codebase organization | Folder structure, code templates |
| [DATA_DICTIONARY.md](DATA_DICTIONARY.md) | Data definitions | Tables, fields, relationships |
| [ERROR_CODES.md](ERROR_CODES.md) | Error reference | API errors, troubleshooting |
| [RUNBOOK.md](RUNBOOK.md) | Operations guide | Incident response, maintenance |

---

## Architecture

```
                                   ┌─────────────────────────────────────┐
                                   │           CDN (CloudFlare)          │
                                   │        Static Assets + WAF          │
                                   └─────────────────┬───────────────────┘
                                                     │
┌────────────────────────────────────────────────────┼────────────────────────────────────────────────────┐
│                                                    │                                                     │
│  ┌─────────────────────────────────────────────────▼─────────────────────────────────────────────────┐  │
│  │                              Frontend (React/Next.js PWA)                                          │  │
│  │                                                                                                     │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │  │
│  │  │   Mobile    │  │   Desktop   │  │   Service   │  │  IndexedDB  │  │    FCM      │            │  │
│  │  │   First UI  │  │   Views     │  │   Worker    │  │   Offline   │  │    Push     │            │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘            │  │
│  └─────────────────────────────────────┬──────────────────────┬────────────────────────────────────┘  │
│                                        │ HTTPS/REST           │ WSS                                    │
│                                        │ JWT Bearer           │ WebSocket                              │
│  ┌─────────────────────────────────────▼──────────────────────▼────────────────────────────────────┐  │
│  │                                   API Gateway (Kong/Nginx)                                       │  │
│  │                           Rate Limiting │ Load Balancing │ SSL Termination                       │  │
│  └─────────────────────────────────────┬──────────────────────┬────────────────────────────────────┘  │
│                                        │                      │                                        │
│          ┌─────────────────────────────┼──────────────────────┼─────────────────────────────┐         │
│          │                             │                      │                              │         │
│  ┌───────▼───────┐  ┌──────────────────▼───┐  ┌──────────────▼───────┐  ┌──────────────────▼──────┐  │
│  │   REST API    │  │   WebSocket Server   │  │     ML Service       │  │   Notification Service  │  │
│  │   FastAPI     │  │   Real-time Events   │  │   Predictions API    │  │   FCM + Email           │  │
│  │   /api/v1/    │  │   /ws/               │  │   /ml/v1/            │  │   /notifications/       │  │
│  │               │  │                      │  │                      │  │                         │  │
│  │  • Auth       │  │  • Live Scores       │  │  • XGBoost           │  │  • Injury Alerts        │  │
│  │  • Players    │  │  • Injury Updates    │  │  • LightGBM          │  │  • Game Reminders       │  │
│  │  • Teams      │  │  • Predictions       │  │  • LSTM              │  │  • Recommendations      │  │
│  │  • Rankings   │  │  • Recommendations   │  │  • Ensemble          │  │  • Trade Alerts         │  │
│  └───────┬───────┘  └──────────┬───────────┘  └──────────┬───────────┘  └────────────┬────────────┘  │
│          │                     │                         │                           │               │
│          └─────────────────────┼─────────────────────────┼───────────────────────────┘               │
│                                │                         │                                            │
│  ┌─────────────────────────────▼─────────────────────────▼────────────────────────────────────────┐  │
│  │                                   Message Queue (Kafka)                                         │  │
│  │                     Events: stats_update │ injury │ prediction │ recommendation                 │  │
│  └─────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                     │                                                  │
│          ┌──────────────────────────────────────────┼──────────────────────────────────────────┐      │
│          │                                          │                                           │      │
│  ┌───────▼───────┐  ┌───────────────┐  ┌───────────▼───────┐  ┌─────────────┐  ┌─────────────┐ │      │
│  │  PostgreSQL   │  │    Redis      │  │   Celery Workers  │  │   MLflow    │  │   Feast     │ │      │
│  │  + PgBouncer  │  │    Cluster    │  │                   │  │   Registry  │  │   Features  │ │      │
│  │               │  │               │  │  • Stats Ingest   │  │             │  │             │ │      │
│  │  • Users      │  │  • Cache      │  │  • Yahoo Sync     │  │  • Models   │  │  • Player   │ │      │
│  │  • Stats      │  │  • Sessions   │  │  • ML Training    │  │  • Metrics  │  │  • Game     │ │      │
│  │  • Predictions│  │  • Pub/Sub    │  │  • Notifications  │  │  • Versions │  │  • Opponent │ │      │
│  └───────────────┘  └───────────────┘  └───────────────────┘  └─────────────┘  └─────────────┘ │      │
│                                                                                                 │      │
│  └──────────────────────────────────────────────────────────────────────────────────────────────┘      │
│                                                                                                         │
│                                        Kubernetes Cluster                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘

External Data Sources:
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  NBA API    │  │   Yahoo     │  │   ESPN      │  │  Rotowire   │
│  (Primary)  │  │   Fantasy   │  │  (Fallback) │  │  (Injuries) │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘
```

---

## Key Features

### Core Platform

| Feature | Description | Status |
|---------|-------------|--------|
| **Real-Time Stats** | Live NBA statistics via WebSocket | Ready |
| **Ensemble ML** | XGBoost + LightGBM + LSTM predictions | Ready |
| **Yahoo Sync** | Full OAuth 2.0 league integration | Ready |
| **Recommendations** | AI-driven start/sit and waiver advice | Ready |
| **Z-Score Rankings** | Category-based player valuations | Ready |
| **Matchup Analysis** | Weekly H2H projections | Ready |

### Advanced Features

| Feature | Description | Status |
|---------|-------------|--------|
| **WebSocket Streaming** | Real-time updates via WSS | Ready |
| **Push Notifications** | FCM-based alerts | Ready |
| **PWA Support** | Offline-first with service worker | Ready |
| **Mobile-First UI** | Touch-optimized responsive design | Ready |
| **Injury Tracking** | Real-time injury alerts and impact | Ready |
| **Points League** | Fantasy points scoring support | Ready |
| **Data Failover** | Multi-source with circuit breaker | Ready |

---

## Tech Stack

### Backend Services

| Component | Technology | Purpose |
|-----------|------------|---------|
| REST API | FastAPI (Python 3.11+) | CRUD operations, auth |
| WebSocket | FastAPI WebSocket | Real-time streaming |
| ML Service | FastAPI + MLflow | Prediction serving |
| Task Queue | Celery + Redis | Background jobs |
| Message Bus | Apache Kafka | Event streaming |

### Data Layer

| Component | Technology | Purpose |
|-----------|------------|---------|
| Database | PostgreSQL 15+ | Primary data store |
| Connection Pool | PgBouncer | Connection management |
| Cache | Redis 7+ Cluster | Caching, sessions, pub/sub |
| Feature Store | Feast | ML feature management |
| Model Registry | MLflow | Model versioning |

### ML Pipeline

| Component | Technology | Purpose |
|-----------|------------|---------|
| Gradient Boosting | XGBoost, LightGBM | Structured predictions |
| Sequence Model | LSTM (PyTorch) | Time-series patterns |
| Ensemble | Custom Weighted | Combined predictions |
| Feature Engineering | Pandas, NumPy | Data transformation |

### Frontend

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | Next.js 14+ | React SSR/SSG |
| Language | TypeScript | Type safety |
| Styling | Tailwind CSS | Utility-first CSS |
| State | React Query + Zustand | Server + client state |
| Offline | IndexedDB + Service Worker | PWA support |
| Notifications | Firebase Cloud Messaging | Push notifications |

### Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| Container | Docker | Application packaging |
| Orchestration | Kubernetes | Container orchestration |
| IaC | Terraform | Infrastructure as code |
| CI/CD | GitHub Actions | Automated pipelines |
| Monitoring | Prometheus + Grafana | Observability |
| Logging | ELK Stack | Centralized logs |

---

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js 18+
- Docker & Docker Compose

### Development Setup

```bash
# Clone repository
git clone <your-repo-url>
cd fantasy-basketball-analyzer

# Start infrastructure
docker-compose -f docker-compose.dev.yml up -d

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-ml.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run migrations
alembic upgrade head

# Seed initial data
python scripts/seed_nba_data.py

# Start services
uvicorn main:app --reload --port 8000 &
python -m celery -A workers worker --loglevel=info &

# Frontend setup (new terminal)
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### Service URLs

| Service | URL |
|---------|-----|
| REST API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| WebSocket | ws://localhost:8000/ws |
| Frontend | http://localhost:3000 |
| Grafana | http://localhost:3001 |
| Prometheus | http://localhost:9090 |

---

## API Overview

### REST Endpoints

```
Authentication:
POST   /api/v1/auth/register      - Register new user
POST   /api/v1/auth/login         - Login and get tokens
POST   /api/v1/auth/refresh       - Refresh access token
POST   /api/v1/auth/logout        - Logout and revoke tokens

Players:
GET    /api/v1/players            - Search/list players
GET    /api/v1/players/{id}       - Get player details
GET    /api/v1/players/{id}/stats - Get player statistics
GET    /api/v1/players/trending   - Get trending players

Predictions:
GET    /api/v1/predictions/player/{id}  - Get player prediction
GET    /api/v1/predictions/daily        - Get daily predictions
GET    /api/v1/predictions/accuracy     - Get model accuracy

Teams:
GET    /api/v1/teams              - Get user's teams
GET    /api/v1/teams/{id}/roster  - Get team roster
GET    /api/v1/matchups/weekly/{id} - Get weekly matchup

Recommendations:
GET    /api/v1/recommendations/{team_id} - Get recommendations
POST   /api/v1/recommendations/{team_id}/feedback - Submit feedback
```

### WebSocket Channels

```
live_scores       - Real-time game statistics
injuries          - Injury status updates
predictions       - Prediction updates
team:{team_id}    - Team-specific events
```

See [LOVABLE_INTEGRATION_GUIDE.md](LOVABLE_INTEGRATION_GUIDE.md) for complete API documentation.

---

## ML Pipeline

### Ensemble Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Feature Engineering                       │
│  Player Stats │ Opponent Stats │ Schedule │ Injuries │ Trends│
└─────────────────────────┬───────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
    ┌────▼────┐     ┌────▼────┐     ┌─────▼─────┐
    │ XGBoost │     │LightGBM │     │   LSTM    │
    │  (40%)  │     │  (35%)  │     │   (25%)   │
    └────┬────┘     └────┬────┘     └─────┬─────┘
         │                │                │
         └────────────────┼────────────────┘
                          │
              ┌───────────▼───────────┐
              │   Weighted Ensemble   │
              │   Meta-Learner        │
              └───────────┬───────────┘
                          │
              ┌───────────▼───────────┐
              │   Final Prediction    │
              │   + Confidence Score  │
              └───────────────────────┘
```

### Model Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Points MAE | < 3.5 | 3.2 |
| Rebounds MAE | < 1.5 | 1.4 |
| Assists MAE | < 1.2 | 1.1 |
| Overall R² | > 0.75 | 0.78 |

---

## Testing

```bash
# Backend tests
cd backend
pytest                           # All tests
pytest --cov=app --cov-report=html  # With coverage
pytest tests/unit               # Unit tests
pytest tests/integration        # Integration tests
pytest -m "not slow"            # Fast tests only

# Frontend tests
cd frontend
npm test                        # Run tests
npm run test:watch             # Watch mode
npm run test:coverage          # With coverage

# E2E tests
npm run test:e2e               # Playwright E2E
```

---

## Deployment

### Production Deployment

```bash
# Build images
docker build -t fantasy-api:latest -f backend/Dockerfile .
docker build -t fantasy-ml:latest -f backend/Dockerfile.ml .
docker build -t fantasy-frontend:latest -f frontend/Dockerfile .

# Deploy to Kubernetes
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/
```

### Environment Variables

```bash
# Required
DATABASE_URL=postgresql://user:pass@host:5432/fantasy
REDIS_URL=redis://host:6379/0
JWT_SECRET_KEY=<secure-random-string>
YAHOO_CLIENT_ID=<yahoo-app-id>
YAHOO_CLIENT_SECRET=<yahoo-secret>

# Optional
SENTRY_DSN=<sentry-dsn>
FCM_SERVER_KEY=<firebase-key>
```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

---

## Monitoring

### Health Checks

```bash
# API health
curl https://api.yourdomain.com/health

# Detailed health
curl https://api.yourdomain.com/health/detailed
```

### Dashboards

| Dashboard | Purpose |
|-----------|---------|
| API Metrics | Request rates, latencies, errors |
| ML Performance | Prediction accuracy, model drift |
| Infrastructure | CPU, memory, disk, network |
| Business KPIs | Users, predictions, engagement |

---

## Competitive Advantages

| vs Competitor | Our Advantage |
|---------------|---------------|
| **vs Basketball Monster** | Modern UI, ensemble ML (not rules), real-time updates |
| **vs ESPN/Yahoo** | Advanced ML, personalized AI, cross-category optimization |
| **vs FantasyPros** | Automated advice, WebSocket streaming, offline PWA |
| **vs Hashtag Basketball** | Better Yahoo integration, mobile-first, push notifications |

---

## Roadmap

### Q1 2025
- [x] Core platform with ensemble ML
- [x] WebSocket real-time updates
- [x] PWA with offline support
- [x] Push notifications
- [ ] Trade analyzer

### Q2 2025
- [ ] ESPN integration
- [ ] Dynasty league support
- [ ] Player comparison tool
- [ ] Advanced analytics dashboard

### Q3 2025
- [ ] Mobile native apps (iOS/Android)
- [ ] Voice assistant integration
- [ ] Social features
- [ ] Premium tier features

---

## Contributing

This is a private project. See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for development guidelines.

---

## License

Proprietary - All rights reserved

---

## Support

1. Check documentation files
2. Review API docs at `/docs`
3. Check [RUNBOOK.md](RUNBOOK.md) for operations
4. Check [ERROR_CODES.md](ERROR_CODES.md) for troubleshooting
5. Contact development team

---

**Built for Fantasy Basketball enthusiasts**
