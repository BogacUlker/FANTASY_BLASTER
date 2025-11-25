# Deployment Guide & Checklist

**Version:** 2.0
**Last Updated:** 2025-01-11
**Purpose:** Complete deployment guide for Fantasy Basketball Analyzer SaaS with enhanced architecture

---

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Local Development Setup](#local-development-setup)
3. [Database Setup](#database-setup)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [WebSocket Server Deployment](#websocket-server-deployment)
7. [ML Service Deployment](#ml-service-deployment)
8. [Kafka & Event Streaming](#kafka--event-streaming)
9. [Environment Variables](#environment-variables)
10. [CI/CD Pipeline](#cicd-pipeline)
11. [Monitoring & Observability](#monitoring--observability)
12. [Scaling & Performance](#scaling--performance)
13. [Security Hardening](#security-hardening)
14. [Pre-Launch Checklist](#pre-launch-checklist)
15. [Post-Launch Operations](#post-launch-operations)
16. [Disaster Recovery](#disaster-recovery)

---

## Deployment Overview

### Enhanced Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PRODUCTION ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        LOAD BALANCER (NGINX/ALB)                      │   │
│  │                   HTTPS termination, SSL certificates                  │   │
│  └────────────────────┬────────────────────┬────────────────────────────┘   │
│                       │                    │                                 │
│         ┌─────────────▼──────────┐  ┌─────▼──────────────────┐              │
│         │   Frontend (Vercel)     │  │   API Gateway (Kong)    │              │
│         │   app.yourdomain.com    │  │   api.yourdomain.com    │              │
│         │   PWA + CDN + Edge      │  │   Rate limiting, Auth   │              │
│         └────────────────────────┘  └────────┬─────────────────┘              │
│                                              │                               │
│  ┌───────────────────────────────────────────┼──────────────────────────┐   │
│  │                         BACKEND SERVICES                              │   │
│  │                                           │                           │   │
│  │   ┌─────────────────┐  ┌─────────────────▼──────────────┐            │   │
│  │   │  WebSocket       │  │   FastAPI (3 replicas)         │            │   │
│  │   │  Server (2x)     │  │   REST API + GraphQL           │            │   │
│  │   │  ws.yourdom.com  │  │   Horizontal Auto-Scaling      │            │   │
│  │   └────────┬─────────┘  └──────────────┬─────────────────┘            │   │
│  │            │                           │                              │   │
│  │   ┌────────▼───────────────────────────▼─────────────────┐            │   │
│  │   │              ML Service (2 replicas)                  │            │   │
│  │   │         XGBoost/LightGBM/LSTM Ensemble               │            │   │
│  │   │         Feature Store (Feast) + MLflow               │            │   │
│  │   └──────────────────────────────────────────────────────┘            │   │
│  │                                                                       │   │
│  │   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │   │
│  │   │  Celery Workers │  │  Celery Beat    │  │  Notification   │      │   │
│  │   │  (4 replicas)   │  │  (Scheduler)    │  │  Service        │      │   │
│  │   └─────────────────┘  └─────────────────┘  └─────────────────┘      │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │                         DATA LAYER                                     │   │
│  │                                                                        │   │
│  │   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │   │
│  │   │   PostgreSQL    │  │     Redis       │  │     Kafka       │       │   │
│  │   │   (Primary +    │  │   (Cluster)     │  │   (3 brokers)   │       │   │
│  │   │    Replica)     │  │   Cache + PubSub│  │   Event Stream  │       │   │
│  │   └─────────────────┘  └─────────────────┘  └─────────────────┘       │   │
│  │                                                                        │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │                      OBSERVABILITY STACK                               │   │
│  │                                                                        │   │
│  │   ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐     │   │
│  │   │ Prometheus │  │  Grafana   │  │   Sentry   │  │    ELK     │     │   │
│  │   │  Metrics   │  │ Dashboards │  │   Errors   │  │   Logs     │     │   │
│  │   └────────────┘  └────────────┘  └────────────┘  └────────────┘     │   │
│  │                                                                        │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Deployment Platforms Comparison

| Platform | Best For | Pros | Cons | Cost (Est.) |
|----------|----------|------|------|-------------|
| **Railway** | MVP/Startup | Easy setup, Postgres/Redis included | Limited Kafka support | $50-150/mo |
| **Render** | Alternative | Free tier available, Simple deployment | Slower cold starts | $30-100/mo |
| **AWS EKS** | Enterprise | Full control, Kafka support, Auto-scaling | Complex setup | $200-500/mo |
| **GCP GKE** | Enterprise | Great ML tools, Kubernetes | Learning curve | $150-400/mo |
| **Vercel** | Frontend | Best Next.js, Edge functions, CDN | Backend not supported | Free-$50/mo |

**Recommendations:**
- **MVP**: Railway (backend) + Vercel (frontend)
- **Growth**: AWS EKS + Vercel (frontend) + Managed Kafka (Confluent)
- **Enterprise**: Full AWS/GCP with Kubernetes + Terraform

---

## Local Development Setup

### Prerequisites

```bash
# Required software versions
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js 18+ (for frontend)
- Docker & Docker Compose 2.0+
- Kafka 3.0+ (optional, for event streaming)
```

### Docker Compose Development Stack

```yaml
# docker-compose.dev.yml

version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: fantasy_user
      POSTGRES_PASSWORD: dev_password
      POSTGRES_DB: fantasy_bball
    ports:
      - '5432:5432'
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/scripts/init_db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fantasy_user -d fantasy_bball"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - '6379:6379'
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - '2181:2181'
    healthcheck:
      test: ["CMD", "nc", "-z", "localhost", "2181"]
      interval: 10s
      timeout: 5s
      retries: 5

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      zookeeper:
        condition: service_healthy
    ports:
      - '9092:9092'
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
    healthcheck:
      test: ["CMD-SHELL", "kafka-broker-api-versions --bootstrap-server localhost:9092"]
      interval: 10s
      timeout: 10s
      retries: 10

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - '8000:8000'
    environment:
      DATABASE_URL: postgresql://fantasy_user:dev_password@db:5432/fantasy_bball
      REDIS_URL: redis://redis:6379/0
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      JWT_SECRET_KEY: dev-secret-key-change-in-production
      JWT_REFRESH_SECRET_KEY: dev-refresh-secret-key
      ENCRYPTION_KEY: dev-encryption-key-32-chars-long
      ENVIRONMENT: development
    volumes:
      - ./backend:/app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      kafka:
        condition: service_healthy

  websocket:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    command: uvicorn websocket_server:app --host 0.0.0.0 --port 8001 --reload
    ports:
      - '8001:8001'
    environment:
      REDIS_URL: redis://redis:6379/0
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
    volumes:
      - ./backend:/app
    depends_on:
      redis:
        condition: service_healthy
      kafka:
        condition: service_healthy

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    command: celery -A tasks.celery_app worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://fantasy_user:dev_password@db:5432/fantasy_bball
      REDIS_URL: redis://redis:6379/0
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
    volumes:
      - ./backend:/app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    command: celery -A tasks.celery_app beat --loglevel=info
    environment:
      DATABASE_URL: postgresql://fantasy_user:dev_password@db:5432/fantasy_bball
      REDIS_URL: redis://redis:6379/0
    volumes:
      - ./backend:/app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  prometheus:
    image: prom/prometheus:latest
    ports:
      - '9090:9090'
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana:latest
    ports:
      - '3001:3000'
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
      - grafana_data:/var/lib/grafana

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

### Quick Start Commands

```bash
# Clone repository
git clone <your-repo-url>
cd fantasy-basketball-analyzer

# Start all services
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be healthy
docker-compose -f docker-compose.dev.yml ps

# Services available at:
# - Backend API: http://localhost:8000
# - WebSocket: ws://localhost:8001
# - API Docs: http://localhost:8000/docs
# - GraphQL: http://localhost:8000/api/v2/graphql
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3001

# View logs
docker-compose -f docker-compose.dev.yml logs -f backend

# Run database migrations
docker-compose -f docker-compose.dev.yml exec backend alembic upgrade head

# Seed initial data
docker-compose -f docker-compose.dev.yml exec backend python scripts/seed_nba_data.py

# Stop services
docker-compose -f docker-compose.dev.yml down
```

---

## Database Setup

### PostgreSQL Configuration for Production

```sql
-- scripts/init_db.sql

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Performance tuning (adjust based on instance size)
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '64MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET work_mem = '64MB';
ALTER SYSTEM SET min_wal_size = '1GB';
ALTER SYSTEM SET max_wal_size = '4GB';
ALTER SYSTEM SET max_worker_processes = 8;
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_workers = 8;
ALTER SYSTEM SET max_parallel_maintenance_workers = 4;

-- Connection pooling settings
ALTER SYSTEM SET max_connections = 200;

-- Logging for performance monitoring
ALTER SYSTEM SET log_min_duration_statement = 1000;
ALTER SYSTEM SET log_checkpoints = on;
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
ALTER SYSTEM SET log_lock_waits = on;
ALTER SYSTEM SET log_temp_files = 0;
```

### Database Migration Strategy

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial schema with all tables"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View migration history
alembic history

# Generate migration for specific changes
alembic revision --autogenerate -m "Add injury tracking tables"
```

### Connection Pooling with PgBouncer

```ini
# pgbouncer.ini

[databases]
fantasy_bball = host=postgres port=5432 dbname=fantasy_bball

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 3
max_db_connections = 100
server_idle_timeout = 600
server_lifetime = 3600
```

---

## Backend Deployment

### Kubernetes Deployment (Production)

```yaml
# kubernetes/base/deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: fantasy-basketball-api
  labels:
    app: fantasy-basketball
    component: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fantasy-basketball
      component: api
  template:
    metadata:
      labels:
        app: fantasy-basketball
        component: api
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      containers:
        - name: api
          image: your-registry/fantasy-basketball-api:latest
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: fantasy-basketball-secrets
                  key: database-url
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: fantasy-basketball-secrets
                  key: redis-url
            - name: KAFKA_BOOTSTRAP_SERVERS
              valueFrom:
                configMapKeyRef:
                  name: fantasy-basketball-config
                  key: kafka-servers
            - name: JWT_SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: fantasy-basketball-secrets
                  key: jwt-secret
            - name: ENVIRONMENT
              value: "production"
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "2Gi"
              cpu: "1000m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
          volumeMounts:
            - name: ml-models
              mountPath: /app/ml/models
              readOnly: true
      volumes:
        - name: ml-models
          persistentVolumeClaim:
            claimName: ml-models-pvc
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values:
                        - fantasy-basketball
                topologyKey: kubernetes.io/hostname
---
apiVersion: v1
kind: Service
metadata:
  name: fantasy-basketball-api
spec:
  selector:
    app: fantasy-basketball
    component: api
  ports:
    - port: 80
      targetPort: 8000
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fantasy-basketball-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fantasy-basketball-api
  minReplicas: 3
  maxReplicas: 10
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
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "100"
```

### Railway Deployment (Simplified)

```toml
# railway.toml

[build]
builder = "nixpacks"

[deploy]
startCommand = "gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 120 --keep-alive 5"
restartPolicyType = "on-failure"
restartPolicyMaxRetries = 10
healthcheckPath = "/health"
healthcheckTimeout = 300
```

### Dockerfile (Production)

```dockerfile
# Dockerfile

FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r fantasy && useradd -r -g fantasy fantasy

# Copy wheels and install
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY . .

# Set ownership
RUN chown -R fantasy:fantasy /app

# Switch to non-root user
USER fantasy

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

---

## WebSocket Server Deployment

### Kubernetes WebSocket Deployment

```yaml
# kubernetes/base/websocket-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: fantasy-basketball-websocket
  labels:
    app: fantasy-basketball
    component: websocket
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fantasy-basketball
      component: websocket
  template:
    metadata:
      labels:
        app: fantasy-basketball
        component: websocket
    spec:
      containers:
        - name: websocket
          image: your-registry/fantasy-basketball-websocket:latest
          ports:
            - containerPort: 8001
          env:
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: fantasy-basketball-secrets
                  key: redis-url
            - name: KAFKA_BOOTSTRAP_SERVERS
              valueFrom:
                configMapKeyRef:
                  name: fantasy-basketball-config
                  key: kafka-servers
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          livenessProbe:
            tcpSocket:
              port: 8001
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            tcpSocket:
              port: 8001
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: fantasy-basketball-websocket
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
spec:
  selector:
    app: fantasy-basketball
    component: websocket
  ports:
    - port: 80
      targetPort: 8001
  type: LoadBalancer
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 3600
```

### NGINX WebSocket Configuration

```nginx
# nginx.conf

upstream websocket_backend {
    ip_hash;
    server websocket-1:8001;
    server websocket-2:8001;
}

server {
    listen 443 ssl http2;
    server_name ws.yourdomain.com;

    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;

    location / {
        proxy_pass http://websocket_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket specific settings
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
        proxy_connect_timeout 60s;

        # Buffer settings
        proxy_buffering off;
        proxy_buffer_size 4k;
    }
}
```

---

## ML Service Deployment

### ML Service Kubernetes Deployment

```yaml
# kubernetes/base/ml-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: fantasy-basketball-ml
  labels:
    app: fantasy-basketball
    component: ml
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fantasy-basketball
      component: ml
  template:
    metadata:
      labels:
        app: fantasy-basketball
        component: ml
    spec:
      containers:
        - name: ml-service
          image: your-registry/fantasy-basketball-ml:latest
          ports:
            - containerPort: 8002
          env:
            - name: MLFLOW_TRACKING_URI
              value: "http://mlflow:5000"
            - name: FEAST_REPO_PATH
              value: "/app/feast/feature_repo"
            - name: MODEL_VERSION
              value: "production"
          resources:
            requests:
              memory: "2Gi"
              cpu: "1000m"
            limits:
              memory: "4Gi"
              cpu: "2000m"
          volumeMounts:
            - name: ml-models
              mountPath: /app/ml/models
            - name: feast-repo
              mountPath: /app/feast
          livenessProbe:
            httpGet:
              path: /health
              port: 8002
            initialDelaySeconds: 60
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /ready
              port: 8002
            initialDelaySeconds: 30
            periodSeconds: 10
      volumes:
        - name: ml-models
          persistentVolumeClaim:
            claimName: ml-models-pvc
        - name: feast-repo
          configMap:
            name: feast-config
---
apiVersion: v1
kind: Service
metadata:
  name: fantasy-basketball-ml
spec:
  selector:
    app: fantasy-basketball
    component: ml
  ports:
    - port: 8002
      targetPort: 8002
  type: ClusterIP
```

### MLflow Server Deployment

```yaml
# kubernetes/base/mlflow-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: mlflow
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mlflow
  template:
    metadata:
      labels:
        app: mlflow
    spec:
      containers:
        - name: mlflow
          image: ghcr.io/mlflow/mlflow:latest
          args:
            - "server"
            - "--backend-store-uri"
            - "postgresql://mlflow:password@postgres:5432/mlflow"
            - "--default-artifact-root"
            - "s3://your-bucket/mlflow-artifacts"
            - "--host"
            - "0.0.0.0"
          ports:
            - containerPort: 5000
          env:
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: access-key
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: secret-key
---
apiVersion: v1
kind: Service
metadata:
  name: mlflow
spec:
  selector:
    app: mlflow
  ports:
    - port: 5000
      targetPort: 5000
```

### ML Dockerfile

```dockerfile
# Dockerfile.ml

FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-ml.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements-ml.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq5 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r mluser && useradd -r -g mluser mluser

# Copy wheels and install
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application
COPY ml/ ./ml/
COPY feast/ ./feast/

# Set ownership
RUN chown -R mluser:mluser /app

USER mluser

EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

CMD ["python", "-m", "ml.inference.server"]
```

---

## Kafka & Event Streaming

### Kafka Topics Configuration

```bash
# Create required topics
kafka-topics --create --topic injuries --bootstrap-server kafka:9092 --partitions 3 --replication-factor 3
kafka-topics --create --topic game-scores --bootstrap-server kafka:9092 --partitions 6 --replication-factor 3
kafka-topics --create --topic predictions --bootstrap-server kafka:9092 --partitions 3 --replication-factor 3
kafka-topics --create --topic notifications --bootstrap-server kafka:9092 --partitions 3 --replication-factor 3
kafka-topics --create --topic lineup-changes --bootstrap-server kafka:9092 --partitions 3 --replication-factor 3
```

### Kafka Kubernetes Deployment (using Strimzi)

```yaml
# kubernetes/kafka/kafka-cluster.yaml

apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: fantasy-basketball-kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3
      min.insync.replicas: 2
      inter.broker.protocol.version: "3.6"
      log.retention.hours: 168
      log.retention.bytes: 10737418240
    storage:
      type: persistent-claim
      size: 100Gi
      class: gp3
    resources:
      requests:
        memory: 2Gi
        cpu: "500m"
      limits:
        memory: 4Gi
        cpu: "2000m"
    metricsConfig:
      type: jmxPrometheusExporter
      valueFrom:
        configMapKeyRef:
          name: kafka-metrics
          key: kafka-metrics-config.yml
  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 10Gi
      class: gp3
    resources:
      requests:
        memory: 512Mi
        cpu: "250m"
      limits:
        memory: 1Gi
        cpu: "500m"
  entityOperator:
    topicOperator: {}
    userOperator: {}
```

---

## Environment Variables

### Complete Environment Configuration

```bash
# backend/.env.production

# ===========================================
# DATABASE
# ===========================================
DATABASE_URL=postgresql://user:password@postgres:5432/fantasy_bball
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=1800

# ===========================================
# REDIS
# ===========================================
REDIS_URL=redis://:password@redis-cluster:6379/0
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=5

# ===========================================
# KAFKA
# ===========================================
KAFKA_BOOTSTRAP_SERVERS=kafka-1:9092,kafka-2:9092,kafka-3:9092
KAFKA_CONSUMER_GROUP=fantasy-basketball
KAFKA_AUTO_OFFSET_RESET=latest
KAFKA_ENABLE_AUTO_COMMIT=false

# ===========================================
# SECURITY
# ===========================================
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-64>
JWT_REFRESH_SECRET_KEY=<generate-with-openssl-rand-hex-64>
SECRET_KEY=<generate-with-openssl-rand-hex-64>
ENCRYPTION_KEY=<generate-with-openssl-rand-hex-32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ===========================================
# YAHOO OAUTH
# ===========================================
YAHOO_CLIENT_ID=<your-yahoo-app-id>
YAHOO_CLIENT_SECRET=<your-yahoo-app-secret>
YAHOO_REDIRECT_URI=https://api.yourdomain.com/api/v1/yahoo/auth/callback

# ===========================================
# DATA SOURCES
# ===========================================
ESPN_API_KEY=<your-espn-api-key>
TWITTER_BEARER_TOKEN=<your-twitter-bearer-token>

# ===========================================
# NOTIFICATIONS
# ===========================================
FIREBASE_CREDENTIALS_PATH=/app/config/firebase-credentials.json
SENDGRID_API_KEY=<your-sendgrid-api-key>
TWILIO_ACCOUNT_SID=<your-twilio-account-sid>
TWILIO_AUTH_TOKEN=<your-twilio-auth-token>

# ===========================================
# ML CONFIGURATION
# ===========================================
MLFLOW_TRACKING_URI=http://mlflow:5000
FEAST_REPO_PATH=/app/feast/feature_repo
MODEL_REGISTRY_PATH=/app/ml/models/registry
MODEL_VERSION=production

# ===========================================
# CIRCUIT BREAKER
# ===========================================
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60
CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS=3

# ===========================================
# RATE LIMITING
# ===========================================
RATE_LIMIT_FREE_TIER=100
RATE_LIMIT_PREMIUM_TIER=1000
RATE_LIMIT_ENTERPRISE_TIER=10000

# ===========================================
# WEBSOCKET
# ===========================================
WS_HEARTBEAT_INTERVAL=30
WS_MAX_CONNECTIONS=10000
WS_MAX_MESSAGE_SIZE=1048576

# ===========================================
# MONITORING
# ===========================================
SENTRY_DSN=<your-sentry-dsn>
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090

# ===========================================
# ENVIRONMENT
# ===========================================
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# ===========================================
# CORS
# ===========================================
ALLOWED_ORIGINS=https://app.yourdomain.com,https://yourdomain.com
```

### Frontend Environment

```bash
# frontend/.env.production

# API
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
NEXT_PUBLIC_WS_URL=wss://ws.yourdomain.com

# Firebase (Push Notifications)
NEXT_PUBLIC_FIREBASE_API_KEY=<your-firebase-api-key>
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=<your-project>.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=<your-project-id>
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=<sender-id>
NEXT_PUBLIC_FIREBASE_APP_ID=<app-id>
NEXT_PUBLIC_FIREBASE_VAPID_KEY=<vapid-key>

# Yahoo OAuth
NEXT_PUBLIC_YAHOO_REDIRECT_URI=https://app.yourdomain.com/auth/yahoo/callback

# Analytics
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX

# Feature Flags
NEXT_PUBLIC_ENABLE_PWA=true
NEXT_PUBLIC_ENABLE_PUSH_NOTIFICATIONS=true
```

---

## CI/CD Pipeline

### GitHub Actions Complete Workflow

```yaml
# .github/workflows/deploy.yml

name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ===========================================
  # BACKEND TESTS
  # ===========================================
  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install -r backend/requirements-dev.txt

      - name: Run linter
        run: ruff check backend/app/

      - name: Run type checker
        run: mypy backend/app/ --ignore-missing-imports

      - name: Run tests
        env:
          DATABASE_URL: postgresql://test_user:test_password@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
          JWT_SECRET_KEY: test-secret-key
          JWT_REFRESH_SECRET_KEY: test-refresh-secret
          ENCRYPTION_KEY: test-encryption-key-32chars
        run: |
          cd backend
          pytest --cov=app --cov-report=xml --cov-report=html tests/

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: backend/coverage.xml
          flags: backend

  # ===========================================
  # ML TESTS
  # ===========================================
  test-ml:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install ML dependencies
        run: pip install -r backend/requirements-ml.txt

      - name: Run ML tests
        run: |
          cd backend
          pytest tests/ml/ -v

  # ===========================================
  # FRONTEND TESTS
  # ===========================================
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run linter
        run: |
          cd frontend
          npm run lint

      - name: Run type check
        run: |
          cd frontend
          npm run type-check

      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: frontend/coverage/lcov.info
          flags: frontend

  # ===========================================
  # SECURITY SCAN
  # ===========================================
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Run Snyk security scan
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

  # ===========================================
  # BUILD & PUSH IMAGES
  # ===========================================
  build-and-push:
    needs: [test-backend, test-ml, test-frontend, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build and push API image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          file: ./backend/Dockerfile
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-api:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-api:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build and push ML image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          file: ./backend/Dockerfile.ml
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-ml:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-ml:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ===========================================
  # DEPLOY TO KUBERNETES
  # ===========================================
  deploy-staging:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: staging

    steps:
      - uses: actions/checkout@v4

      - name: Set up kubectl
        uses: azure/setup-kubectl@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Update kubeconfig
        run: aws eks update-kubeconfig --name fantasy-basketball-staging

      - name: Deploy to staging
        run: |
          kubectl set image deployment/fantasy-basketball-api \
            api=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-api:${{ github.sha }} \
            -n staging
          kubectl set image deployment/fantasy-basketball-ml \
            ml-service=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-ml:${{ github.sha }} \
            -n staging
          kubectl rollout status deployment/fantasy-basketball-api -n staging
          kubectl rollout status deployment/fantasy-basketball-ml -n staging

      - name: Run integration tests
        run: |
          npm install -g newman
          newman run tests/postman/integration.json \
            --environment tests/postman/staging.json \
            --reporters cli,junit \
            --reporter-junit-export results.xml

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production

    steps:
      - uses: actions/checkout@v4

      - name: Set up kubectl
        uses: azure/setup-kubectl@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Update kubeconfig
        run: aws eks update-kubeconfig --name fantasy-basketball-prod

      - name: Deploy to production (canary)
        run: |
          # Deploy canary (10% traffic)
          kubectl apply -f kubernetes/overlays/production/canary.yaml
          sleep 60

          # Check canary health
          CANARY_ERRORS=$(kubectl logs -l app=fantasy-basketball,version=canary -n production --tail=100 | grep -c ERROR || true)
          if [ "$CANARY_ERRORS" -gt 10 ]; then
            echo "Canary deployment has too many errors, rolling back"
            kubectl delete -f kubernetes/overlays/production/canary.yaml
            exit 1
          fi

          # Full rollout
          kubectl set image deployment/fantasy-basketball-api \
            api=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-api:${{ github.sha }} \
            -n production
          kubectl rollout status deployment/fantasy-basketball-api -n production

      - name: Notify deployment
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "Production deployment completed: ${{ github.sha }}"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

## Monitoring & Observability

### Prometheus Configuration

```yaml
# monitoring/prometheus/prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

rule_files:
  - /etc/prometheus/alerts/*.yml

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'fantasy-basketball-api'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: fantasy-basketball
      - source_labels: [__meta_kubernetes_pod_label_component]
        action: keep
        regex: api

  - job_name: 'fantasy-basketball-ml'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        action: keep
        regex: fantasy-basketball
      - source_labels: [__meta_kubernetes_pod_label_component]
        action: keep
        regex: ml

  - job_name: 'kafka'
    static_configs:
      - targets: ['kafka-1:9404', 'kafka-2:9404', 'kafka-3:9404']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### Alert Rules

```yaml
# monitoring/prometheus/alerts/api-alerts.yml

groups:
  - name: api-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} for the last 5 minutes"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API latency detected"
          description: "95th percentile latency is {{ $value }}s"

      - alert: ServiceDown
        expr: up{job="fantasy-basketball-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "API service is down"
          description: "{{ $labels.instance }} has been down for more than 1 minute"

      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes{container="api"} / container_spec_memory_limit_bytes{container="api"} > 0.85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value | humanizePercentage }}"

      - alert: HighCPUUsage
        expr: rate(container_cpu_usage_seconds_total{container="api"}[5m]) > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is {{ $value | humanizePercentage }}"

  - name: ml-alerts
    rules:
      - alert: ModelDriftDetected
        expr: ml_model_drift_score > 0.3
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Model drift detected"
          description: "Drift score is {{ $value }} for model {{ $labels.model_name }}"

      - alert: LowPredictionAccuracy
        expr: ml_prediction_accuracy < 0.6
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Low prediction accuracy"
          description: "Accuracy dropped to {{ $value }} for {{ $labels.category }}"

      - alert: HighInferenceLatency
        expr: histogram_quantile(0.95, rate(ml_inference_duration_seconds_bucket[5m])) > 0.2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High ML inference latency"
          description: "95th percentile inference time is {{ $value }}s"

  - name: infrastructure-alerts
    rules:
      - alert: KafkaConsumerLag
        expr: kafka_consumer_lag > 10000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High Kafka consumer lag"
          description: "Consumer {{ $labels.consumer_group }} has lag of {{ $value }}"

      - alert: DatabaseConnectionPoolExhausted
        expr: pg_stat_activity_count / pg_settings_max_connections > 0.8
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "{{ $value | humanizePercentage }} of connections used"

      - alert: RedisMemoryHigh
        expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis memory usage high"
          description: "Redis memory at {{ $value | humanizePercentage }}"
```

### Grafana Dashboards

```json
{
  "dashboard": {
    "title": "Fantasy Basketball - API Performance",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{job=\"fantasy-basketball-api\"}[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time (p95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p95"
          },
          {
            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p99"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) * 100",
            "legendFormat": "Error %"
          }
        ]
      },
      {
        "title": "Active WebSocket Connections",
        "type": "stat",
        "targets": [
          {
            "expr": "websocket_active_connections",
            "legendFormat": "Connections"
          }
        ]
      },
      {
        "title": "ML Predictions/sec",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(ml_predictions_total[5m])",
            "legendFormat": "{{category}}"
          }
        ]
      },
      {
        "title": "Prediction Accuracy by Category",
        "type": "bargauge",
        "targets": [
          {
            "expr": "ml_prediction_accuracy",
            "legendFormat": "{{category}}"
          }
        ]
      }
    ]
  }
}
```

---

## Scaling & Performance

### Horizontal Pod Autoscaler Configuration

```yaml
# kubernetes/base/hpa.yaml

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fantasy-basketball-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fantasy-basketball-api
  minReplicas: 3
  maxReplicas: 20
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Pods
          value: 4
          periodSeconds: 60
        - type: Percent
          value: 100
          periodSeconds: 60
      selectPolicy: Max
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
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
    - type: External
      external:
        metric:
          name: http_requests_per_second
          selector:
            matchLabels:
              service: fantasy-basketball-api
        target:
          type: AverageValue
          averageValue: "100"
```

### Redis Cluster Configuration

```yaml
# kubernetes/base/redis-cluster.yaml

apiVersion: redis.redis.opstreelabs.in/v1beta1
kind: RedisCluster
metadata:
  name: fantasy-basketball-redis
spec:
  clusterSize: 6
  clusterVersion: v7
  persistenceEnabled: true
  redisExporter:
    enabled: true
    image: quay.io/opstree/redis-exporter:v1.44.0
  storage:
    volumeClaimTemplate:
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: gp3
        resources:
          requests:
            storage: 10Gi
  resources:
    requests:
      cpu: 200m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 2Gi
```

### Performance Benchmarks

```bash
# Load testing with k6

# scripts/load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up to 100 users
    { duration: '5m', target: 100 },   // Stay at 100 users
    { duration: '2m', target: 200 },   // Ramp up to 200 users
    { duration: '5m', target: 200 },   // Stay at 200 users
    { duration: '2m', target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.API_URL || 'https://api.yourdomain.com';

export default function () {
  // Get daily predictions
  let res = http.get(`${BASE_URL}/api/v1/predictions/daily`);
  check(res, {
    'predictions status is 200': (r) => r.status === 200,
    'predictions response time < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);

  // Get player stats
  res = http.get(`${BASE_URL}/api/v1/players?limit=20`);
  check(res, {
    'players status is 200': (r) => r.status === 200,
    'players response time < 300ms': (r) => r.timings.duration < 300,
  });
  sleep(1);
}
```

---

## Security Hardening

### Network Policies

```yaml
# kubernetes/base/network-policy.yaml

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-policy
spec:
  podSelector:
    matchLabels:
      app: fantasy-basketball
      component: api
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
        - podSelector:
            matchLabels:
              app: fantasy-basketball
      ports:
        - protocol: TCP
          port: 8000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
    - to:
        - podSelector:
            matchLabels:
              app: redis
      ports:
        - protocol: TCP
          port: 6379
    - to:
        - podSelector:
            matchLabels:
              app: kafka
      ports:
        - protocol: TCP
          port: 9092
    # Allow external API calls (NBA API, Yahoo)
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0
      ports:
        - protocol: TCP
          port: 443
```

### Pod Security Policy

```yaml
# kubernetes/base/pod-security.yaml

apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: fantasy-basketball-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'persistentVolumeClaim'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
  readOnlyRootFilesystem: true
```

### Secrets Management

```yaml
# kubernetes/base/external-secrets.yaml

apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: fantasy-basketball-secrets
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: fantasy-basketball-secrets
    creationPolicy: Owner
  data:
    - secretKey: database-url
      remoteRef:
        key: fantasy-basketball/prod/database
        property: url
    - secretKey: redis-url
      remoteRef:
        key: fantasy-basketball/prod/redis
        property: url
    - secretKey: jwt-secret
      remoteRef:
        key: fantasy-basketball/prod/jwt
        property: secret
    - secretKey: encryption-key
      remoteRef:
        key: fantasy-basketball/prod/encryption
        property: key
```

---

## Pre-Launch Checklist

### Infrastructure
- [ ] Kubernetes cluster provisioned and configured
- [ ] Network policies applied
- [ ] SSL certificates configured (Let's Encrypt/ACM)
- [ ] DNS records configured (A/CNAME)
- [ ] Load balancer configured with health checks
- [ ] Auto-scaling policies configured
- [ ] Persistent volumes provisioned

### Backend
- [ ] Database schema deployed and migrated
- [ ] All environment variables set in secrets
- [ ] NBA stats data seeded (teams, players)
- [ ] Health check endpoint returns 200
- [ ] API documentation accessible at `/docs`
- [ ] CORS configured for frontend domain
- [ ] Rate limiting enabled and tested
- [ ] Error tracking (Sentry) configured
- [ ] Structured logging configured
- [ ] Database backups configured (hourly/daily)
- [ ] Redis cluster working with replication

### ML Service
- [ ] Models trained and validated
- [ ] MLflow registry configured
- [ ] Feature store (Feast) materialized
- [ ] Model serving endpoint working
- [ ] Prediction accuracy meets threshold (>70%)
- [ ] Model drift monitoring enabled
- [ ] Backtesting validation passed

### WebSocket
- [ ] WebSocket server deployed
- [ ] Connection manager working
- [ ] Topic subscriptions working
- [ ] Heartbeat mechanism tested
- [ ] Redis pub/sub configured
- [ ] Session affinity configured

### Frontend
- [ ] Environment variables set
- [ ] API integration tested end-to-end
- [ ] Authentication flow working
- [ ] PWA manifest configured
- [ ] Service worker caching working
- [ ] Push notifications working
- [ ] Offline mode working
- [ ] Mobile responsive design tested
- [ ] Analytics configured

### Monitoring
- [ ] Prometheus scraping all services
- [ ] Grafana dashboards configured
- [ ] Alert rules configured
- [ ] On-call rotation set up
- [ ] Runbooks documented

### Security
- [ ] Security scan passed (no critical vulnerabilities)
- [ ] Network policies applied
- [ ] Secrets stored securely (AWS Secrets Manager/Vault)
- [ ] API rate limiting configured
- [ ] DDoS protection enabled
- [ ] WAF rules configured

---

## Post-Launch Operations

### Daily Operations

```bash
# Health check script
#!/bin/bash

echo "=== Fantasy Basketball Health Check ==="

# API Health
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://api.yourdomain.com/health)
echo "API Health: $API_STATUS"

# WebSocket Health
WS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://ws.yourdomain.com/health)
echo "WebSocket Health: $WS_STATUS"

# ML Service Health
ML_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://ml.yourdomain.com/health)
echo "ML Service Health: $ML_STATUS"

# Check Kubernetes pods
echo "=== Kubernetes Pods ==="
kubectl get pods -n production -l app=fantasy-basketball

# Check recent errors
echo "=== Recent Errors (last 1 hour) ==="
kubectl logs -n production -l app=fantasy-basketball --since=1h | grep ERROR | tail -20
```

### Weekly Tasks
- [ ] Review Grafana dashboards for anomalies
- [ ] Check prediction accuracy metrics
- [ ] Review error logs in Sentry
- [ ] Check database performance (slow queries)
- [ ] Review Kafka consumer lag
- [ ] Check disk usage and database size
- [ ] Review and respond to user feedback

### Monthly Tasks
- [ ] Security patches and dependency updates
- [ ] Database backup verification
- [ ] Disaster recovery drill
- [ ] Cost analysis and optimization
- [ ] Model retraining evaluation
- [ ] Performance optimization review
- [ ] Capacity planning review

---

## Disaster Recovery

### Backup Strategy

```bash
# Database backup script
#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="fantasy_bball_${DATE}.sql.gz"

# Create backup
pg_dump $DATABASE_URL | gzip > /tmp/$BACKUP_FILE

# Upload to S3
aws s3 cp /tmp/$BACKUP_FILE s3://your-backup-bucket/database/$BACKUP_FILE

# Retain last 30 days
aws s3 ls s3://your-backup-bucket/database/ | while read -r line; do
  createDate=$(echo "$line" | awk '{print $1}')
  fileName=$(echo "$line" | awk '{print $4}')
  if [[ $(date -d "$createDate" +%s) -lt $(date -d "-30 days" +%s) ]]; then
    aws s3 rm s3://your-backup-bucket/database/$fileName
  fi
done

# Cleanup
rm /tmp/$BACKUP_FILE
```

### Recovery Procedures

```bash
# Database recovery
#!/bin/bash

# Download latest backup
LATEST_BACKUP=$(aws s3 ls s3://your-backup-bucket/database/ | sort | tail -1 | awk '{print $4}')
aws s3 cp s3://your-backup-bucket/database/$LATEST_BACKUP /tmp/

# Restore
gunzip /tmp/$LATEST_BACKUP
psql $DATABASE_URL < /tmp/${LATEST_BACKUP%.gz}
```

### Incident Response Runbook

```markdown
## Incident Response Checklist

### 1. Detection
- [ ] Alert received (PagerDuty/Slack)
- [ ] Verify alert is not false positive
- [ ] Assess severity (P1/P2/P3)

### 2. Triage
- [ ] Check health endpoints
- [ ] Check Grafana dashboards
- [ ] Check recent deployments
- [ ] Check external dependencies (NBA API, Yahoo)

### 3. Communication
- [ ] Update status page
- [ ] Notify stakeholders (if P1)
- [ ] Create incident channel

### 4. Resolution
- [ ] Identify root cause
- [ ] Implement fix or rollback
- [ ] Verify fix
- [ ] Update status page

### 5. Post-Incident
- [ ] Write post-mortem
- [ ] Create follow-up tickets
- [ ] Update runbooks
```

---

This enhanced deployment guide covers the complete infrastructure for the Fantasy Basketball Analyzer with production-grade configurations for all components.
