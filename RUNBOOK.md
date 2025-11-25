# Fantasy Basketball Analyzer - Operations Runbook

> **Version**: 2.0
> **Last Updated**: 2024
> **Purpose**: Operations guide for deployment, maintenance, incident response, and troubleshooting

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Service Dependencies](#service-dependencies)
4. [Deployment Procedures](#deployment-procedures)
5. [Health Checks](#health-checks)
6. [Monitoring & Alerting](#monitoring--alerting)
7. [Incident Response](#incident-response)
8. [Common Issues & Resolutions](#common-issues--resolutions)
9. [Maintenance Procedures](#maintenance-procedures)
10. [Backup & Recovery](#backup--recovery)
11. [Scaling Operations](#scaling-operations)
12. [Security Operations](#security-operations)
13. [On-Call Procedures](#on-call-procedures)

---

## System Overview

### Service Components

| Service | Purpose | Port | Replicas | Critical |
|---------|---------|------|----------|----------|
| api-gateway | Request routing, rate limiting | 8080 | 3 | Yes |
| auth-service | Authentication, JWT management | 8001 | 2 | Yes |
| user-service | User management, preferences | 8002 | 2 | Yes |
| player-service | NBA player data, stats | 8003 | 3 | Yes |
| prediction-service | ML predictions, recommendations | 8004 | 3 | Yes |
| yahoo-service | Yahoo Fantasy integration | 8005 | 2 | Yes |
| notification-service | Push notifications, emails | 8006 | 2 | No |
| websocket-service | Real-time updates | 8007 | 3 | Yes |
| scheduler-service | Background jobs, cron tasks | 8008 | 1 | No |

### Infrastructure Components

| Component | Purpose | Version | Cluster |
|-----------|---------|---------|---------|
| PostgreSQL | Primary database | 15.x | 3-node |
| Redis | Cache, sessions, pub/sub | 7.x | 6-node |
| Kafka | Event streaming | 3.x | 3-broker |
| Elasticsearch | Search, logs | 8.x | 3-node |
| MinIO | Object storage | Latest | 4-node |

### External Dependencies

| Service | Purpose | SLA | Fallback |
|---------|---------|-----|----------|
| Yahoo Fantasy API | League data sync | 99.5% | Cached data |
| NBA Stats API | Live game data | 99.0% | Cached data |
| Firebase FCM | Push notifications | 99.9% | Email fallback |
| SendGrid | Email delivery | 99.95% | Queue & retry |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              LOAD BALANCER                                   │
│                         (AWS ALB / Cloudflare)                              │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│  API Gateway  │       │  API Gateway  │       │  API Gateway  │
│   (replica)   │       │   (replica)   │       │   (replica)   │
└───────┬───────┘       └───────┬───────┘       └───────┬───────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│ Auth Service  │       │Player Service │       │Predict Service│
└───────┬───────┘       └───────┬───────┘       └───────┬───────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                                ▼
        ┌───────────────────────────────────────────────┐
        │                MESSAGE BUS                     │
        │            (Kafka / Redis Pub/Sub)            │
        └───────────────────────┬───────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│  PostgreSQL   │       │    Redis      │       │ Elasticsearch │
│   (Primary)   │       │   (Cluster)   │       │   (Cluster)   │
└───────────────┘       └───────────────┘       └───────────────┘
```

---

## Service Dependencies

### Startup Order

```
1. Infrastructure (parallel):
   ├── PostgreSQL
   ├── Redis
   ├── Kafka
   └── Elasticsearch

2. Core Services (sequential):
   ├── auth-service (requires: PostgreSQL, Redis)
   ├── user-service (requires: auth-service, PostgreSQL)
   └── player-service (requires: PostgreSQL, Redis)

3. Feature Services (parallel):
   ├── prediction-service (requires: player-service)
   ├── yahoo-service (requires: user-service)
   └── notification-service (requires: Redis, Kafka)

4. Gateway Services:
   ├── websocket-service (requires: Redis, auth-service)
   └── api-gateway (requires: all services)

5. Background Services:
   └── scheduler-service (requires: all services)
```

### Shutdown Order

```
1. scheduler-service (graceful: 30s)
2. api-gateway (drain: 60s)
3. websocket-service (drain: 30s)
4. Feature services (parallel, graceful: 30s)
5. Core services (parallel, graceful: 30s)
6. Infrastructure (graceful: 60s)
```

---

## Deployment Procedures

### Pre-Deployment Checklist

```bash
# 1. Verify CI/CD pipeline status
kubectl get pods -n ci-cd

# 2. Check current cluster health
kubectl get nodes
kubectl top nodes

# 3. Verify database migrations are ready
./scripts/check-migrations.sh

# 4. Review deployment manifest changes
git diff HEAD~1 k8s/

# 5. Ensure rollback plan is documented
echo "Rollback commit: $(git rev-parse HEAD~1)"
```

### Standard Deployment

```bash
# Step 1: Deploy to staging
kubectl config use-context staging
./scripts/deploy.sh staging v2.1.0

# Step 2: Run smoke tests
./scripts/smoke-tests.sh staging

# Step 3: Deploy to production (canary)
kubectl config use-context production
./scripts/deploy-canary.sh production v2.1.0 10%

# Step 4: Monitor canary metrics (15 min)
./scripts/monitor-canary.sh

# Step 5: Progressive rollout
./scripts/deploy-canary.sh production v2.1.0 50%
# Wait 15 min, monitor
./scripts/deploy-canary.sh production v2.1.0 100%

# Step 6: Verify deployment
kubectl rollout status deployment/api-gateway -n production
```

### Database Migration Deployment

```bash
# Step 1: Create database backup
./scripts/backup-db.sh production pre-migration

# Step 2: Run migration in maintenance window
kubectl exec -it postgres-0 -n production -- \
  psql -U postgres -d fantasy -f /migrations/v2.1.0.sql

# Step 3: Verify migration
./scripts/verify-migration.sh v2.1.0

# Step 4: Deploy application
./scripts/deploy.sh production v2.1.0

# Step 5: Monitor for issues
./scripts/monitor-deployment.sh 30m
```

### Rollback Procedure

```bash
# Immediate rollback (< 5 min)
kubectl rollout undo deployment/api-gateway -n production

# Rollback to specific version
kubectl rollout undo deployment/api-gateway -n production --to-revision=5

# Database rollback (if needed)
./scripts/restore-db.sh production pre-migration

# Verify rollback
kubectl rollout status deployment/api-gateway -n production
./scripts/smoke-tests.sh production
```

### Zero-Downtime Deployment Config

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    spec:
      containers:
      - name: api-gateway
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          failureThreshold: 3
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          failureThreshold: 3
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]
      terminationGracePeriodSeconds: 60
```

---

## Health Checks

### Endpoint Reference

| Service | Liveness | Readiness | Metrics |
|---------|----------|-----------|---------|
| api-gateway | /health/live | /health/ready | /metrics |
| auth-service | /health/live | /health/ready | /metrics |
| player-service | /health/live | /health/ready | /metrics |
| prediction-service | /health/live | /health/ready | /metrics |
| websocket-service | /health/live | /health/ready | /metrics |

### Health Check Script

```bash
#!/bin/bash
# scripts/health-check.sh

SERVICES=(
  "api-gateway:8080"
  "auth-service:8001"
  "user-service:8002"
  "player-service:8003"
  "prediction-service:8004"
  "yahoo-service:8005"
  "notification-service:8006"
  "websocket-service:8007"
)

echo "=== Service Health Check ==="
echo "Time: $(date)"
echo ""

for service in "${SERVICES[@]}"; do
  name="${service%%:*}"
  port="${service##*:}"

  # Liveness check
  live=$(curl -s -o /dev/null -w "%{http_code}" \
    "http://${name}.default.svc.cluster.local:${port}/health/live")

  # Readiness check
  ready=$(curl -s -o /dev/null -w "%{http_code}" \
    "http://${name}.default.svc.cluster.local:${port}/health/ready")

  if [ "$live" = "200" ] && [ "$ready" = "200" ]; then
    echo "✅ ${name}: HEALTHY (live: ${live}, ready: ${ready})"
  else
    echo "❌ ${name}: UNHEALTHY (live: ${live}, ready: ${ready})"
  fi
done

echo ""
echo "=== Infrastructure Health ==="

# PostgreSQL
pg_status=$(kubectl exec postgres-0 -- pg_isready -U postgres 2>/dev/null && echo "OK" || echo "FAIL")
echo "PostgreSQL: ${pg_status}"

# Redis
redis_status=$(kubectl exec redis-0 -- redis-cli ping 2>/dev/null || echo "FAIL")
echo "Redis: ${redis_status}"

# Kafka
kafka_status=$(kubectl exec kafka-0 -- kafka-broker-api-versions.sh \
  --bootstrap-server localhost:9092 2>/dev/null && echo "OK" || echo "FAIL")
echo "Kafka: ${kafka_status}"
```

### Deep Health Check

```python
# scripts/deep_health_check.py

import asyncio
import aiohttp
import asyncpg
import redis.asyncio as redis
from datetime import datetime

async def check_database():
    """Verify database connectivity and performance"""
    try:
        conn = await asyncpg.connect(
            host='postgres-primary',
            database='fantasy',
            user='app_user',
            password='***'
        )

        # Check connection
        version = await conn.fetchval('SELECT version()')

        # Check replication lag
        lag = await conn.fetchval('''
            SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))
        ''')

        # Check connection count
        connections = await conn.fetchval('''
            SELECT count(*) FROM pg_stat_activity
        ''')

        await conn.close()

        return {
            'status': 'healthy',
            'version': version,
            'replication_lag_seconds': lag or 0,
            'active_connections': connections
        }
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}

async def check_redis():
    """Verify Redis cluster health"""
    try:
        r = redis.Redis(host='redis-cluster', port=6379)

        # Ping
        await r.ping()

        # Check memory
        info = await r.info('memory')

        # Check cluster
        cluster_info = await r.cluster_info()

        await r.close()

        return {
            'status': 'healthy',
            'used_memory_mb': info['used_memory'] / 1024 / 1024,
            'cluster_state': cluster_info.get('cluster_state', 'unknown')
        }
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}

async def check_external_apis():
    """Verify external API connectivity"""
    results = {}

    async with aiohttp.ClientSession() as session:
        # Yahoo API
        try:
            async with session.get(
                'https://fantasysports.yahooapis.com/fantasy/v2/users',
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                results['yahoo'] = {
                    'status': 'reachable' if resp.status in [200, 401] else 'unreachable',
                    'response_code': resp.status
                }
        except Exception as e:
            results['yahoo'] = {'status': 'unreachable', 'error': str(e)}

        # NBA Stats API
        try:
            async with session.get(
                'https://stats.nba.com/stats/commonallplayers',
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                results['nba'] = {
                    'status': 'reachable' if resp.status == 200 else 'unreachable',
                    'response_code': resp.status
                }
        except Exception as e:
            results['nba'] = {'status': 'unreachable', 'error': str(e)}

    return results

async def main():
    print(f"=== Deep Health Check ===")
    print(f"Time: {datetime.now().isoformat()}")
    print()

    db = await check_database()
    print(f"Database: {db}")

    cache = await check_redis()
    print(f"Redis: {cache}")

    external = await check_external_apis()
    print(f"External APIs: {external}")

if __name__ == '__main__':
    asyncio.run(main())
```

---

## Monitoring & Alerting

### Key Metrics

#### Service Level Indicators (SLIs)

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| API Latency (p99) | < 500ms | > 750ms | > 1000ms |
| API Error Rate | < 0.1% | > 0.5% | > 1% |
| API Availability | > 99.9% | < 99.5% | < 99% |
| Prediction Latency (p99) | < 2s | > 3s | > 5s |
| WebSocket Connections | - | > 80% capacity | > 95% capacity |
| Database Connections | - | > 70% pool | > 90% pool |
| Cache Hit Rate | > 90% | < 80% | < 70% |

#### Infrastructure Metrics

| Metric | Warning | Critical |
|--------|---------|----------|
| CPU Usage | > 70% | > 85% |
| Memory Usage | > 75% | > 90% |
| Disk Usage | > 70% | > 85% |
| Network I/O | > 80% capacity | > 95% capacity |
| Pod Restarts | > 3/hour | > 10/hour |

### Prometheus Alerts

```yaml
# prometheus/alerts.yaml

groups:
  - name: fantasy-analyzer-alerts
    rules:
      # High Error Rate
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) /
          sum(rate(http_requests_total[5m])) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"
          runbook: "https://runbook.fantasy/high-error-rate"

      # High Latency
      - alert: HighLatency
        expr: |
          histogram_quantile(0.99,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          ) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API latency detected"
          description: "P99 latency is {{ $value }}s"
          runbook: "https://runbook.fantasy/high-latency"

      # Database Connection Pool Exhaustion
      - alert: DatabaseConnectionPoolLow
        expr: |
          pg_stat_activity_count / pg_settings_max_connections > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "{{ $value | humanizePercentage }} connections used"
          runbook: "https://runbook.fantasy/db-connections"

      # Redis Memory High
      - alert: RedisMemoryHigh
        expr: |
          redis_memory_used_bytes / redis_memory_max_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Redis memory usage high"
          description: "Redis using {{ $value | humanizePercentage }} of max memory"
          runbook: "https://runbook.fantasy/redis-memory"

      # Prediction Service Degraded
      - alert: PredictionServiceDegraded
        expr: |
          sum(rate(prediction_requests_total{status="error"}[5m])) /
          sum(rate(prediction_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Prediction service experiencing errors"
          description: "{{ $value | humanizePercentage }} predictions failing"
          runbook: "https://runbook.fantasy/prediction-errors"

      # Yahoo API Errors
      - alert: YahooAPIErrors
        expr: |
          sum(rate(yahoo_api_requests_total{status="error"}[5m])) > 0.1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Yahoo API experiencing issues"
          description: "Yahoo API error rate elevated"
          runbook: "https://runbook.fantasy/yahoo-errors"

      # Pod Restart Loop
      - alert: PodRestartLoop
        expr: |
          increase(kube_pod_container_status_restarts_total[1h]) > 5
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Pod in restart loop"
          description: "Pod {{ $labels.pod }} has restarted {{ $value }} times"
          runbook: "https://runbook.fantasy/pod-restart"
```

### Grafana Dashboards

#### Main Dashboard Panels

```json
{
  "dashboard": {
    "title": "Fantasy Analyzer Overview",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [{
          "expr": "sum(rate(http_requests_total[5m])) by (service)"
        }]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [{
          "expr": "sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m]))"
        }]
      },
      {
        "title": "P99 Latency",
        "type": "graph",
        "targets": [{
          "expr": "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))"
        }]
      },
      {
        "title": "Active Users",
        "type": "stat",
        "targets": [{
          "expr": "sum(websocket_connections_active)"
        }]
      },
      {
        "title": "Predictions/min",
        "type": "stat",
        "targets": [{
          "expr": "sum(rate(prediction_requests_total[1m])) * 60"
        }]
      },
      {
        "title": "Cache Hit Rate",
        "type": "gauge",
        "targets": [{
          "expr": "sum(rate(redis_hits_total[5m])) / sum(rate(redis_commands_total[5m]))"
        }]
      }
    ]
  }
}
```

### PagerDuty Integration

```yaml
# alertmanager/config.yaml

global:
  pagerduty_url: 'https://events.pagerduty.com/v2/enqueue'

route:
  receiver: 'default'
  group_by: ['alertname', 'service']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
      continue: true
    - match:
        severity: warning
      receiver: 'slack-warnings'

receivers:
  - name: 'default'
    slack_configs:
      - channel: '#alerts-fantasy'
        send_resolved: true

  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: '<PAGERDUTY_SERVICE_KEY>'
        severity: critical
        description: '{{ .CommonAnnotations.summary }}'
        details:
          firing: '{{ .Alerts.Firing | len }}'
          resolved: '{{ .Alerts.Resolved | len }}'
          runbook: '{{ .CommonAnnotations.runbook }}'

  - name: 'slack-warnings'
    slack_configs:
      - channel: '#alerts-fantasy'
        send_resolved: true
        title: '{{ .CommonAnnotations.summary }}'
        text: '{{ .CommonAnnotations.description }}'
```

---

## Incident Response

### Severity Levels

| Level | Description | Response Time | Examples |
|-------|-------------|---------------|----------|
| SEV1 | Complete outage, all users affected | 15 min | API down, database failure |
| SEV2 | Major feature broken, many users affected | 30 min | Predictions unavailable |
| SEV3 | Minor feature broken, some users affected | 2 hours | Yahoo sync delayed |
| SEV4 | Minor issue, workaround available | 24 hours | UI glitch, slow reports |

### Incident Response Checklist

#### SEV1 - Complete Outage

```markdown
## Initial Response (0-15 min)
- [ ] Acknowledge incident in PagerDuty
- [ ] Join incident Slack channel #incident-response
- [ ] Assign Incident Commander (IC)
- [ ] Post initial status to status page
- [ ] Begin investigation

## Triage (15-30 min)
- [ ] Identify affected services
- [ ] Check recent deployments: `kubectl rollout history`
- [ ] Review error logs: `kubectl logs -l app=api-gateway --tail=500`
- [ ] Check infrastructure metrics
- [ ] Identify root cause or escalate

## Mitigation (30-60 min)
- [ ] Implement fix or rollback
- [ ] Verify service restoration
- [ ] Update status page
- [ ] Monitor for recurrence

## Post-Incident
- [ ] Schedule post-mortem (within 48 hours)
- [ ] Document timeline and actions
- [ ] Identify preventive measures
- [ ] Update runbooks if needed
```

### Incident Communication Template

```markdown
# Incident: [TITLE]

## Status: [INVESTIGATING | IDENTIFIED | MONITORING | RESOLVED]

**Started**: 2024-01-15 10:30 UTC
**Resolved**: 2024-01-15 11:15 UTC (if applicable)

### Impact
- Affected services: API, Predictions
- Affected users: ~5,000 (estimated)
- Duration: 45 minutes

### Summary
Brief description of what happened.

### Timeline
- 10:30 - Alert triggered for high error rate
- 10:35 - On-call engineer acknowledged
- 10:40 - Root cause identified (database connection exhaustion)
- 10:45 - Mitigation started (increase pool size)
- 11:00 - Service restored
- 11:15 - Confirmed stable, incident closed

### Root Cause
Database connection pool was exhausted due to connection leak in new code.

### Mitigation
- Increased connection pool size from 100 to 200
- Deployed hotfix to close leaked connections

### Follow-up Actions
- [ ] Add connection leak detection monitoring
- [ ] Review code for similar issues
- [ ] Add integration test for connection handling
```

---

## Common Issues & Resolutions

### Issue: High API Latency

**Symptoms**: P99 latency > 1s, slow user experience

**Diagnosis**:
```bash
# Check service latency breakdown
curl -s localhost:8080/metrics | grep http_request_duration

# Check database query times
kubectl exec -it postgres-0 -- psql -U postgres -c \
  "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Check Redis latency
kubectl exec -it redis-0 -- redis-cli --latency-history

# Check for goroutine leaks (Go services)
curl -s localhost:8080/debug/pprof/goroutine?debug=1 | head -50
```

**Resolution**:
```bash
# 1. Scale up if CPU/memory bound
kubectl scale deployment/api-gateway --replicas=5

# 2. Add database indexes if query slow
kubectl exec -it postgres-0 -- psql -U postgres -d fantasy -c \
  "CREATE INDEX CONCURRENTLY idx_stats_player_date ON player_game_stats(player_id, game_date);"

# 3. Increase cache TTL if cache miss rate high
kubectl set env deployment/api-gateway CACHE_TTL=600

# 4. Enable query result caching
kubectl set env deployment/player-service QUERY_CACHE_ENABLED=true
```

---

### Issue: Database Connection Pool Exhaustion

**Symptoms**: Connection errors, "too many connections" errors

**Diagnosis**:
```bash
# Check active connections
kubectl exec -it postgres-0 -- psql -U postgres -c \
  "SELECT count(*), state FROM pg_stat_activity GROUP BY state;"

# Check connection sources
kubectl exec -it postgres-0 -- psql -U postgres -c \
  "SELECT client_addr, count(*) FROM pg_stat_activity GROUP BY client_addr ORDER BY count DESC;"

# Check for long-running queries
kubectl exec -it postgres-0 -- psql -U postgres -c \
  "SELECT pid, now() - query_start as duration, query
   FROM pg_stat_activity
   WHERE state != 'idle'
   ORDER BY duration DESC LIMIT 10;"
```

**Resolution**:
```bash
# 1. Kill long-running queries
kubectl exec -it postgres-0 -- psql -U postgres -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity
   WHERE duration > interval '5 minutes' AND state != 'idle';"

# 2. Increase pool size (temporary)
kubectl set env deployment/api-gateway DB_POOL_SIZE=50

# 3. Restart PgBouncer
kubectl rollout restart deployment/pgbouncer

# 4. Identify and fix connection leaks
# Review recent deployments for connection handling issues
```

---

### Issue: Redis Memory Pressure

**Symptoms**: High memory usage, evictions, slow responses

**Diagnosis**:
```bash
# Check memory usage
kubectl exec -it redis-0 -- redis-cli INFO memory

# Check biggest keys
kubectl exec -it redis-0 -- redis-cli --bigkeys

# Check key count by pattern
kubectl exec -it redis-0 -- redis-cli DBSIZE

# Check eviction policy
kubectl exec -it redis-0 -- redis-cli CONFIG GET maxmemory-policy
```

**Resolution**:
```bash
# 1. Clear specific cache patterns
kubectl exec -it redis-0 -- redis-cli KEYS "cache:predictions:*" | xargs redis-cli DEL

# 2. Reduce TTL for large keys
kubectl set env deployment/prediction-service PREDICTION_CACHE_TTL=300

# 3. Scale Redis cluster (add nodes)
./scripts/scale-redis.sh add-node

# 4. Enable compression for large values
kubectl set env deployment/api-gateway REDIS_COMPRESSION=true
```

---

### Issue: Yahoo API Rate Limiting

**Symptoms**: Error code 5004, Yahoo sync failures

**Diagnosis**:
```bash
# Check Yahoo API metrics
curl -s localhost:8005/metrics | grep yahoo_api

# Check error logs
kubectl logs -l app=yahoo-service --tail=200 | grep -i "rate limit"

# Check request patterns
kubectl exec -it yahoo-service-0 -- cat /var/log/yahoo-requests.log | tail -100
```

**Resolution**:
```bash
# 1. Enable request throttling
kubectl set env deployment/yahoo-service YAHOO_RATE_LIMIT=50/minute

# 2. Increase sync interval
kubectl set env deployment/scheduler-service YAHOO_SYNC_INTERVAL=15m

# 3. Enable request batching
kubectl set env deployment/yahoo-service YAHOO_BATCH_ENABLED=true

# 4. Use cached data for non-critical requests
kubectl set env deployment/yahoo-service YAHOO_CACHE_FALLBACK=true
```

---

### Issue: ML Model Performance Degradation

**Symptoms**: High prediction latency, low accuracy, model errors

**Diagnosis**:
```bash
# Check model metrics
curl -s localhost:8004/metrics | grep model

# Check feature store latency
curl -s localhost:8004/metrics | grep feast

# Check model version
kubectl exec -it prediction-service-0 -- cat /models/version.txt

# Check model inference times
kubectl logs -l app=prediction-service --tail=200 | grep "inference_time"
```

**Resolution**:
```bash
# 1. Restart model server
kubectl rollout restart deployment/prediction-service

# 2. Roll back to previous model version
kubectl set env deployment/prediction-service MODEL_VERSION=v2.0.1

# 3. Scale prediction service
kubectl scale deployment/prediction-service --replicas=5

# 4. Enable model caching
kubectl set env deployment/prediction-service MODEL_CACHE_ENABLED=true
```

---

### Issue: WebSocket Connection Drops

**Symptoms**: Users disconnecting, reconnection storms

**Diagnosis**:
```bash
# Check WebSocket metrics
curl -s localhost:8007/metrics | grep websocket

# Check connection count
curl -s localhost:8007/ws/stats

# Check for memory pressure
kubectl top pods -l app=websocket-service

# Check logs for disconnection reasons
kubectl logs -l app=websocket-service --tail=500 | grep -i "disconnect\|close"
```

**Resolution**:
```bash
# 1. Scale WebSocket service
kubectl scale deployment/websocket-service --replicas=5

# 2. Increase connection limits
kubectl set env deployment/websocket-service MAX_CONNECTIONS=10000

# 3. Adjust heartbeat interval
kubectl set env deployment/websocket-service HEARTBEAT_INTERVAL=30s

# 4. Enable sticky sessions on load balancer
kubectl annotate service websocket-service \
  "service.beta.kubernetes.io/aws-load-balancer-stickiness-enabled=true"
```

---

## Maintenance Procedures

### Scheduled Maintenance Window

```bash
#!/bin/bash
# scripts/maintenance-start.sh

echo "Starting maintenance mode..."

# 1. Enable maintenance mode (returns 503 to new requests)
kubectl set env deployment/api-gateway MAINTENANCE_MODE=true

# 2. Drain existing connections (wait 60s)
echo "Draining connections..."
sleep 60

# 3. Update status page
curl -X POST https://status.fantasyanalyzer.com/api/incidents \
  -H "Authorization: Bearer $STATUS_PAGE_TOKEN" \
  -d '{"title": "Scheduled Maintenance", "status": "in_progress"}'

# 4. Scale down non-essential services
kubectl scale deployment/notification-service --replicas=0
kubectl scale deployment/scheduler-service --replicas=0

echo "Maintenance mode active. Proceed with maintenance tasks."
```

```bash
#!/bin/bash
# scripts/maintenance-end.sh

echo "Ending maintenance mode..."

# 1. Scale up services
kubectl scale deployment/notification-service --replicas=2
kubectl scale deployment/scheduler-service --replicas=1

# 2. Disable maintenance mode
kubectl set env deployment/api-gateway MAINTENANCE_MODE=false

# 3. Run health checks
./scripts/health-check.sh

# 4. Update status page
curl -X POST https://status.fantasyanalyzer.com/api/incidents \
  -H "Authorization: Bearer $STATUS_PAGE_TOKEN" \
  -d '{"status": "resolved"}'

echo "Maintenance complete. System operational."
```

### Database Maintenance

```bash
#!/bin/bash
# scripts/db-maintenance.sh

echo "Starting database maintenance..."

# 1. Run VACUUM ANALYZE on large tables
kubectl exec -it postgres-0 -- psql -U postgres -d fantasy -c \
  "VACUUM ANALYZE player_game_stats;"

kubectl exec -it postgres-0 -- psql -U postgres -d fantasy -c \
  "VACUUM ANALYZE player_predictions;"

# 2. Reindex critical indexes
kubectl exec -it postgres-0 -- psql -U postgres -d fantasy -c \
  "REINDEX INDEX CONCURRENTLY idx_stats_player_date;"

# 3. Update statistics
kubectl exec -it postgres-0 -- psql -U postgres -d fantasy -c \
  "ANALYZE;"

# 4. Check for bloated tables
kubectl exec -it postgres-0 -- psql -U postgres -d fantasy -c \
  "SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
   FROM pg_catalog.pg_statio_user_tables
   ORDER BY pg_total_relation_size(relid) DESC LIMIT 10;"

echo "Database maintenance complete."
```

### Log Rotation & Cleanup

```bash
#!/bin/bash
# scripts/log-cleanup.sh

# Delete logs older than 30 days from Elasticsearch
curl -X DELETE "elasticsearch:9200/logs-*-$(date -d '-30 days' +%Y.%m)*"

# Clean up old Kubernetes events
kubectl delete events --all-namespaces --field-selector 'lastTimestamp<2024-01-01T00:00:00Z'

# Prune Docker images
docker system prune -af --filter "until=720h"

# Clean up old backups (keep last 7)
aws s3 ls s3://fantasy-backups/db/ | sort -r | tail -n +8 | \
  awk '{print $4}' | xargs -I {} aws s3 rm s3://fantasy-backups/db/{}
```

---

## Backup & Recovery

### Backup Schedule

| Data | Frequency | Retention | Storage |
|------|-----------|-----------|---------|
| PostgreSQL (full) | Daily | 30 days | S3 |
| PostgreSQL (WAL) | Continuous | 7 days | S3 |
| Redis (RDB) | Hourly | 24 hours | S3 |
| Elasticsearch | Daily | 14 days | S3 |
| ML Models | On deploy | 10 versions | S3 |
| Config/Secrets | On change | 30 days | Vault |

### Backup Procedures

```bash
#!/bin/bash
# scripts/backup-db.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="fantasy_${TIMESTAMP}"
S3_BUCKET="s3://fantasy-backups/db"

echo "Starting PostgreSQL backup: ${BACKUP_NAME}"

# Create backup
kubectl exec -it postgres-0 -- pg_dump -U postgres -d fantasy -Fc > /tmp/${BACKUP_NAME}.dump

# Compress
gzip /tmp/${BACKUP_NAME}.dump

# Upload to S3
aws s3 cp /tmp/${BACKUP_NAME}.dump.gz ${S3_BUCKET}/${BACKUP_NAME}.dump.gz

# Verify upload
aws s3 ls ${S3_BUCKET}/${BACKUP_NAME}.dump.gz

# Cleanup
rm /tmp/${BACKUP_NAME}.dump.gz

echo "Backup complete: ${S3_BUCKET}/${BACKUP_NAME}.dump.gz"
```

### Recovery Procedures

```bash
#!/bin/bash
# scripts/restore-db.sh

BACKUP_NAME=$1
S3_BUCKET="s3://fantasy-backups/db"

if [ -z "$BACKUP_NAME" ]; then
  echo "Usage: ./restore-db.sh <backup_name>"
  echo "Available backups:"
  aws s3 ls ${S3_BUCKET}/ | tail -10
  exit 1
fi

echo "Starting restore from: ${BACKUP_NAME}"

# Download backup
aws s3 cp ${S3_BUCKET}/${BACKUP_NAME}.dump.gz /tmp/

# Decompress
gunzip /tmp/${BACKUP_NAME}.dump.gz

# Stop applications
kubectl scale deployment --all --replicas=0 -n production

# Restore database
kubectl exec -it postgres-0 -- dropdb -U postgres fantasy
kubectl exec -it postgres-0 -- createdb -U postgres fantasy
kubectl cp /tmp/${BACKUP_NAME}.dump postgres-0:/tmp/
kubectl exec -it postgres-0 -- pg_restore -U postgres -d fantasy /tmp/${BACKUP_NAME}.dump

# Run migrations (if needed)
./scripts/run-migrations.sh

# Restart applications
kubectl scale deployment --all --replicas=3 -n production

# Verify
./scripts/health-check.sh

echo "Restore complete."
```

### Point-in-Time Recovery

```bash
#!/bin/bash
# scripts/pitr-restore.sh

TARGET_TIME=$1  # Format: "2024-01-15 10:30:00"

echo "Restoring to: ${TARGET_TIME}"

# Stop replication
kubectl exec -it postgres-replica-0 -- pg_ctl stop

# Restore WAL to target time
kubectl exec -it postgres-replica-0 -- \
  pg_restore --target-time="${TARGET_TIME}" --target-action=promote

# Promote replica to primary
kubectl exec -it postgres-replica-0 -- pg_ctl promote

# Update service to point to new primary
kubectl patch service postgres -p '{"spec":{"selector":{"statefulset.kubernetes.io/pod-name":"postgres-replica-0"}}}'

echo "PITR complete. Verify data integrity."
```

---

## Scaling Operations

### Horizontal Pod Autoscaler Configuration

```yaml
# k8s/hpa.yaml

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
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
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "1000"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 100
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
```

### Manual Scaling Commands

```bash
# Scale specific service
kubectl scale deployment/api-gateway --replicas=10

# Scale all services proportionally
./scripts/scale-all.sh 2x

# Scale database read replicas
kubectl scale statefulset/postgres-replica --replicas=3

# Scale Redis cluster
./scripts/scale-redis.sh --nodes=9
```

### Database Scaling

```bash
#!/bin/bash
# scripts/scale-db-read-replicas.sh

REPLICA_COUNT=$1

echo "Scaling PostgreSQL read replicas to: ${REPLICA_COUNT}"

# Update StatefulSet
kubectl scale statefulset/postgres-replica --replicas=${REPLICA_COUNT}

# Wait for pods to be ready
kubectl rollout status statefulset/postgres-replica

# Update PgBouncer config
kubectl exec -it pgbouncer-0 -- pgbouncer reload

# Verify replication
for i in $(seq 0 $((REPLICA_COUNT-1))); do
  kubectl exec -it postgres-replica-${i} -- psql -U postgres -c \
    "SELECT pg_last_wal_replay_lsn(), pg_last_xact_replay_timestamp();"
done

echo "Scaling complete."
```

---

## Security Operations

### Secret Rotation

```bash
#!/bin/bash
# scripts/rotate-secrets.sh

echo "Rotating secrets..."

# 1. Generate new database password
NEW_DB_PASSWORD=$(openssl rand -base64 32)

# 2. Update database user
kubectl exec -it postgres-0 -- psql -U postgres -c \
  "ALTER USER app_user WITH PASSWORD '${NEW_DB_PASSWORD}';"

# 3. Update Kubernetes secret
kubectl create secret generic db-credentials \
  --from-literal=password=${NEW_DB_PASSWORD} \
  --dry-run=client -o yaml | kubectl apply -f -

# 4. Rolling restart of services
kubectl rollout restart deployment/api-gateway
kubectl rollout restart deployment/auth-service

# 5. Verify connectivity
./scripts/health-check.sh

echo "Secret rotation complete."
```

### Security Audit

```bash
#!/bin/bash
# scripts/security-audit.sh

echo "=== Security Audit Report ==="
echo "Date: $(date)"
echo ""

# Check for exposed secrets
echo "## Secrets Check"
kubectl get secrets -A -o json | jq '.items[] | select(.data != null) | .metadata.name'

# Check pod security policies
echo "## Pod Security"
kubectl get pods -A -o json | jq '.items[] | select(.spec.containers[].securityContext.privileged == true) | .metadata.name'

# Check network policies
echo "## Network Policies"
kubectl get networkpolicies -A

# Check RBAC
echo "## RBAC Check"
kubectl auth can-i --list --as=system:serviceaccount:default:default

# Check for outdated images
echo "## Image Versions"
kubectl get pods -A -o jsonpath='{range .items[*]}{.spec.containers[*].image}{"\n"}{end}' | sort | uniq -c

# Check TLS certificates
echo "## Certificate Expiry"
kubectl get certificates -A -o jsonpath='{range .items[*]}{.metadata.name}: {.status.notAfter}{"\n"}{end}'

echo ""
echo "=== Audit Complete ==="
```

### Vulnerability Scanning

```bash
#!/bin/bash
# scripts/vulnerability-scan.sh

echo "Running vulnerability scan..."

# Scan container images
for image in $(kubectl get pods -o jsonpath='{.items[*].spec.containers[*].image}' | tr ' ' '\n' | sort -u); do
  echo "Scanning: ${image}"
  trivy image --severity HIGH,CRITICAL ${image}
done

# Scan Kubernetes manifests
trivy config ./k8s/

# Check for CVEs in dependencies
./scripts/check-dependencies.sh

echo "Vulnerability scan complete."
```

---

## On-Call Procedures

### On-Call Rotation

| Week | Primary | Secondary | Escalation |
|------|---------|-----------|------------|
| 1 | Alice | Bob | Charlie |
| 2 | Bob | Charlie | Alice |
| 3 | Charlie | Alice | Bob |
| 4 | Alice | Bob | Charlie |

### On-Call Checklist

```markdown
## Start of Shift
- [ ] Check PagerDuty schedule
- [ ] Review active incidents
- [ ] Check recent deployments
- [ ] Review system health dashboard
- [ ] Ensure VPN access working
- [ ] Test alerting phone number

## During Shift
- [ ] Acknowledge alerts within 5 minutes
- [ ] Update incident channel with progress
- [ ] Escalate if needed after 30 minutes
- [ ] Document all actions taken

## End of Shift
- [ ] Handoff active incidents
- [ ] Update runbook with new learnings
- [ ] Complete shift summary
- [ ] Clear any test alerts
```

### Escalation Matrix

| Time | Action | Contact |
|------|--------|---------|
| 0-15 min | Primary on-call responds | PagerDuty |
| 15-30 min | Secondary engaged | PagerDuty |
| 30-60 min | Engineering lead notified | Slack + Phone |
| 60+ min | VP Engineering + Director | Phone |

### Contact Information

```yaml
# Keep in secure location (e.g., 1Password)
contacts:
  engineering_lead:
    name: "Engineering Lead"
    phone: "+1-xxx-xxx-xxxx"
    slack: "@eng-lead"

  vp_engineering:
    name: "VP Engineering"
    phone: "+1-xxx-xxx-xxxx"
    slack: "@vp-eng"

  database_admin:
    name: "DBA"
    phone: "+1-xxx-xxx-xxxx"
    slack: "@dba"

  vendor_support:
    aws:
      account: "Premium Support"
      phone: "+1-xxx-xxx-xxxx"
    yahoo_api:
      email: "fantasy-api-support@yahoo.com"
```

---

## Quick Reference Commands

### Status Commands

```bash
# Overall cluster status
kubectl get nodes && kubectl get pods -A | grep -v Running

# Service health
./scripts/health-check.sh

# Recent events
kubectl get events --sort-by='.lastTimestamp' | tail -20

# Resource usage
kubectl top nodes && kubectl top pods
```

### Emergency Commands

```bash
# Immediate rollback
kubectl rollout undo deployment/api-gateway

# Kill runaway pod
kubectl delete pod <pod-name> --grace-period=0 --force

# Enable maintenance mode
kubectl set env deployment/api-gateway MAINTENANCE_MODE=true

# Scale to handle load
kubectl scale deployment/api-gateway --replicas=20

# Drain node for maintenance
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data
```

### Debugging Commands

```bash
# Pod logs
kubectl logs -f <pod-name> --tail=100

# Previous pod logs (after crash)
kubectl logs <pod-name> --previous

# Exec into pod
kubectl exec -it <pod-name> -- /bin/sh

# Port forward for debugging
kubectl port-forward <pod-name> 8080:8080

# Describe pod (events, status)
kubectl describe pod <pod-name>
```

---

**Document Version**: 2.0
**Maintainer**: SRE Team
**Last Review**: 2024
**Next Review**: Quarterly
