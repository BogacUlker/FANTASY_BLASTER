# Fantasy Basketball Analyzer - Error Codes Reference

> **Version**: 2.0
> **Last Updated**: 2024
> **Purpose**: Comprehensive API error codes, troubleshooting guides, and resolution procedures

---

## Table of Contents

1. [Error Code Format](#error-code-format)
2. [HTTP Status Code Mapping](#http-status-code-mapping)
3. [Authentication Errors (1xxx)](#authentication-errors-1xxx)
4. [Authorization Errors (2xxx)](#authorization-errors-2xxx)
5. [Validation Errors (3xxx)](#validation-errors-3xxx)
6. [Resource Errors (4xxx)](#resource-errors-4xxx)
7. [External Service Errors (5xxx)](#external-service-errors-5xxx)
8. [Database Errors (6xxx)](#database-errors-6xxx)
9. [Cache Errors (7xxx)](#cache-errors-7xxx)
10. [ML/Prediction Errors (8xxx)](#mlprediction-errors-8xxx)
11. [WebSocket Errors (9xxx)](#websocket-errors-9xxx)
12. [Rate Limiting Errors (10xxx)](#rate-limiting-errors-10xxx)
13. [System Errors (11xxx)](#system-errors-11xxx)
14. [Error Response Format](#error-response-format)
15. [Troubleshooting Guide](#troubleshooting-guide)
16. [Client-Side Error Handling](#client-side-error-handling)

---

## Error Code Format

```
[Category][Subcategory][Sequence]
    │         │          │
    │         │          └── 01-99: Specific error within subcategory
    │         └── 0-9: Subcategory within domain
    └── 1-11: Error category/domain
```

### Example
```
Error Code: 1201
    │ │  │
    │ │  └── 01: First error in subcategory
    │ └── 2: Token-related subcategory
    └── 1: Authentication domain
```

---

## HTTP Status Code Mapping

| HTTP Status | Error Code Range | Description |
|-------------|------------------|-------------|
| 400 | 3xxx | Bad Request - Validation errors |
| 401 | 1xxx | Unauthorized - Authentication errors |
| 403 | 2xxx | Forbidden - Authorization errors |
| 404 | 4xxx | Not Found - Resource errors |
| 409 | 4xxx | Conflict - Resource state conflicts |
| 422 | 3xxx | Unprocessable Entity - Business logic validation |
| 429 | 10xxx | Too Many Requests - Rate limiting |
| 500 | 6xxx, 11xxx | Internal Server Error |
| 502 | 5xxx | Bad Gateway - External service errors |
| 503 | 5xxx, 7xxx | Service Unavailable |
| 504 | 5xxx | Gateway Timeout |

---

## Authentication Errors (1xxx)

### 1.1 Login Errors (10xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 1001 | INVALID_CREDENTIALS | 401 | Email or password is incorrect | Verify credentials and retry |
| 1002 | ACCOUNT_DISABLED | 401 | User account has been disabled | Contact support |
| 1003 | ACCOUNT_LOCKED | 401 | Account locked due to too many failed attempts | Wait 15 minutes or reset password |
| 1004 | EMAIL_NOT_VERIFIED | 401 | Email address not verified | Check email for verification link |
| 1005 | MFA_REQUIRED | 401 | Multi-factor authentication required | Provide MFA code |
| 1006 | MFA_INVALID | 401 | Invalid MFA code | Retry with correct code |
| 1007 | MFA_EXPIRED | 401 | MFA code has expired | Request new code |
| 1008 | PASSWORD_EXPIRED | 401 | Password has expired | Reset password |
| 1009 | SESSION_EXPIRED | 401 | Login session has expired | Re-authenticate |

### 1.2 Token Errors (12xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 1201 | TOKEN_MISSING | 401 | Authorization header missing | Include Bearer token |
| 1202 | TOKEN_INVALID | 401 | Token format is invalid | Use valid JWT token |
| 1203 | TOKEN_EXPIRED | 401 | Access token has expired | Refresh token or re-login |
| 1204 | TOKEN_REVOKED | 401 | Token has been revoked | Re-authenticate |
| 1205 | TOKEN_NOT_YET_VALID | 401 | Token not yet valid (nbf claim) | Check system clock sync |
| 1206 | REFRESH_TOKEN_INVALID | 401 | Refresh token is invalid | Re-authenticate |
| 1207 | REFRESH_TOKEN_EXPIRED | 401 | Refresh token has expired | Re-authenticate |
| 1208 | REFRESH_TOKEN_REUSED | 401 | Refresh token already used (replay attack) | Re-authenticate, check for compromise |
| 1209 | TOKEN_SIGNATURE_INVALID | 401 | Token signature verification failed | Token may be tampered |

### 1.3 OAuth Errors (13xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 1301 | OAUTH_STATE_MISMATCH | 401 | OAuth state parameter mismatch | Restart OAuth flow |
| 1302 | OAUTH_CODE_INVALID | 401 | Authorization code invalid or expired | Restart OAuth flow |
| 1303 | OAUTH_TOKEN_EXCHANGE_FAILED | 502 | Failed to exchange code for tokens | Retry or contact support |
| 1304 | YAHOO_AUTH_REQUIRED | 401 | Yahoo authentication required | Link Yahoo account |
| 1305 | YAHOO_TOKEN_EXPIRED | 401 | Yahoo OAuth token expired | Re-authorize Yahoo |
| 1306 | YAHOO_TOKEN_REVOKED | 401 | Yahoo authorization revoked | Re-authorize Yahoo |
| 1307 | OAUTH_PROVIDER_ERROR | 502 | OAuth provider returned error | Retry later |

---

## Authorization Errors (2xxx)

### 2.1 Permission Errors (20xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 2001 | PERMISSION_DENIED | 403 | User lacks required permission | Request access from admin |
| 2002 | ROLE_INSUFFICIENT | 403 | User role insufficient for action | Upgrade account or request role |
| 2003 | RESOURCE_NOT_OWNED | 403 | User doesn't own the resource | Access only your resources |
| 2004 | ACTION_NOT_ALLOWED | 403 | Action not allowed in current state | Check resource state |
| 2005 | SUBSCRIPTION_REQUIRED | 403 | Premium subscription required | Upgrade subscription |
| 2006 | TRIAL_EXPIRED | 403 | Trial period has expired | Subscribe to continue |
| 2007 | FEATURE_DISABLED | 403 | Feature disabled for account | Contact support |

### 2.2 League Access Errors (21xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 2101 | LEAGUE_ACCESS_DENIED | 403 | Not a member of this league | Join league or request access |
| 2102 | LEAGUE_MANAGER_REQUIRED | 403 | League manager role required | Contact league manager |
| 2103 | LEAGUE_NOT_PUBLIC | 403 | League is private | Request invitation |
| 2104 | TEAM_ACCESS_DENIED | 403 | Not owner of this team | Access only your teams |
| 2105 | DRAFT_ACCESS_DENIED | 403 | Cannot access draft in current phase | Wait for draft to start |

### 2.3 API Access Errors (22xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 2201 | API_KEY_INVALID | 403 | API key is invalid | Use valid API key |
| 2202 | API_KEY_DISABLED | 403 | API key has been disabled | Generate new API key |
| 2203 | IP_NOT_WHITELISTED | 403 | IP address not in whitelist | Add IP to whitelist |
| 2204 | CORS_ORIGIN_DENIED | 403 | Origin not allowed | Add origin to allowed list |

---

## Validation Errors (3xxx)

### 3.1 Input Validation (30xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 3001 | VALIDATION_ERROR | 400 | General validation error | Check error details |
| 3002 | REQUIRED_FIELD_MISSING | 400 | Required field is missing | Provide required field |
| 3003 | INVALID_FORMAT | 400 | Field format is invalid | Use correct format |
| 3004 | INVALID_TYPE | 400 | Field type is incorrect | Use correct data type |
| 3005 | VALUE_OUT_OF_RANGE | 400 | Value outside allowed range | Use value within range |
| 3006 | STRING_TOO_SHORT | 400 | String below minimum length | Provide longer value |
| 3007 | STRING_TOO_LONG | 400 | String exceeds maximum length | Shorten value |
| 3008 | INVALID_EMAIL | 400 | Email format is invalid | Use valid email format |
| 3009 | INVALID_DATE | 400 | Date format is invalid | Use ISO 8601 format |
| 3010 | INVALID_UUID | 400 | UUID format is invalid | Use valid UUID v4 |
| 3011 | INVALID_ENUM_VALUE | 400 | Value not in allowed enum | Use allowed value |
| 3012 | ARRAY_TOO_SHORT | 400 | Array below minimum items | Add more items |
| 3013 | ARRAY_TOO_LONG | 400 | Array exceeds maximum items | Reduce items |
| 3014 | DUPLICATE_VALUE | 400 | Duplicate value not allowed | Use unique values |

### 3.2 Business Validation (31xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 3101 | ROSTER_FULL | 422 | Team roster is at maximum capacity | Drop a player first |
| 3102 | POSITION_FILLED | 422 | Position already filled in lineup | Move existing player |
| 3103 | PLAYER_NOT_ELIGIBLE | 422 | Player not eligible for position | Use eligible position |
| 3104 | TRADE_DEADLINE_PASSED | 422 | Trade deadline has passed | No trades until next season |
| 3105 | WAIVER_PERIOD_ACTIVE | 422 | Player on waivers | Wait for waiver period |
| 3106 | BUDGET_EXCEEDED | 422 | Transaction exceeds budget | Adjust transaction |
| 3107 | LINEUP_INCOMPLETE | 422 | Lineup has empty required positions | Fill all positions |
| 3108 | PLAYER_INJURED | 422 | Player has injury status | Consider injury status |
| 3109 | GAME_ALREADY_STARTED | 422 | Cannot modify after game start | Wait for next period |
| 3110 | MATCHUP_LOCKED | 422 | Matchup is locked | Cannot modify locked matchup |
| 3111 | INVALID_TRADE_PROPOSAL | 422 | Trade proposal is invalid | Check trade rules |
| 3112 | INSUFFICIENT_PLAYERS | 422 | Not enough players for transaction | Add more players |

### 3.3 Query Validation (32xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 3201 | INVALID_SORT_FIELD | 400 | Sort field not allowed | Use allowed sort field |
| 3202 | INVALID_FILTER_OPERATOR | 400 | Filter operator not supported | Use supported operator |
| 3203 | PAGE_SIZE_EXCEEDED | 400 | Page size exceeds maximum | Reduce page size |
| 3204 | INVALID_DATE_RANGE | 400 | Date range is invalid | Use valid date range |
| 3205 | SEARCH_QUERY_TOO_SHORT | 400 | Search query too short | Use at least 2 characters |
| 3206 | INVALID_AGGREGATION | 400 | Aggregation not supported | Use supported aggregation |

---

## Resource Errors (4xxx)

### 4.1 Not Found Errors (40xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 4001 | RESOURCE_NOT_FOUND | 404 | Requested resource not found | Verify resource ID |
| 4002 | USER_NOT_FOUND | 404 | User does not exist | Check user ID |
| 4003 | PLAYER_NOT_FOUND | 404 | NBA player not found | Verify player ID |
| 4004 | TEAM_NOT_FOUND | 404 | Team not found | Verify team ID |
| 4005 | LEAGUE_NOT_FOUND | 404 | Fantasy league not found | Verify league ID |
| 4006 | MATCHUP_NOT_FOUND | 404 | Matchup not found | Verify matchup ID |
| 4007 | PREDICTION_NOT_FOUND | 404 | Prediction not found | Verify prediction ID |
| 4008 | GAME_NOT_FOUND | 404 | NBA game not found | Verify game ID |
| 4009 | SEASON_NOT_FOUND | 404 | Season data not found | Verify season year |
| 4010 | RECOMMENDATION_NOT_FOUND | 404 | Recommendation not found | Verify recommendation ID |

### 4.2 Conflict Errors (41xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 4101 | RESOURCE_ALREADY_EXISTS | 409 | Resource already exists | Use existing resource |
| 4102 | EMAIL_ALREADY_REGISTERED | 409 | Email already registered | Use different email or login |
| 4103 | USERNAME_TAKEN | 409 | Username already taken | Choose different username |
| 4104 | PLAYER_ALREADY_ROSTERED | 409 | Player already on a roster | Choose different player |
| 4105 | LEAGUE_ALREADY_JOINED | 409 | Already a member of league | Access existing membership |
| 4106 | CONCURRENT_MODIFICATION | 409 | Resource modified by another request | Refresh and retry |
| 4107 | OPTIMISTIC_LOCK_FAILED | 409 | Version conflict detected | Refresh and retry |
| 4108 | DUPLICATE_TRANSACTION | 409 | Duplicate transaction detected | Transaction already processed |

### 4.3 State Errors (42xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 4201 | INVALID_STATE_TRANSITION | 409 | Invalid state transition | Check current state |
| 4202 | RESOURCE_ARCHIVED | 410 | Resource has been archived | Resource no longer available |
| 4203 | RESOURCE_DELETED | 410 | Resource has been deleted | Resource permanently removed |
| 4204 | LEAGUE_SEASON_ENDED | 409 | League season has ended | Wait for new season |
| 4205 | DRAFT_COMPLETED | 409 | Draft has already completed | Draft no longer available |
| 4206 | MATCHUP_FINALIZED | 409 | Matchup has been finalized | Cannot modify finalized matchup |

---

## External Service Errors (5xxx)

### 5.1 Yahoo API Errors (50xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 5001 | YAHOO_API_ERROR | 502 | Yahoo API returned error | Retry later |
| 5002 | YAHOO_API_TIMEOUT | 504 | Yahoo API request timed out | Retry later |
| 5003 | YAHOO_API_UNAVAILABLE | 503 | Yahoo API is unavailable | Check Yahoo status |
| 5004 | YAHOO_RATE_LIMITED | 429 | Yahoo API rate limit exceeded | Wait before retrying |
| 5005 | YAHOO_DATA_SYNC_FAILED | 502 | Failed to sync Yahoo data | Manual sync required |
| 5006 | YAHOO_LEAGUE_NOT_FOUND | 404 | Yahoo league not found | Verify league key |
| 5007 | YAHOO_INVALID_RESPONSE | 502 | Invalid response from Yahoo | Contact support |

### 5.2 NBA API Errors (51xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 5101 | NBA_API_ERROR | 502 | NBA API returned error | Retry later |
| 5102 | NBA_API_TIMEOUT | 504 | NBA API request timed out | Retry later |
| 5103 | NBA_API_UNAVAILABLE | 503 | NBA API is unavailable | Using cached data |
| 5104 | NBA_DATA_STALE | 200 | NBA data may be outdated | Refresh pending |
| 5105 | NBA_GAME_NOT_STARTED | 200 | Game has not started yet | Stats unavailable |
| 5106 | NBA_OFFSEASON | 200 | NBA offseason - limited data | Historical data only |

### 5.3 Third-Party Service Errors (52xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 5201 | EMAIL_SERVICE_ERROR | 502 | Email service error | Retry later |
| 5202 | SMS_SERVICE_ERROR | 502 | SMS service error | Retry later |
| 5203 | PUSH_NOTIFICATION_FAILED | 502 | Push notification failed | Check device registration |
| 5204 | STORAGE_SERVICE_ERROR | 502 | Cloud storage error | Retry later |
| 5205 | ANALYTICS_SERVICE_ERROR | 502 | Analytics service error | Non-critical, continuing |
| 5206 | PAYMENT_GATEWAY_ERROR | 502 | Payment processing error | Retry or use different method |

---

## Database Errors (6xxx)

### 6.1 Connection Errors (60xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 6001 | DB_CONNECTION_FAILED | 503 | Database connection failed | Retry later |
| 6002 | DB_CONNECTION_TIMEOUT | 504 | Database connection timed out | Retry later |
| 6003 | DB_POOL_EXHAUSTED | 503 | Connection pool exhausted | Retry later |
| 6004 | DB_READ_REPLICA_UNAVAILABLE | 503 | Read replica unavailable | Using primary |
| 6005 | DB_PRIMARY_UNAVAILABLE | 503 | Primary database unavailable | Service degraded |

### 6.2 Query Errors (61xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 6101 | DB_QUERY_FAILED | 500 | Database query failed | Contact support |
| 6102 | DB_QUERY_TIMEOUT | 504 | Query execution timed out | Simplify query |
| 6103 | DB_DEADLOCK_DETECTED | 500 | Database deadlock detected | Automatic retry |
| 6104 | DB_CONSTRAINT_VIOLATION | 409 | Constraint violation | Check data integrity |
| 6105 | DB_UNIQUE_VIOLATION | 409 | Unique constraint violation | Use unique value |
| 6106 | DB_FOREIGN_KEY_VIOLATION | 409 | Foreign key violation | Check references |

### 6.3 Transaction Errors (62xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 6201 | DB_TRANSACTION_FAILED | 500 | Transaction failed | Automatic rollback |
| 6202 | DB_TRANSACTION_TIMEOUT | 504 | Transaction timed out | Retry operation |
| 6203 | DB_SERIALIZATION_FAILURE | 500 | Serialization failure | Automatic retry |
| 6204 | DB_ROLLBACK_FAILED | 500 | Rollback failed | Contact support |

---

## Cache Errors (7xxx)

### 7.1 Redis Errors (70xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 7001 | CACHE_CONNECTION_FAILED | 503 | Redis connection failed | Using database fallback |
| 7002 | CACHE_TIMEOUT | 504 | Cache operation timed out | Using database fallback |
| 7003 | CACHE_CLUSTER_UNAVAILABLE | 503 | Redis cluster unavailable | Service degraded |
| 7004 | CACHE_MEMORY_EXCEEDED | 503 | Redis memory limit exceeded | Cache eviction active |
| 7005 | CACHE_KEY_NOT_FOUND | 200 | Cache miss (not an error) | Fetching from source |

### 7.2 Cache Consistency Errors (71xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 7101 | CACHE_INVALIDATION_FAILED | 500 | Cache invalidation failed | Manual refresh may be needed |
| 7102 | CACHE_SYNC_FAILED | 500 | Cache sync failed | Data may be stale |
| 7103 | CACHE_VERSION_MISMATCH | 409 | Cache version conflict | Refreshing cache |

---

## ML/Prediction Errors (8xxx)

### 8.1 Model Errors (80xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 8001 | MODEL_NOT_FOUND | 404 | ML model not found | Check model version |
| 8002 | MODEL_LOADING_FAILED | 503 | Failed to load ML model | Using fallback model |
| 8003 | MODEL_VERSION_MISMATCH | 500 | Model version incompatible | Update required |
| 8004 | MODEL_INFERENCE_FAILED | 500 | Model inference failed | Using fallback |
| 8005 | MODEL_TIMEOUT | 504 | Model inference timed out | Retry with simpler request |

### 8.2 Prediction Errors (81xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 8101 | INSUFFICIENT_DATA | 422 | Not enough data for prediction | Need more historical data |
| 8102 | PREDICTION_UNAVAILABLE | 503 | Predictions temporarily unavailable | Retry later |
| 8103 | PLAYER_DATA_INSUFFICIENT | 422 | Insufficient player statistics | New player or limited history |
| 8104 | FEATURE_EXTRACTION_FAILED | 500 | Feature extraction failed | Contact support |
| 8105 | CONFIDENCE_TOO_LOW | 200 | Prediction confidence below threshold | Result may be unreliable |
| 8106 | ENSEMBLE_DISAGREEMENT | 200 | Model ensemble disagreement | Higher uncertainty |

### 8.3 Feature Store Errors (82xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 8201 | FEATURE_STORE_UNAVAILABLE | 503 | Feature store unavailable | Using cached features |
| 8202 | FEATURE_NOT_FOUND | 404 | Required feature not found | Feature may be deprecated |
| 8203 | FEATURE_STALE | 200 | Feature data is stale | Refresh in progress |
| 8204 | FEATURE_COMPUTATION_FAILED | 500 | Feature computation failed | Using fallback |

---

## WebSocket Errors (9xxx)

### 9.1 Connection Errors (90xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 9001 | WS_CONNECTION_FAILED | - | WebSocket connection failed | Check network and retry |
| 9002 | WS_CONNECTION_CLOSED | - | WebSocket connection closed | Automatic reconnection |
| 9003 | WS_AUTHENTICATION_FAILED | - | WebSocket authentication failed | Re-authenticate |
| 9004 | WS_MAX_CONNECTIONS | - | Maximum connections reached | Close unused connections |
| 9005 | WS_INVALID_PROTOCOL | - | Invalid WebSocket protocol | Use correct protocol |

### 9.2 Subscription Errors (91xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 9101 | WS_SUBSCRIPTION_FAILED | - | Channel subscription failed | Verify channel name |
| 9102 | WS_CHANNEL_NOT_FOUND | - | Channel does not exist | Use valid channel |
| 9103 | WS_SUBSCRIPTION_LIMIT | - | Subscription limit reached | Unsubscribe unused channels |
| 9104 | WS_UNAUTHORIZED_CHANNEL | - | Not authorized for channel | Check permissions |

### 9.3 Message Errors (92xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 9201 | WS_MESSAGE_TOO_LARGE | - | Message exceeds size limit | Reduce message size |
| 9202 | WS_INVALID_MESSAGE | - | Invalid message format | Use correct format |
| 9203 | WS_MESSAGE_RATE_LIMITED | - | Message rate limit exceeded | Slow down messages |
| 9204 | WS_BROADCAST_FAILED | - | Broadcast delivery failed | Partial delivery |

---

## Rate Limiting Errors (10xxx)

### 10.1 API Rate Limits (100xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 10001 | RATE_LIMIT_EXCEEDED | 429 | API rate limit exceeded | Wait and retry |
| 10002 | BURST_LIMIT_EXCEEDED | 429 | Burst limit exceeded | Slow down requests |
| 10003 | DAILY_LIMIT_EXCEEDED | 429 | Daily request limit exceeded | Wait until reset |
| 10004 | CONCURRENT_LIMIT_EXCEEDED | 429 | Too many concurrent requests | Reduce parallelism |

### 10.2 User Rate Limits (101xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 10101 | USER_RATE_LIMITED | 429 | User-specific rate limit | Wait before retrying |
| 10102 | LOGIN_ATTEMPTS_EXCEEDED | 429 | Too many login attempts | Wait 15 minutes |
| 10103 | PASSWORD_RESET_LIMITED | 429 | Too many password reset requests | Wait before retry |
| 10104 | VERIFICATION_CODE_LIMITED | 429 | Too many verification requests | Wait before retry |

### 10.3 Resource Rate Limits (102xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 10201 | PREDICTION_RATE_LIMITED | 429 | Prediction request limit | Wait or upgrade |
| 10202 | SYNC_RATE_LIMITED | 429 | Sync request limit | Wait before syncing |
| 10203 | EXPORT_RATE_LIMITED | 429 | Export request limit | Wait before exporting |
| 10204 | SEARCH_RATE_LIMITED | 429 | Search request limit | Wait before searching |

---

## System Errors (11xxx)

### 11.1 Server Errors (110xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 11001 | INTERNAL_ERROR | 500 | Internal server error | Contact support |
| 11002 | SERVICE_UNAVAILABLE | 503 | Service temporarily unavailable | Retry later |
| 11003 | MAINTENANCE_MODE | 503 | System under maintenance | Wait for completion |
| 11004 | OVERLOADED | 503 | System overloaded | Retry with backoff |
| 11005 | DEPENDENCY_FAILED | 500 | Internal dependency failed | Contact support |

### 11.2 Configuration Errors (111xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 11101 | CONFIG_ERROR | 500 | Configuration error | Contact support |
| 11102 | FEATURE_FLAG_ERROR | 500 | Feature flag error | Contact support |
| 11103 | ENVIRONMENT_ERROR | 500 | Environment misconfiguration | Contact support |

### 11.3 Processing Errors (112xx)

| Code | Name | HTTP | Description | Resolution |
|------|------|------|-------------|------------|
| 11201 | QUEUE_FULL | 503 | Processing queue full | Retry later |
| 11202 | WORKER_UNAVAILABLE | 503 | Background worker unavailable | Retry later |
| 11203 | JOB_FAILED | 500 | Background job failed | Check job status |
| 11204 | TIMEOUT_ERROR | 504 | Operation timed out | Retry with smaller payload |

---

## Error Response Format

### Standard Error Response

```json
{
  "error": {
    "code": 1203,
    "name": "TOKEN_EXPIRED",
    "message": "Access token has expired",
    "details": {
      "expired_at": "2024-01-15T10:30:00Z",
      "token_type": "access"
    },
    "help_url": "https://docs.fantasyanalyzer.com/errors/1203",
    "request_id": "req_abc123xyz",
    "timestamp": "2024-01-15T10:35:00Z"
  }
}
```

### Validation Error Response

```json
{
  "error": {
    "code": 3001,
    "name": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "fields": [
        {
          "field": "email",
          "code": 3008,
          "message": "Invalid email format",
          "value": "invalid-email"
        },
        {
          "field": "password",
          "code": 3006,
          "message": "Password must be at least 8 characters",
          "constraint": {
            "min_length": 8,
            "actual_length": 5
          }
        }
      ]
    },
    "request_id": "req_def456uvw",
    "timestamp": "2024-01-15T10:35:00Z"
  }
}
```

### Rate Limit Error Response

```json
{
  "error": {
    "code": 10001,
    "name": "RATE_LIMIT_EXCEEDED",
    "message": "API rate limit exceeded",
    "details": {
      "limit": 100,
      "window": "1m",
      "remaining": 0,
      "reset_at": "2024-01-15T10:36:00Z",
      "retry_after": 25
    },
    "request_id": "req_ghi789rst",
    "timestamp": "2024-01-15T10:35:35Z"
  }
}
```

### Error Response Headers

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
X-Request-Id: req_ghi789rst
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1705315560
Retry-After: 25
```

---

## Troubleshooting Guide

### Authentication Issues

#### Problem: TOKEN_EXPIRED (1203)
```
Symptoms:
- API returns 401 with code 1203
- User was previously logged in

Diagnosis:
1. Check token expiration time in JWT payload
2. Verify system clock synchronization
3. Check if refresh token is available

Resolution:
1. Attempt token refresh using refresh token
2. If refresh fails, redirect to login
3. Clear stored tokens and re-authenticate

Code Example:
```typescript
async function handleTokenExpired() {
  const refreshToken = storage.getRefreshToken();
  if (refreshToken) {
    try {
      const { accessToken } = await api.refreshToken(refreshToken);
      storage.setAccessToken(accessToken);
      return true; // Retry original request
    } catch (e) {
      if (e.code === 1207) { // REFRESH_TOKEN_EXPIRED
        return redirectToLogin();
      }
    }
  }
  return redirectToLogin();
}
```

#### Problem: YAHOO_AUTH_REQUIRED (1304)
```
Symptoms:
- Yahoo API calls fail
- User hasn't linked Yahoo account

Resolution:
1. Prompt user to link Yahoo account
2. Redirect to Yahoo OAuth flow
3. Store tokens after successful auth
```

### Rate Limiting Issues

#### Problem: RATE_LIMIT_EXCEEDED (10001)
```
Symptoms:
- API returns 429
- Requests being rejected

Diagnosis:
1. Check X-RateLimit headers
2. Identify request patterns
3. Review client-side caching

Resolution:
1. Implement exponential backoff
2. Add client-side request queuing
3. Cache responses where possible

Code Example:
```typescript
async function requestWithBackoff(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (e) {
      if (e.code === 10001 && i < maxRetries - 1) {
        const delay = Math.min(1000 * Math.pow(2, i), 30000);
        await sleep(delay);
        continue;
      }
      throw e;
    }
  }
}
```

### Database Issues

#### Problem: DB_CONNECTION_TIMEOUT (6002)
```
Symptoms:
- Slow response times
- Intermittent 504 errors

Diagnosis:
1. Check database metrics
2. Review connection pool status
3. Analyze slow query logs

Resolution:
1. Scale database resources
2. Optimize slow queries
3. Increase connection pool size
```

### ML/Prediction Issues

#### Problem: INSUFFICIENT_DATA (8101)
```
Symptoms:
- Predictions unavailable for some players
- Low confidence warnings

Diagnosis:
1. Check player's game history
2. Verify feature availability
3. Review minimum data requirements

Resolution:
1. Inform user about data limitations
2. Use alternative prediction methods
3. Show historical averages instead
```

---

## Client-Side Error Handling

### React Error Boundary

```typescript
import React, { Component, ErrorInfo } from 'react';
import { ApiError } from '@/lib/api';

interface Props {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ApiErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('API Error:', error, errorInfo);

    if (error instanceof ApiError) {
      // Handle specific error codes
      switch (error.code) {
        case 1203: // TOKEN_EXPIRED
        case 1204: // TOKEN_REVOKED
          window.location.href = '/login?reason=session_expired';
          break;
        case 11003: // MAINTENANCE_MODE
          window.location.href = '/maintenance';
          break;
      }
    }
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || <ErrorFallback error={this.state.error} />;
    }
    return this.props.children;
  }
}
```

### API Client Error Interceptor

```typescript
import axios, { AxiosError } from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

api.interceptors.response.use(
  response => response,
  async (error: AxiosError<ApiErrorResponse>) => {
    const apiError = error.response?.data?.error;

    if (!apiError) {
      throw new NetworkError('Network error occurred');
    }

    // Handle authentication errors
    if (apiError.code >= 1000 && apiError.code < 2000) {
      return handleAuthError(apiError, error.config);
    }

    // Handle rate limiting
    if (apiError.code >= 10000 && apiError.code < 11000) {
      return handleRateLimitError(apiError, error.config);
    }

    // Handle validation errors
    if (apiError.code >= 3000 && apiError.code < 4000) {
      throw new ValidationError(apiError);
    }

    throw new ApiError(apiError);
  }
);

async function handleAuthError(error: ApiErrorData, config: any) {
  if (error.code === 1203) { // TOKEN_EXPIRED
    const newToken = await refreshToken();
    if (newToken) {
      config.headers.Authorization = `Bearer ${newToken}`;
      return api.request(config);
    }
  }

  // Redirect to login for other auth errors
  window.location.href = '/login';
  throw new AuthenticationError(error);
}

async function handleRateLimitError(error: ApiErrorData, config: any) {
  const retryAfter = error.details?.retry_after || 60;

  // Show rate limit notification
  showNotification({
    type: 'warning',
    message: `Rate limited. Retrying in ${retryAfter} seconds...`,
  });

  await sleep(retryAfter * 1000);
  return api.request(config);
}
```

### Error Display Component

```typescript
import { AlertCircle, RefreshCw, Home } from 'lucide-react';

interface ErrorDisplayProps {
  error: ApiError;
  onRetry?: () => void;
}

export function ErrorDisplay({ error, onRetry }: ErrorDisplayProps) {
  const getErrorMessage = () => {
    switch (error.code) {
      case 4003:
        return 'Player not found. They may have been traded or retired.';
      case 5001:
        return 'Yahoo is temporarily unavailable. Please try again later.';
      case 8101:
        return 'Not enough data to generate predictions for this player.';
      case 10001:
        return 'Too many requests. Please wait a moment before trying again.';
      case 11003:
        return 'System is under maintenance. Please check back soon.';
      default:
        return error.message || 'An unexpected error occurred.';
    }
  };

  const getErrorAction = () => {
    switch (error.code) {
      case 1203:
      case 1204:
        return { label: 'Log In', href: '/login' };
      case 1304:
        return { label: 'Connect Yahoo', href: '/settings/yahoo' };
      case 11003:
        return { label: 'Check Status', href: '/status' };
      default:
        return onRetry ? { label: 'Try Again', onClick: onRetry } : null;
    }
  };

  const action = getErrorAction();

  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4">
      <div className="flex items-start gap-3">
        <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
        <div className="flex-1">
          <h3 className="font-medium text-red-800">
            Error {error.code}: {error.name}
          </h3>
          <p className="mt-1 text-sm text-red-700">
            {getErrorMessage()}
          </p>
          {action && (
            <div className="mt-3">
              {action.href ? (
                <a
                  href={action.href}
                  className="inline-flex items-center gap-2 text-sm font-medium text-red-600 hover:text-red-800"
                >
                  {action.label}
                </a>
              ) : (
                <button
                  onClick={action.onClick}
                  className="inline-flex items-center gap-2 text-sm font-medium text-red-600 hover:text-red-800"
                >
                  <RefreshCw className="h-4 w-4" />
                  {action.label}
                </button>
              )}
            </div>
          )}
        </div>
      </div>
      {error.requestId && (
        <p className="mt-2 text-xs text-red-500">
          Request ID: {error.requestId}
        </p>
      )}
    </div>
  );
}
```

### Error Logging Service

```typescript
interface ErrorLog {
  code: number;
  name: string;
  message: string;
  requestId?: string;
  timestamp: string;
  context: Record<string, any>;
  stack?: string;
}

class ErrorLoggingService {
  private logs: ErrorLog[] = [];
  private maxLogs = 100;

  log(error: ApiError, context: Record<string, any> = {}) {
    const log: ErrorLog = {
      code: error.code,
      name: error.name,
      message: error.message,
      requestId: error.requestId,
      timestamp: new Date().toISOString(),
      context,
      stack: error.stack,
    };

    this.logs.unshift(log);
    if (this.logs.length > this.maxLogs) {
      this.logs.pop();
    }

    // Send critical errors to monitoring service
    if (this.isCritical(error.code)) {
      this.sendToMonitoring(log);
    }

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('API Error:', log);
    }
  }

  private isCritical(code: number): boolean {
    // System errors and unexpected errors are critical
    return code >= 11000 || (code >= 6000 && code < 7000);
  }

  private async sendToMonitoring(log: ErrorLog) {
    try {
      await fetch('/api/monitoring/errors', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(log),
      });
    } catch {
      // Silently fail - don't want error logging to cause more errors
    }
  }

  getRecentErrors(): ErrorLog[] {
    return [...this.logs];
  }

  clearLogs() {
    this.logs = [];
  }
}

export const errorLogger = new ErrorLoggingService();
```

---

## Appendix: Quick Reference

### Most Common Errors

| Code | Name | Quick Fix |
|------|------|-----------|
| 1203 | TOKEN_EXPIRED | Refresh token or re-login |
| 3001 | VALIDATION_ERROR | Check field requirements |
| 4001 | RESOURCE_NOT_FOUND | Verify resource ID exists |
| 5001 | YAHOO_API_ERROR | Retry later |
| 10001 | RATE_LIMIT_EXCEEDED | Wait and implement backoff |
| 11001 | INTERNAL_ERROR | Contact support with request ID |

### Error Code Ranges Summary

| Range | Category | Description |
|-------|----------|-------------|
| 1xxx | Authentication | Login, tokens, OAuth |
| 2xxx | Authorization | Permissions, access control |
| 3xxx | Validation | Input and business validation |
| 4xxx | Resources | Not found, conflicts, state |
| 5xxx | External Services | Yahoo, NBA, third-party |
| 6xxx | Database | Connections, queries, transactions |
| 7xxx | Cache | Redis, cache consistency |
| 8xxx | ML/Predictions | Models, features, inference |
| 9xxx | WebSocket | Connections, subscriptions |
| 10xxx | Rate Limiting | API and user limits |
| 11xxx | System | Server, config, processing |

---

**Document Version**: 2.0
**Maintainer**: Backend Team
**Last Review**: 2024
