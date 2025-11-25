# Lovable Frontend Integration Guide

**Version:** 2.0
**Last Updated:** 2025-01-15
**Purpose:** Complete guide for integrating Lovable-generated frontend with FastAPI backend, including WebSocket real-time updates, PWA support, and mobile-first design

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [API Authentication](#api-authentication)
3. [Token Management](#token-management)
4. [Core API Endpoints](#core-api-endpoints)
5. [Data Models (TypeScript)](#data-models-typescript)
6. [API Client Setup](#api-client-setup)
7. [WebSocket Integration](#websocket-integration)
8. [Push Notifications](#push-notifications)
9. [PWA & Offline Support](#pwa--offline-support)
10. [Mobile-First Design](#mobile-first-design)
11. [Example Implementations](#example-implementations)
12. [Error Handling](#error-handling)
13. [State Management](#state-management)
14. [Performance Optimization](#performance-optimization)
15. [Deployment & CORS](#deployment--cors)

---

## Architecture Overview

### System Components (v2.0)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Lovable Frontend (React/Next.js)                      │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   Pages     │  │ Components  │  │   Hooks     │  │    PWA      │   │
│  │  (Mobile    │  │  (Touch     │  │ (WebSocket  │  │  (Service   │   │
│  │   First)    │  │   Ready)    │  │  Enabled)   │  │   Worker)   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                     State Management Layer                        │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐                  │   │
│  │  │  Zustand   │  │   React    │  │  IndexedDB │                  │   │
│  │  │  (Client)  │  │   Query    │  │  (Offline) │                  │   │
│  │  └────────────┘  └────────────┘  └────────────┘                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      API Client Layer                             │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐                  │   │
│  │  │   Axios    │  │ WebSocket  │  │   FCM      │                  │   │
│  │  │  (REST)    │  │  Client    │  │  (Push)    │                  │   │
│  │  └────────────┘  └────────────┘  └────────────┘                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└────────────────────────┬─────────────────────┬──────────────────────────┘
                         │                     │
            HTTPS/REST   │                     │  WSS
            JWT Bearer   │                     │  WebSocket
                         │                     │
┌────────────────────────▼─────────────────────▼──────────────────────────┐
│                        Backend Services                                  │
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │   FastAPI       │  │   WebSocket     │  │   ML Service    │         │
│  │   REST API      │  │   Server        │  │                 │         │
│  │   /api/v1/      │  │   /ws/          │  │   /ml/v1/       │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
│                                                                          │
│  Base URL: https://api.fantasyhoops.com                                 │
│  WebSocket: wss://api.fantasyhoops.com/ws                               │
└─────────────────────────────────────────────────────────────────────────┘
```

### Communication Protocols

| Protocol | Purpose | Authentication |
|----------|---------|----------------|
| HTTPS REST | CRUD operations, data fetching | JWT Bearer Token |
| WebSocket (WSS) | Real-time updates, live scores | JWT in connection params |
| FCM | Push notifications | FCM Token + User ID |

### Base URLs

```typescript
// config/api.ts
export const API_CONFIG = {
  REST_BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'https://api.fantasyhoops.com/api/v1',
  WS_BASE_URL: process.env.NEXT_PUBLIC_WS_URL || 'wss://api.fantasyhoops.com/ws',
  ML_BASE_URL: process.env.NEXT_PUBLIC_ML_URL || 'https://api.fantasyhoops.com/ml/v1',
};
```

---

## API Authentication

### Authentication Flow (Enhanced)

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  User   │     │ Frontend│     │ Backend │     │  Redis  │
└────┬────┘     └────┬────┘     └────┬────┘     └────┬────┘
     │               │               │               │
     │  1. Login     │               │               │
     │──────────────>│               │               │
     │               │  2. POST /auth/login          │
     │               │──────────────>│               │
     │               │               │  3. Validate  │
     │               │               │──────────────>│
     │               │               │<──────────────│
     │               │  4. Access + Refresh Tokens   │
     │               │<──────────────│               │
     │  5. Store     │               │               │
     │<──────────────│               │               │
     │               │               │               │
     │  6. API Call  │               │               │
     │──────────────>│               │               │
     │               │  7. Request + Bearer Token    │
     │               │──────────────>│               │
     │               │  8. Response  │               │
     │               │<──────────────│               │
     │  9. Data      │               │               │
     │<──────────────│               │               │
     │               │               │               │
     │  10. Token Expired            │               │
     │               │  11. POST /auth/refresh       │
     │               │──────────────>│               │
     │               │  12. New Tokens│              │
     │               │<──────────────│               │
```

### Registration

```typescript
// POST /api/v1/auth/register
interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  accept_terms: boolean;
}

interface RegisterResponse {
  user_id: string;
  email: string;
  username: string;
  message: string;
  verification_required: boolean;
}

// Example
const register = async (data: RegisterRequest): Promise<RegisterResponse> => {
  const response = await apiClient.post('/auth/register', data);
  return response.data;
};
```

### Login

```typescript
// POST /api/v1/auth/login
interface LoginRequest {
  email: string;
  password: string;
  remember_me?: boolean;
  device_info?: {
    platform: string;
    browser: string;
    device_id: string;
  };
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: 'Bearer';
  expires_in: number;        // Access token expiry (seconds)
  refresh_expires_in: number; // Refresh token expiry (seconds)
  user: {
    id: string;
    email: string;
    username: string;
    is_premium: boolean;
  };
}

// Example
const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
  const response = await apiClient.post('/auth/login', credentials);
  return response.data;
};
```

---

## Token Management

### Secure Token Storage

```typescript
// lib/token-storage.ts

import { openDB, IDBPDatabase } from 'idb';

interface TokenData {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;
  refreshExpiresAt: number;
}

class TokenStorage {
  private dbName = 'fantasy-auth';
  private storeName = 'tokens';
  private db: IDBPDatabase | null = null;

  async init(): Promise<void> {
    this.db = await openDB(this.dbName, 1, {
      upgrade(db) {
        db.createObjectStore('tokens');
      },
    });
  }

  async setTokens(tokens: TokenData): Promise<void> {
    if (!this.db) await this.init();
    await this.db!.put(this.storeName, tokens, 'current');
  }

  async getTokens(): Promise<TokenData | null> {
    if (!this.db) await this.init();
    return await this.db!.get(this.storeName, 'current');
  }

  async clearTokens(): Promise<void> {
    if (!this.db) await this.init();
    await this.db!.delete(this.storeName, 'current');
  }

  async isAccessTokenValid(): Promise<boolean> {
    const tokens = await this.getTokens();
    if (!tokens) return false;
    return Date.now() < tokens.expiresAt - 60000; // 1 minute buffer
  }

  async isRefreshTokenValid(): Promise<boolean> {
    const tokens = await this.getTokens();
    if (!tokens) return false;
    return Date.now() < tokens.refreshExpiresAt;
  }
}

export const tokenStorage = new TokenStorage();
```

### Token Refresh Logic

```typescript
// lib/token-refresh.ts

import { apiClient } from './api-client';
import { tokenStorage } from './token-storage';

let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

const subscribeTokenRefresh = (cb: (token: string) => void) => {
  refreshSubscribers.push(cb);
};

const onRefreshed = (token: string) => {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
};

export const refreshAccessToken = async (): Promise<string | null> => {
  const tokens = await tokenStorage.getTokens();

  if (!tokens || !(await tokenStorage.isRefreshTokenValid())) {
    await tokenStorage.clearTokens();
    window.location.href = '/login?session_expired=true';
    return null;
  }

  if (isRefreshing) {
    return new Promise((resolve) => {
      subscribeTokenRefresh((token) => resolve(token));
    });
  }

  isRefreshing = true;

  try {
    const response = await apiClient.post('/auth/refresh', {
      refresh_token: tokens.refreshToken,
    });

    const { access_token, refresh_token, expires_in, refresh_expires_in } = response.data;

    await tokenStorage.setTokens({
      accessToken: access_token,
      refreshToken: refresh_token,
      expiresAt: Date.now() + expires_in * 1000,
      refreshExpiresAt: Date.now() + refresh_expires_in * 1000,
    });

    onRefreshed(access_token);
    return access_token;
  } catch (error) {
    await tokenStorage.clearTokens();
    window.location.href = '/login?session_expired=true';
    return null;
  } finally {
    isRefreshing = false;
  }
};
```

### Token Revocation

```typescript
// POST /api/v1/auth/logout
interface LogoutRequest {
  refresh_token: string;
  revoke_all_devices?: boolean;
}

// POST /api/v1/auth/revoke
interface RevokeRequest {
  token: string;
  token_type: 'access' | 'refresh';
}

// Example: Logout from current device
const logout = async (): Promise<void> => {
  const tokens = await tokenStorage.getTokens();

  if (tokens) {
    try {
      await apiClient.post('/auth/logout', {
        refresh_token: tokens.refreshToken,
      });
    } catch (error) {
      console.error('Logout API error:', error);
    }
  }

  await tokenStorage.clearTokens();
  window.location.href = '/login';
};

// Example: Logout from all devices
const logoutAllDevices = async (): Promise<void> => {
  const tokens = await tokenStorage.getTokens();

  if (tokens) {
    await apiClient.post('/auth/logout', {
      refresh_token: tokens.refreshToken,
      revoke_all_devices: true,
    });
  }

  await tokenStorage.clearTokens();
  window.location.href = '/login';
};
```

---

## Core API Endpoints

### Endpoint Categories

#### 1. Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get tokens |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Logout and revoke tokens |
| POST | `/auth/revoke` | Revoke specific token |
| GET | `/auth/me` | Get current user info |
| PUT | `/auth/me` | Update user profile |
| POST | `/auth/password/change` | Change password |
| POST | `/auth/password/reset` | Request password reset |

#### 2. Players
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/players` | Search/list players |
| GET | `/players/{id}` | Get player details |
| GET | `/players/{id}/stats` | Get player statistics |
| GET | `/players/{id}/game-log` | Get recent game log |
| GET | `/players/{id}/injuries` | Get injury history |
| GET | `/players/trending` | Get trending players |
| GET | `/players/compare` | Compare multiple players |

#### 3. Predictions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/predictions/player/{id}` | Get player prediction |
| GET | `/predictions/daily` | Get all daily predictions |
| GET | `/predictions/accuracy` | Get model accuracy stats |
| POST | `/predictions/custom` | Custom prediction request |

#### 4. Teams & Rosters
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/teams` | Get user's teams |
| GET | `/teams/{id}` | Get team details |
| GET | `/teams/{id}/roster` | Get team roster |
| PUT | `/teams/{id}/roster` | Update roster |
| GET | `/teams/{id}/schedule` | Get team schedule |

#### 5. Recommendations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/recommendations/{team_id}` | Get recommendations |
| POST | `/recommendations/{team_id}/feedback` | Submit feedback |

#### 6. Matchups
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/matchups/weekly/{team_id}` | Get weekly matchup |
| GET | `/matchups/history/{team_id}` | Get matchup history |

#### 7. Yahoo Integration
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/yahoo/auth/init` | Start OAuth flow |
| GET | `/yahoo/auth/callback` | OAuth callback |
| POST | `/yahoo/sync/leagues` | Sync all leagues |
| POST | `/yahoo/sync/team/{league_id}` | Sync specific team |
| GET | `/yahoo/leagues` | Get synced leagues |

#### 8. Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/notifications/register` | Register FCM token |
| DELETE | `/notifications/unregister` | Unregister FCM token |
| GET | `/notifications/preferences` | Get notification prefs |
| PUT | `/notifications/preferences` | Update notification prefs |

---

## Data Models (TypeScript)

### Core Types

```typescript
// types/api.ts

// ============ User & Auth ============
export interface User {
  id: string;
  email: string;
  username: string;
  avatar_url?: string;
  is_active: boolean;
  is_premium: boolean;
  premium_expires_at?: string;
  created_at: string;
  last_login_at: string;
  notification_preferences: NotificationPreferences;
}

export interface NotificationPreferences {
  push_enabled: boolean;
  email_enabled: boolean;
  game_start_alerts: boolean;
  injury_alerts: boolean;
  trade_alerts: boolean;
  waiver_alerts: boolean;
  prediction_alerts: boolean;
  quiet_hours_start?: string; // "22:00"
  quiet_hours_end?: string;   // "08:00"
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: 'Bearer';
  expires_in: number;
  refresh_expires_in: number;
}

// ============ Players ============
export interface Player {
  id: number;
  full_name: string;
  first_name: string;
  last_name: string;
  position: PlayerPosition;
  positions: PlayerPosition[]; // Multi-position eligibility
  team_id: number;
  team_abbreviation: string;
  team_name: string;
  jersey_number: string;
  height: string;
  weight: string;
  birth_date: string;
  is_active: boolean;
  headshot_url?: string;
  injury_status?: InjuryStatus;
}

export type PlayerPosition = 'PG' | 'SG' | 'SF' | 'PF' | 'C' | 'G' | 'F' | 'UTIL';

export interface InjuryStatus {
  status: 'HEALTHY' | 'QUESTIONABLE' | 'DOUBTFUL' | 'OUT' | 'GTD';
  description?: string;
  return_date?: string;
  last_updated: string;
}

export interface PlayerStats {
  player_id: number;
  season: string;
  games_played: number;
  games_started: number;

  // Per-game averages
  minutes_pg: number;
  points_pg: number;
  rebounds_pg: number;
  offensive_rebounds_pg: number;
  defensive_rebounds_pg: number;
  assists_pg: number;
  steals_pg: number;
  blocks_pg: number;
  turnovers_pg: number;
  personal_fouls_pg: number;
  fg3m_pg: number;

  // Shooting
  fgm_pg: number;
  fga_pg: number;
  fg_pct: number;
  fg3a_pg: number;
  fg3_pct: number;
  ftm_pg: number;
  fta_pg: number;
  ft_pct: number;

  // Advanced
  plus_minus: number;
  usage_rate: number;
  true_shooting_pct: number;
  effective_fg_pct: number;
}

export interface GameLog {
  game_id: string;
  game_date: string;
  opponent_team_id: number;
  opponent_abbreviation: string;
  is_home: boolean;
  result: 'W' | 'L';
  score: string;

  minutes_played: number;
  points: number;
  rebounds: number;
  assists: number;
  steals: number;
  blocks: number;
  turnovers: number;

  fgm: number;
  fga: number;
  fg_pct: number;
  fg3m: number;
  fg3a: number;
  fg3_pct: number;
  ftm: number;
  fta: number;
  ft_pct: number;

  plus_minus: number;
  fantasy_points?: number;
}

// ============ Predictions ============
export interface PredictionValue {
  value: number;
  low: number;
  high: number;
  confidence: number;
  z_score?: number;
}

export interface PlayerPrediction {
  player_id: number;
  player_name: string;
  game_date: string;
  opponent: {
    team_id: number;
    team_name: string;
    abbreviation: string;
    defensive_rating: number;
  };
  is_home: boolean;

  predictions: {
    minutes: PredictionValue;
    points: PredictionValue;
    rebounds: PredictionValue;
    assists: PredictionValue;
    steals: PredictionValue;
    blocks: PredictionValue;
    turnovers: PredictionValue;
    fg3m: PredictionValue;
    fg_pct: PredictionValue;
    ft_pct: PredictionValue;
    fantasy_points: PredictionValue;
  };

  total_z_score: number;
  confidence: number;
  model_version: string;
  factors: PredictionFactor[];
  injury_risk: number;
  prediction_date: string;
}

export interface PredictionFactor {
  name: string;
  impact: 'positive' | 'negative' | 'neutral';
  description: string;
  weight: number;
}

// ============ Teams & Rosters ============
export interface Team {
  id: string;
  user_id: string;
  league_id: string;
  league_name: string;
  team_name: string;
  team_logo_url?: string;
  wins: number;
  losses: number;
  ties: number;
  rank: number;
  points_for: number;
  points_against: number;
  streak: string;
  last_synced_at: string;
}

export interface RosterPlayer {
  player_id: number;
  player: Player;
  roster_position: RosterPosition;
  acquisition_type: 'draft' | 'trade' | 'waiver' | 'free_agent';
  acquisition_date: string;
}

export type RosterPosition = 'PG' | 'SG' | 'SF' | 'PF' | 'C' | 'G' | 'F' | 'UTIL' | 'BN' | 'IL' | 'IL+';

// ============ Recommendations ============
export interface Recommendation {
  id: string;
  type: RecommendationType;
  priority: 'critical' | 'high' | 'medium' | 'low';

  // Start/Sit specific
  action?: 'start' | 'sit';
  player?: Player;
  over_player?: Player;

  // Waiver specific
  add_player?: Player;
  drop_player?: Player;

  reasoning: string;
  detailed_analysis?: string;
  confidence: number;
  expected_value?: number;
  expires_at: string;

  // Waiver specific
  projected_ros_z_score?: number;
  ownership_pct?: number;
  trending?: 'up' | 'down' | 'stable';
}

export type RecommendationType = 'start_sit' | 'waiver_add' | 'waiver_drop' | 'trade' | 'matchup_strategy';

// ============ Matchups ============
export interface Matchup {
  team_id: string;
  opponent_team_id: string;
  opponent_team_name: string;
  week_number: number;

  win_probability: number;
  projected_score: number;
  opponent_projected_score: number;

  category_breakdown: {
    [category: string]: CategoryProjection;
  };

  key_matchups: KeyMatchup[];
  week_start_date: string;
  week_end_date: string;
}

export interface CategoryProjection {
  my_team: number;
  opponent: number;
  projected_winner: 'me' | 'opponent' | 'tie';
  confidence: number;
  margin: number;
}

export interface KeyMatchup {
  category: string;
  importance: 'critical' | 'important' | 'normal';
  suggestion: string;
}

// ============ API Response Wrappers ============
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
    timestamp: string;
    request_id: string;
  };
}
```

---

## API Client Setup

### Enhanced Axios Configuration

```typescript
// lib/api-client.ts

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { tokenStorage } from './token-storage';
import { refreshAccessToken } from './token-refresh';
import { API_CONFIG } from '@/config/api';
import { ApiError } from '@/types/api';

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.REST_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Skip auth for public endpoints
    const publicEndpoints = ['/auth/login', '/auth/register', '/auth/password/reset'];
    if (publicEndpoints.some(endpoint => config.url?.includes(endpoint))) {
      return config;
    }

    const tokens = await tokenStorage.getTokens();

    if (tokens) {
      // Check if token needs refresh
      if (!(await tokenStorage.isAccessTokenValid())) {
        const newToken = await refreshAccessToken();
        if (newToken) {
          config.headers.Authorization = `Bearer ${newToken}`;
        }
      } else {
        config.headers.Authorization = `Bearer ${tokens.accessToken}`;
      }
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Handle 401 - try refresh once
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const newToken = await refreshAccessToken();
      if (newToken) {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(originalRequest);
      }
    }

    // Handle other errors
    if (error.response) {
      const { status, data } = error.response;

      switch (status) {
        case 403:
          console.error('Access forbidden:', data.error?.message);
          break;
        case 404:
          console.error('Resource not found:', data.error?.message);
          break;
        case 422:
          console.error('Validation error:', data.error?.details);
          break;
        case 429:
          console.error('Rate limit exceeded');
          break;
        case 500:
        case 502:
        case 503:
          console.error('Server error:', data.error?.message);
          break;
      }
    } else if (error.request) {
      console.error('Network error - no response received');
    }

    return Promise.reject(error);
  }
);

export default apiClient;
```

### React Query Configuration

```typescript
// lib/react-query-client.ts

import { QueryClient, QueryCache, MutationCache } from '@tanstack/react-query';
import toast from 'react-hot-toast';

export const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: (error, query) => {
      // Only show toast for errors that aren't handled by component
      if (query.meta?.showErrorToast !== false) {
        toast.error(`Error: ${(error as Error).message}`);
      }
    },
  }),
  mutationCache: new MutationCache({
    onError: (error) => {
      toast.error(`Error: ${(error as Error).message}`);
    },
  }),
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => {
        // Don't retry on 4xx errors
        if ((error as any)?.response?.status >= 400 && (error as any)?.response?.status < 500) {
          return false;
        }
        return failureCount < 2;
      },
      staleTime: 5 * 60 * 1000,      // 5 minutes
      gcTime: 30 * 60 * 1000,        // 30 minutes (formerly cacheTime)
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 1,
    },
  },
});
```

---

## WebSocket Integration

### WebSocket Client

```typescript
// lib/websocket-client.ts

import { tokenStorage } from './token-storage';
import { API_CONFIG } from '@/config/api';

type MessageHandler = (data: any) => void;
type ConnectionHandler = () => void;

interface SubscriptionConfig {
  channel: string;
  params?: Record<string, any>;
}

class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private messageHandlers: Map<string, Set<MessageHandler>> = new Map();
  private connectionHandlers: Set<ConnectionHandler> = new Set();
  private disconnectionHandlers: Set<ConnectionHandler> = new Set();
  private subscriptions: Set<string> = new Set();
  private pingInterval: NodeJS.Timeout | null = null;

  async connect(): Promise<void> {
    const tokens = await tokenStorage.getTokens();
    if (!tokens) {
      console.error('No auth tokens available for WebSocket connection');
      return;
    }

    const wsUrl = `${API_CONFIG.WS_BASE_URL}?token=${tokens.accessToken}`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.startPing();
      this.resubscribe();
      this.connectionHandlers.forEach(handler => handler());
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket disconnected:', event.code, event.reason);
      this.stopPing();
      this.disconnectionHandlers.forEach(handler => handler());

      if (event.code !== 1000) {
        this.attemptReconnect();
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  private handleMessage(message: { type: string; channel?: string; data: any }) {
    const { type, channel, data } = message;

    // Handle system messages
    if (type === 'pong') return;
    if (type === 'subscribed') {
      console.log(`Subscribed to ${channel}`);
      return;
    }
    if (type === 'unsubscribed') {
      console.log(`Unsubscribed from ${channel}`);
      return;
    }
    if (type === 'error') {
      console.error('WebSocket error:', data);
      return;
    }

    // Route to channel handlers
    if (channel) {
      const handlers = this.messageHandlers.get(channel);
      handlers?.forEach(handler => handler(data));
    }

    // Route to type handlers
    const typeHandlers = this.messageHandlers.get(type);
    typeHandlers?.forEach(handler => handler(data));
  }

  subscribe(config: SubscriptionConfig): void {
    const { channel, params } = config;

    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        action: 'subscribe',
        channel,
        params,
      }));
    }

    this.subscriptions.add(JSON.stringify(config));
  }

  unsubscribe(channel: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        action: 'unsubscribe',
        channel,
      }));
    }

    // Remove from subscriptions
    this.subscriptions.forEach(sub => {
      const config = JSON.parse(sub);
      if (config.channel === channel) {
        this.subscriptions.delete(sub);
      }
    });
  }

  on(event: string, handler: MessageHandler): () => void {
    if (!this.messageHandlers.has(event)) {
      this.messageHandlers.set(event, new Set());
    }
    this.messageHandlers.get(event)!.add(handler);

    // Return unsubscribe function
    return () => {
      this.messageHandlers.get(event)?.delete(handler);
    };
  }

  onConnect(handler: ConnectionHandler): () => void {
    this.connectionHandlers.add(handler);
    return () => this.connectionHandlers.delete(handler);
  }

  onDisconnect(handler: ConnectionHandler): () => void {
    this.disconnectionHandlers.add(handler);
    return () => this.disconnectionHandlers.delete(handler);
  }

  private resubscribe(): void {
    this.subscriptions.forEach(sub => {
      const config = JSON.parse(sub);
      this.subscribe(config);
    });
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

    setTimeout(() => this.connect(), delay);
  }

  private startPing(): void {
    this.pingInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ action: 'ping' }));
      }
    }, 30000);
  }

  private stopPing(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  disconnect(): void {
    this.stopPing();
    this.ws?.close(1000, 'Client disconnect');
    this.ws = null;
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

export const wsClient = new WebSocketClient();
```

### WebSocket React Hook

```typescript
// hooks/useWebSocket.ts

import { useEffect, useState, useCallback, useRef } from 'react';
import { wsClient } from '@/lib/websocket-client';

interface UseWebSocketOptions {
  channel?: string;
  params?: Record<string, any>;
  onMessage?: (data: any) => void;
  autoConnect?: boolean;
}

interface UseWebSocketReturn<T> {
  isConnected: boolean;
  lastMessage: T | null;
  messages: T[];
  subscribe: (channel: string, params?: Record<string, any>) => void;
  unsubscribe: (channel: string) => void;
}

export function useWebSocket<T = any>(options: UseWebSocketOptions = {}): UseWebSocketReturn<T> {
  const { channel, params, onMessage, autoConnect = true } = options;

  const [isConnected, setIsConnected] = useState(wsClient.isConnected);
  const [lastMessage, setLastMessage] = useState<T | null>(null);
  const [messages, setMessages] = useState<T[]>([]);
  const onMessageRef = useRef(onMessage);

  // Keep onMessage ref updated
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  // Handle connection
  useEffect(() => {
    if (autoConnect && !wsClient.isConnected) {
      wsClient.connect();
    }

    const unsubConnect = wsClient.onConnect(() => setIsConnected(true));
    const unsubDisconnect = wsClient.onDisconnect(() => setIsConnected(false));

    return () => {
      unsubConnect();
      unsubDisconnect();
    };
  }, [autoConnect]);

  // Handle channel subscription
  useEffect(() => {
    if (!channel || !isConnected) return;

    wsClient.subscribe({ channel, params });

    const unsubscribe = wsClient.on(channel, (data: T) => {
      setLastMessage(data);
      setMessages(prev => [...prev.slice(-99), data]); // Keep last 100 messages
      onMessageRef.current?.(data);
    });

    return () => {
      unsubscribe();
      wsClient.unsubscribe(channel);
    };
  }, [channel, params, isConnected]);

  const subscribe = useCallback((ch: string, p?: Record<string, any>) => {
    wsClient.subscribe({ channel: ch, params: p });
  }, []);

  const unsubscribe = useCallback((ch: string) => {
    wsClient.unsubscribe(ch);
  }, []);

  return {
    isConnected,
    lastMessage,
    messages,
    subscribe,
    unsubscribe,
  };
}
```

### Real-Time Updates Hook

```typescript
// hooks/useRealTimeUpdates.ts

import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useWebSocket } from './useWebSocket';

interface LiveScoreUpdate {
  game_id: string;
  player_id: number;
  stats: {
    points: number;
    rebounds: number;
    assists: number;
    steals: number;
    blocks: number;
    turnovers: number;
    fg3m: number;
    minutes: number;
  };
  timestamp: string;
}

interface InjuryUpdate {
  player_id: number;
  status: string;
  description: string;
  return_date?: string;
}

export function useRealTimeUpdates(teamId?: string) {
  const queryClient = useQueryClient();

  // Live scores subscription
  const { lastMessage: liveScore } = useWebSocket<LiveScoreUpdate>({
    channel: 'live_scores',
    onMessage: (data) => {
      // Update player stats in cache
      queryClient.setQueryData(
        ['player', data.player_id, 'live'],
        (old: any) => ({ ...old, ...data.stats })
      );

      // Invalidate related queries
      queryClient.invalidateQueries({
        queryKey: ['predictions', 'player', data.player_id],
      });
    },
  });

  // Injury updates subscription
  const { lastMessage: injuryUpdate } = useWebSocket<InjuryUpdate>({
    channel: 'injuries',
    onMessage: (data) => {
      // Update player injury status
      queryClient.setQueryData(
        ['player', data.player_id],
        (old: any) => ({
          ...old,
          injury_status: {
            status: data.status,
            description: data.description,
            return_date: data.return_date,
            last_updated: new Date().toISOString(),
          },
        })
      );
    },
  });

  // Team-specific updates
  useWebSocket({
    channel: teamId ? `team:${teamId}` : undefined,
    onMessage: (data) => {
      if (data.type === 'roster_update') {
        queryClient.invalidateQueries({
          queryKey: ['teams', teamId, 'roster'],
        });
      }
      if (data.type === 'recommendation') {
        queryClient.invalidateQueries({
          queryKey: ['recommendations', teamId],
        });
      }
    },
  });

  return { liveScore, injuryUpdate };
}
```

---

## Push Notifications

### FCM Setup

```typescript
// lib/firebase.ts

import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, onMessage, Messaging } from 'firebase/messaging';

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

const app = initializeApp(firebaseConfig);

let messaging: Messaging | null = null;

export const getFirebaseMessaging = (): Messaging | null => {
  if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
    if (!messaging) {
      messaging = getMessaging(app);
    }
    return messaging;
  }
  return null;
};

export const requestNotificationPermission = async (): Promise<string | null> => {
  try {
    const permission = await Notification.requestPermission();

    if (permission !== 'granted') {
      console.log('Notification permission denied');
      return null;
    }

    const messaging = getFirebaseMessaging();
    if (!messaging) return null;

    const token = await getToken(messaging, {
      vapidKey: process.env.NEXT_PUBLIC_FIREBASE_VAPID_KEY,
    });

    return token;
  } catch (error) {
    console.error('Error getting FCM token:', error);
    return null;
  }
};

export const onForegroundMessage = (callback: (payload: any) => void) => {
  const messaging = getFirebaseMessaging();
  if (!messaging) return () => {};

  return onMessage(messaging, callback);
};
```

### Notifications Hook

```typescript
// hooks/useNotifications.ts

import { useState, useEffect, useCallback } from 'react';
import { requestNotificationPermission, onForegroundMessage } from '@/lib/firebase';
import { apiClient } from '@/lib/api-client';
import toast from 'react-hot-toast';

interface Notification {
  id: string;
  title: string;
  body: string;
  type: 'injury' | 'game_start' | 'trade' | 'waiver' | 'prediction';
  data?: Record<string, any>;
  timestamp: string;
  read: boolean;
}

export function useNotifications() {
  const [isEnabled, setIsEnabled] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [notifications, setNotifications] = useState<Notification[]>([]);

  // Check current permission status
  useEffect(() => {
    if (typeof window !== 'undefined' && 'Notification' in window) {
      setIsEnabled(Notification.permission === 'granted');
    }
    setIsLoading(false);
  }, []);

  // Listen for foreground messages
  useEffect(() => {
    const unsubscribe = onForegroundMessage((payload) => {
      const { title, body } = payload.notification || {};

      // Show toast for foreground notifications
      toast(body || 'New notification', {
        icon: getNotificationIcon(payload.data?.type),
      });

      // Add to notifications list
      setNotifications(prev => [{
        id: payload.messageId || Date.now().toString(),
        title: title || 'Notification',
        body: body || '',
        type: payload.data?.type || 'prediction',
        data: payload.data,
        timestamp: new Date().toISOString(),
        read: false,
      }, ...prev]);
    });

    return unsubscribe;
  }, []);

  const enableNotifications = useCallback(async () => {
    setIsLoading(true);

    try {
      const fcmToken = await requestNotificationPermission();

      if (fcmToken) {
        // Register token with backend
        await apiClient.post('/notifications/register', {
          fcm_token: fcmToken,
          platform: 'web',
        });

        setIsEnabled(true);
        toast.success('Notifications enabled!');
      }
    } catch (error) {
      console.error('Failed to enable notifications:', error);
      toast.error('Failed to enable notifications');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const disableNotifications = useCallback(async () => {
    try {
      await apiClient.delete('/notifications/unregister');
      setIsEnabled(false);
      toast.success('Notifications disabled');
    } catch (error) {
      console.error('Failed to disable notifications:', error);
    }
  }, []);

  const markAsRead = useCallback((id: string) => {
    setNotifications(prev =>
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  }, []);

  return {
    isEnabled,
    isLoading,
    notifications,
    unreadCount: notifications.filter(n => !n.read).length,
    enableNotifications,
    disableNotifications,
    markAsRead,
    markAllAsRead,
  };
}

function getNotificationIcon(type?: string): string {
  switch (type) {
    case 'injury': return '🏥';
    case 'game_start': return '🏀';
    case 'trade': return '🔄';
    case 'waiver': return '📋';
    case 'prediction': return '📊';
    default: return '🔔';
  }
}
```

### Service Worker for Background Notifications

```javascript
// public/firebase-messaging-sw.js

importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.0.0/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: 'YOUR_API_KEY',
  authDomain: 'YOUR_AUTH_DOMAIN',
  projectId: 'YOUR_PROJECT_ID',
  storageBucket: 'YOUR_STORAGE_BUCKET',
  messagingSenderId: 'YOUR_MESSAGING_SENDER_ID',
  appId: 'YOUR_APP_ID',
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  const { title, body, icon } = payload.notification;

  const notificationOptions = {
    body,
    icon: icon || '/icons/notification-icon.png',
    badge: '/icons/badge-icon.png',
    tag: payload.data?.type || 'default',
    data: payload.data,
    actions: getNotificationActions(payload.data?.type),
  };

  self.registration.showNotification(title, notificationOptions);
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  const { type, player_id, team_id } = event.notification.data || {};
  let url = '/';

  switch (type) {
    case 'injury':
      url = player_id ? `/players/${player_id}` : '/players';
      break;
    case 'game_start':
      url = '/live';
      break;
    case 'recommendation':
      url = team_id ? `/teams/${team_id}/recommendations` : '/recommendations';
      break;
    default:
      url = '/dashboard';
  }

  event.waitUntil(
    clients.matchAll({ type: 'window' }).then((clientList) => {
      for (const client of clientList) {
        if (client.url === url && 'focus' in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(url);
      }
    })
  );
});

function getNotificationActions(type) {
  switch (type) {
    case 'injury':
      return [
        { action: 'view', title: 'View Player' },
        { action: 'dismiss', title: 'Dismiss' },
      ];
    case 'recommendation':
      return [
        { action: 'view', title: 'View Recommendation' },
        { action: 'dismiss', title: 'Later' },
      ];
    default:
      return [];
  }
}
```

---

## PWA & Offline Support

### Service Worker Registration

```typescript
// lib/service-worker.ts

export async function registerServiceWorker(): Promise<ServiceWorkerRegistration | null> {
  if (typeof window === 'undefined' || !('serviceWorker' in navigator)) {
    return null;
  }

  try {
    const registration = await navigator.serviceWorker.register('/sw.js', {
      scope: '/',
    });

    console.log('Service Worker registered:', registration.scope);

    // Check for updates
    registration.addEventListener('updatefound', () => {
      const newWorker = registration.installing;

      newWorker?.addEventListener('statechange', () => {
        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
          // New version available
          if (confirm('New version available! Reload to update?')) {
            window.location.reload();
          }
        }
      });
    });

    return registration;
  } catch (error) {
    console.error('Service Worker registration failed:', error);
    return null;
  }
}
```

### Offline Storage

```typescript
// lib/offline-storage.ts

import { openDB, DBSchema, IDBPDatabase } from 'idb';

interface FantasyDB extends DBSchema {
  players: {
    key: number;
    value: {
      id: number;
      data: any;
      updated_at: number;
    };
    indexes: { 'by-updated': number };
  };
  predictions: {
    key: string;
    value: {
      id: string;
      player_id: number;
      game_date: string;
      data: any;
      updated_at: number;
    };
    indexes: { 'by-player': number; 'by-date': string };
  };
  teams: {
    key: string;
    value: {
      id: string;
      data: any;
      updated_at: number;
    };
  };
  recommendations: {
    key: string;
    value: {
      id: string;
      team_id: string;
      data: any;
      updated_at: number;
    };
    indexes: { 'by-team': string };
  };
  syncQueue: {
    key: number;
    value: {
      id: number;
      action: string;
      endpoint: string;
      method: string;
      body?: any;
      created_at: number;
    };
  };
}

class OfflineStorage {
  private db: IDBPDatabase<FantasyDB> | null = null;
  private dbName = 'fantasy-hoops-offline';
  private dbVersion = 1;

  async init(): Promise<void> {
    if (this.db) return;

    this.db = await openDB<FantasyDB>(this.dbName, this.dbVersion, {
      upgrade(db) {
        // Players store
        const playersStore = db.createObjectStore('players', { keyPath: 'id' });
        playersStore.createIndex('by-updated', 'updated_at');

        // Predictions store
        const predictionsStore = db.createObjectStore('predictions', { keyPath: 'id' });
        predictionsStore.createIndex('by-player', 'player_id');
        predictionsStore.createIndex('by-date', 'game_date');

        // Teams store
        db.createObjectStore('teams', { keyPath: 'id' });

        // Recommendations store
        const recsStore = db.createObjectStore('recommendations', { keyPath: 'id' });
        recsStore.createIndex('by-team', 'team_id');

        // Sync queue
        db.createObjectStore('syncQueue', { keyPath: 'id', autoIncrement: true });
      },
    });
  }

  // Players
  async savePlayer(player: any): Promise<void> {
    await this.init();
    await this.db!.put('players', {
      id: player.id,
      data: player,
      updated_at: Date.now(),
    });
  }

  async getPlayer(id: number): Promise<any | null> {
    await this.init();
    const record = await this.db!.get('players', id);
    return record?.data || null;
  }

  async getAllPlayers(): Promise<any[]> {
    await this.init();
    const records = await this.db!.getAll('players');
    return records.map(r => r.data);
  }

  // Predictions
  async savePrediction(prediction: any): Promise<void> {
    await this.init();
    const id = `${prediction.player_id}_${prediction.game_date}`;
    await this.db!.put('predictions', {
      id,
      player_id: prediction.player_id,
      game_date: prediction.game_date,
      data: prediction,
      updated_at: Date.now(),
    });
  }

  async getPrediction(playerId: number, gameDate: string): Promise<any | null> {
    await this.init();
    const id = `${playerId}_${gameDate}`;
    const record = await this.db!.get('predictions', id);
    return record?.data || null;
  }

  async getPredictionsByDate(gameDate: string): Promise<any[]> {
    await this.init();
    const records = await this.db!.getAllFromIndex('predictions', 'by-date', gameDate);
    return records.map(r => r.data);
  }

  // Teams
  async saveTeam(team: any): Promise<void> {
    await this.init();
    await this.db!.put('teams', {
      id: team.id,
      data: team,
      updated_at: Date.now(),
    });
  }

  async getTeam(id: string): Promise<any | null> {
    await this.init();
    const record = await this.db!.get('teams', id);
    return record?.data || null;
  }

  // Recommendations
  async saveRecommendation(rec: any): Promise<void> {
    await this.init();
    await this.db!.put('recommendations', {
      id: rec.id,
      team_id: rec.team_id,
      data: rec,
      updated_at: Date.now(),
    });
  }

  async getRecommendationsByTeam(teamId: string): Promise<any[]> {
    await this.init();
    const records = await this.db!.getAllFromIndex('recommendations', 'by-team', teamId);
    return records.map(r => r.data);
  }

  // Sync Queue (for offline mutations)
  async queueAction(action: Omit<FantasyDB['syncQueue']['value'], 'id' | 'created_at'>): Promise<void> {
    await this.init();
    await this.db!.add('syncQueue', {
      ...action,
      id: Date.now(),
      created_at: Date.now(),
    });
  }

  async getQueuedActions(): Promise<FantasyDB['syncQueue']['value'][]> {
    await this.init();
    return await this.db!.getAll('syncQueue');
  }

  async clearQueuedAction(id: number): Promise<void> {
    await this.init();
    await this.db!.delete('syncQueue', id);
  }

  // Cleanup old data
  async cleanup(maxAge: number = 7 * 24 * 60 * 60 * 1000): Promise<void> {
    await this.init();
    const cutoff = Date.now() - maxAge;

    // Clean old players
    const players = await this.db!.getAllFromIndex('players', 'by-updated');
    for (const player of players) {
      if (player.updated_at < cutoff) {
        await this.db!.delete('players', player.id);
      }
    }

    // Clean old predictions
    const predictions = await this.db!.getAll('predictions');
    for (const prediction of predictions) {
      if (prediction.updated_at < cutoff) {
        await this.db!.delete('predictions', prediction.id);
      }
    }
  }
}

export const offlineStorage = new OfflineStorage();
```

### Offline-First Hook

```typescript
// hooks/useOfflineFirst.ts

import { useEffect, useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { offlineStorage } from '@/lib/offline-storage';
import { apiClient } from '@/lib/api-client';

interface UseOfflineFirstOptions<T> {
  queryKey: string[];
  fetchFn: () => Promise<T>;
  storageKey: string;
  storeData: (data: T) => Promise<void>;
  loadData: () => Promise<T | null>;
}

export function useOfflineFirst<T>({
  queryKey,
  fetchFn,
  storageKey,
  storeData,
  loadData,
}: UseOfflineFirstOptions<T>) {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const queryClient = useQueryClient();

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const query = useQuery({
    queryKey,
    queryFn: async () => {
      if (!isOnline) {
        // Load from offline storage
        const offlineData = await loadData();
        if (offlineData) {
          return offlineData;
        }
        throw new Error('No offline data available');
      }

      // Fetch from API
      const data = await fetchFn();

      // Store for offline use
      await storeData(data);

      return data;
    },
    // Load offline data immediately as placeholder
    placeholderData: () => {
      loadData().then(data => {
        if (data) {
          queryClient.setQueryData(queryKey, data);
        }
      });
      return undefined;
    },
    staleTime: isOnline ? 5 * 60 * 1000 : Infinity,
    gcTime: 24 * 60 * 60 * 1000, // Keep cache for 24 hours
  });

  return {
    ...query,
    isOnline,
    isOfflineData: !isOnline && query.data !== undefined,
  };
}

// Example usage
export function usePlayerOffline(playerId: number) {
  return useOfflineFirst({
    queryKey: ['player', playerId],
    fetchFn: async () => {
      const response = await apiClient.get(`/players/${playerId}`);
      return response.data;
    },
    storageKey: `player_${playerId}`,
    storeData: async (data) => {
      await offlineStorage.savePlayer(data);
    },
    loadData: async () => {
      return await offlineStorage.getPlayer(playerId);
    },
  });
}
```

---

## Mobile-First Design

### Responsive Breakpoints

```typescript
// config/breakpoints.ts

export const breakpoints = {
  xs: 0,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
} as const;

export const mediaQueries = {
  sm: `@media (min-width: ${breakpoints.sm}px)`,
  md: `@media (min-width: ${breakpoints.md}px)`,
  lg: `@media (min-width: ${breakpoints.lg}px)`,
  xl: `@media (min-width: ${breakpoints.xl}px)`,
  '2xl': `@media (min-width: ${breakpoints['2xl']}px)`,
  touch: '@media (hover: none) and (pointer: coarse)',
  mouse: '@media (hover: hover) and (pointer: fine)',
};
```

### Touch-Friendly Components

```typescript
// components/ui/TouchButton.tsx

import { forwardRef, ButtonHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

interface TouchButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

export const TouchButton = forwardRef<HTMLButtonElement, TouchButtonProps>(
  ({ className, variant = 'primary', size = 'md', children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          // Base styles
          'inline-flex items-center justify-center font-medium transition-colors',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
          'disabled:pointer-events-none disabled:opacity-50',
          // Touch-friendly: minimum 44x44px tap target
          'min-h-[44px] min-w-[44px]',
          // Active state for touch feedback
          'active:scale-95 active:opacity-90',
          // Variants
          {
            'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800': variant === 'primary',
            'bg-gray-200 text-gray-900 hover:bg-gray-300 active:bg-gray-400': variant === 'secondary',
            'hover:bg-gray-100 active:bg-gray-200': variant === 'ghost',
          },
          // Sizes
          {
            'h-9 px-3 text-sm rounded-md': size === 'sm',
            'h-11 px-4 text-base rounded-lg': size === 'md',
            'h-14 px-6 text-lg rounded-xl': size === 'lg',
          },
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);

TouchButton.displayName = 'TouchButton';
```

### Pull-to-Refresh

```typescript
// hooks/usePullToRefresh.ts

import { useEffect, useRef, useState } from 'react';

interface UsePullToRefreshOptions {
  onRefresh: () => Promise<void>;
  threshold?: number;
  resistance?: number;
}

export function usePullToRefresh({
  onRefresh,
  threshold = 80,
  resistance = 2.5,
}: UsePullToRefreshOptions) {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);
  const startY = useRef(0);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    let isPulling = false;

    const handleTouchStart = (e: TouchEvent) => {
      if (container.scrollTop === 0) {
        startY.current = e.touches[0].clientY;
        isPulling = true;
      }
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (!isPulling || isRefreshing) return;

      const currentY = e.touches[0].clientY;
      const diff = (currentY - startY.current) / resistance;

      if (diff > 0) {
        e.preventDefault();
        setPullDistance(Math.min(diff, threshold * 1.5));
      }
    };

    const handleTouchEnd = async () => {
      if (!isPulling) return;
      isPulling = false;

      if (pullDistance >= threshold && !isRefreshing) {
        setIsRefreshing(true);
        await onRefresh();
        setIsRefreshing(false);
      }

      setPullDistance(0);
    };

    container.addEventListener('touchstart', handleTouchStart, { passive: true });
    container.addEventListener('touchmove', handleTouchMove, { passive: false });
    container.addEventListener('touchend', handleTouchEnd, { passive: true });

    return () => {
      container.removeEventListener('touchstart', handleTouchStart);
      container.removeEventListener('touchmove', handleTouchMove);
      container.removeEventListener('touchend', handleTouchEnd);
    };
  }, [onRefresh, threshold, resistance, isRefreshing, pullDistance]);

  return {
    containerRef,
    isRefreshing,
    pullDistance,
    pullProgress: Math.min(pullDistance / threshold, 1),
  };
}
```

### Swipe Actions

```typescript
// components/SwipeableCard.tsx

import { useRef, useState, ReactNode } from 'react';
import { motion, useMotionValue, useTransform, PanInfo } from 'framer-motion';

interface SwipeableCardProps {
  children: ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  leftAction?: ReactNode;
  rightAction?: ReactNode;
  threshold?: number;
}

export function SwipeableCard({
  children,
  onSwipeLeft,
  onSwipeRight,
  leftAction,
  rightAction,
  threshold = 100,
}: SwipeableCardProps) {
  const x = useMotionValue(0);
  const [isDragging, setIsDragging] = useState(false);

  const leftOpacity = useTransform(x, [-threshold, 0], [1, 0]);
  const rightOpacity = useTransform(x, [0, threshold], [0, 1]);

  const handleDragEnd = (_: any, info: PanInfo) => {
    setIsDragging(false);

    if (info.offset.x < -threshold && onSwipeLeft) {
      onSwipeLeft();
    } else if (info.offset.x > threshold && onSwipeRight) {
      onSwipeRight();
    }
  };

  return (
    <div className="relative overflow-hidden">
      {/* Left action background */}
      {leftAction && (
        <motion.div
          className="absolute inset-y-0 left-0 flex items-center px-4 bg-red-500"
          style={{ opacity: leftOpacity }}
        >
          {leftAction}
        </motion.div>
      )}

      {/* Right action background */}
      {rightAction && (
        <motion.div
          className="absolute inset-y-0 right-0 flex items-center px-4 bg-green-500"
          style={{ opacity: rightOpacity }}
        >
          {rightAction}
        </motion.div>
      )}

      {/* Swipeable content */}
      <motion.div
        drag="x"
        dragConstraints={{ left: 0, right: 0 }}
        dragElastic={0.1}
        onDragStart={() => setIsDragging(true)}
        onDragEnd={handleDragEnd}
        style={{ x }}
        className="relative bg-white"
      >
        {children}
      </motion.div>
    </div>
  );
}
```

### Bottom Navigation

```typescript
// components/BottomNav.tsx

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import {
  HomeIcon,
  UsersIcon,
  ChartBarIcon,
  BellIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline';
import {
  HomeIcon as HomeIconSolid,
  UsersIcon as UsersIconSolid,
  ChartBarIcon as ChartBarIconSolid,
  BellIcon as BellIconSolid,
  UserCircleIcon as UserCircleIconSolid,
} from '@heroicons/react/24/solid';

const navItems = [
  { href: '/dashboard', label: 'Home', icon: HomeIcon, activeIcon: HomeIconSolid },
  { href: '/teams', label: 'Teams', icon: UsersIcon, activeIcon: UsersIconSolid },
  { href: '/predictions', label: 'Stats', icon: ChartBarIcon, activeIcon: ChartBarIconSolid },
  { href: '/notifications', label: 'Alerts', icon: BellIcon, activeIcon: BellIconSolid },
  { href: '/profile', label: 'Profile', icon: UserCircleIcon, activeIcon: UserCircleIconSolid },
];

export function BottomNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 pb-safe md:hidden">
      <div className="flex justify-around items-center h-16">
        {navItems.map(({ href, label, icon: Icon, activeIcon: ActiveIcon }) => {
          const isActive = pathname.startsWith(href);
          const IconComponent = isActive ? ActiveIcon : Icon;

          return (
            <Link
              key={href}
              href={href}
              className={cn(
                'flex flex-col items-center justify-center w-full h-full',
                'min-w-[44px] min-h-[44px]', // Touch-friendly tap target
                'transition-colors',
                isActive ? 'text-blue-600' : 'text-gray-500'
              )}
            >
              <IconComponent className="w-6 h-6" />
              <span className="text-xs mt-1">{label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
```

---

## Example Implementations

### Authentication Flow Component

```typescript
// app/(auth)/login/page.tsx

'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { tokenStorage } from '@/lib/token-storage';
import { TouchButton } from '@/components/ui/TouchButton';
import toast from 'react-hot-toast';

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // Show session expired message
  const sessionExpired = searchParams.get('session_expired') === 'true';

  const loginMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.post('/auth/login', {
        email,
        password,
        device_info: {
          platform: navigator.platform,
          browser: navigator.userAgent,
          device_id: localStorage.getItem('device_id') || crypto.randomUUID(),
        },
      });
      return response.data;
    },
    onSuccess: async (data) => {
      await tokenStorage.setTokens({
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        expiresAt: Date.now() + data.expires_in * 1000,
        refreshExpiresAt: Date.now() + data.refresh_expires_in * 1000,
      });

      toast.success('Welcome back!');
      router.push('/dashboard');
    },
    onError: (error: any) => {
      const message = error.response?.data?.error?.message || 'Login failed';
      toast.error(message);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loginMutation.mutate();
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <h1 className="text-2xl font-bold text-center mb-8">
          Fantasy Basketball Analyzer
        </h1>

        {sessionExpired && (
          <div className="bg-yellow-50 text-yellow-800 p-4 rounded-lg mb-6">
            Your session has expired. Please log in again.
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full h-12 px-4 border rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full h-12 px-4 border rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <TouchButton
            type="submit"
            size="lg"
            className="w-full"
            disabled={loginMutation.isPending}
          >
            {loginMutation.isPending ? 'Signing in...' : 'Sign In'}
          </TouchButton>
        </form>
      </div>
    </div>
  );
}
```

### Dashboard with Real-Time Updates

```typescript
// app/dashboard/page.tsx

'use client';

import { useQuery } from '@tanstack/react-query';
import { useRealTimeUpdates } from '@/hooks/useRealTimeUpdates';
import { usePullToRefresh } from '@/hooks/usePullToRefresh';
import { apiClient } from '@/lib/api-client';
import { Team, Recommendation } from '@/types/api';
import { RefreshIndicator } from '@/components/ui/RefreshIndicator';
import { TeamCard } from '@/components/TeamCard';
import { RecommendationCard } from '@/components/RecommendationCard';
import { BottomNav } from '@/components/BottomNav';

export default function DashboardPage() {
  // Fetch teams
  const teamsQuery = useQuery({
    queryKey: ['teams'],
    queryFn: async () => {
      const response = await apiClient.get<{ teams: Team[] }>('/teams');
      return response.data.teams;
    },
  });

  // Real-time updates
  const selectedTeamId = teamsQuery.data?.[0]?.id;
  useRealTimeUpdates(selectedTeamId);

  // Pull to refresh
  const { containerRef, isRefreshing, pullProgress } = usePullToRefresh({
    onRefresh: async () => {
      await teamsQuery.refetch();
    },
  });

  // Fetch recommendations for first team
  const recommendationsQuery = useQuery({
    queryKey: ['recommendations', selectedTeamId],
    queryFn: async () => {
      if (!selectedTeamId) return [];
      const response = await apiClient.get<{ recommendations: Recommendation[] }>(
        `/recommendations/${selectedTeamId}`
      );
      return response.data.recommendations;
    },
    enabled: !!selectedTeamId,
  });

  return (
    <div
      ref={containerRef}
      className="min-h-screen pb-20 md:pb-0 overflow-y-auto"
    >
      {/* Pull to refresh indicator */}
      <RefreshIndicator
        isRefreshing={isRefreshing}
        progress={pullProgress}
      />

      <div className="max-w-7xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

        {/* Teams Section */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-4">Your Teams</h2>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {teamsQuery.data?.map((team) => (
              <TeamCard key={team.id} team={team} />
            ))}
          </div>
        </section>

        {/* Recommendations Section */}
        <section>
          <h2 className="text-lg font-semibold mb-4">Today's Recommendations</h2>
          <div className="space-y-4">
            {recommendationsQuery.data?.slice(0, 5).map((rec) => (
              <RecommendationCard key={rec.id} recommendation={rec} />
            ))}
          </div>
        </section>
      </div>

      {/* Mobile bottom navigation */}
      <BottomNav />
    </div>
  );
}
```

---

## Error Handling

### Error Types

```typescript
// lib/errors.ts

export class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public status?: number,
    public details?: Record<string, unknown>,
    public requestId?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }

  static fromResponse(response: any): ApiError {
    const { error } = response;
    return new ApiError(
      error?.code || 'UNKNOWN_ERROR',
      error?.message || 'An unknown error occurred',
      response.status,
      error?.details,
      error?.request_id
    );
  }

  get isRetryable(): boolean {
    return this.status ? this.status >= 500 || this.status === 429 : true;
  }

  get isAuthError(): boolean {
    return this.status === 401 || this.status === 403;
  }
}

export class NetworkError extends Error {
  constructor(message = 'Network error. Please check your connection.') {
    super(message);
    this.name = 'NetworkError';
  }
}

export class OfflineError extends Error {
  constructor(message = 'You are offline. Some features may be unavailable.') {
    super(message);
    this.name = 'OfflineError';
  }
}
```

### Global Error Handler

```typescript
// components/GlobalErrorHandler.tsx

import { useEffect } from 'react';
import toast from 'react-hot-toast';

export function GlobalErrorHandler() {
  useEffect(() => {
    const handleOnline = () => {
      toast.success('Back online!');
    };

    const handleOffline = () => {
      toast.error('You are offline', {
        duration: Infinity,
        id: 'offline-toast',
      });
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      console.error('Unhandled promise rejection:', event.reason);

      // Don't show toast for handled errors
      if (event.reason?.handled) return;

      toast.error('Something went wrong. Please try again.');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    window.addEventListener('unhandledrejection', handleUnhandledRejection);

    // Check initial state
    if (!navigator.onLine) {
      handleOffline();
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
    };
  }, []);

  return null;
}
```

---

## State Management

### Auth Context

```typescript
// contexts/AuthContext.tsx

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { tokenStorage } from '@/lib/token-storage';
import { apiClient } from '@/lib/api-client';
import { User } from '@/types/api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const tokens = await tokenStorage.getTokens();
      if (tokens && await tokenStorage.isAccessTokenValid()) {
        await refreshUser();
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshUser = async () => {
    const response = await apiClient.get<User>('/auth/me');
    setUser(response.data);
  };

  const login = async (email: string, password: string) => {
    const response = await apiClient.post('/auth/login', { email, password });
    const { access_token, refresh_token, expires_in, refresh_expires_in, user: userData } = response.data;

    await tokenStorage.setTokens({
      accessToken: access_token,
      refreshToken: refresh_token,
      expiresAt: Date.now() + expires_in * 1000,
      refreshExpiresAt: Date.now() + refresh_expires_in * 1000,
    });

    setUser(userData);
  };

  const logout = async () => {
    const tokens = await tokenStorage.getTokens();

    if (tokens) {
      try {
        await apiClient.post('/auth/logout', {
          refresh_token: tokens.refreshToken,
        });
      } catch (error) {
        console.error('Logout API error:', error);
      }
    }

    await tokenStorage.clearTokens();
    setUser(null);
    router.push('/login');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

---

## Performance Optimization

### Image Optimization

```typescript
// components/PlayerAvatar.tsx

import Image from 'next/image';
import { useState } from 'react';

interface PlayerAvatarProps {
  src?: string;
  name: string;
  size?: 'sm' | 'md' | 'lg';
}

const sizes = {
  sm: 32,
  md: 48,
  lg: 64,
};

export function PlayerAvatar({ src, name, size = 'md' }: PlayerAvatarProps) {
  const [hasError, setHasError] = useState(false);
  const dimension = sizes[size];
  const initials = name.split(' ').map(n => n[0]).join('').slice(0, 2);

  if (!src || hasError) {
    return (
      <div
        className="flex items-center justify-center bg-gray-200 rounded-full text-gray-600 font-medium"
        style={{ width: dimension, height: dimension }}
      >
        {initials}
      </div>
    );
  }

  return (
    <Image
      src={src}
      alt={name}
      width={dimension}
      height={dimension}
      className="rounded-full object-cover"
      onError={() => setHasError(true)}
      loading="lazy"
    />
  );
}
```

### Virtual List for Large Data

```typescript
// components/VirtualPlayerList.tsx

import { useVirtualizer } from '@tanstack/react-virtual';
import { useRef } from 'react';
import { Player } from '@/types/api';
import { PlayerCard } from './PlayerCard';

interface VirtualPlayerListProps {
  players: Player[];
  onSelectPlayer: (player: Player) => void;
}

export function VirtualPlayerList({ players, onSelectPlayer }: VirtualPlayerListProps) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: players.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 80, // Estimated row height
    overscan: 5,
  });

  return (
    <div
      ref={parentRef}
      className="h-[600px] overflow-auto"
    >
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((virtualRow) => {
          const player = players[virtualRow.index];
          return (
            <div
              key={virtualRow.key}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: `${virtualRow.size}px`,
                transform: `translateY(${virtualRow.start}px)`,
              }}
            >
              <PlayerCard
                player={player}
                onClick={() => onSelectPlayer(player)}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

---

## Deployment & CORS

### Environment Variables

```bash
# .env.local

# API Configuration
NEXT_PUBLIC_API_URL=https://api.fantasyhoops.com/api/v1
NEXT_PUBLIC_WS_URL=wss://api.fantasyhoops.com/ws
NEXT_PUBLIC_ML_URL=https://api.fantasyhoops.com/ml/v1

# Firebase (Push Notifications)
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789:web:abcdef
NEXT_PUBLIC_FIREBASE_VAPID_KEY=your_vapid_key

# Yahoo OAuth
NEXT_PUBLIC_YAHOO_CLIENT_ID=your_yahoo_client_id
NEXT_PUBLIC_YAHOO_REDIRECT_URI=https://app.fantasyhoops.com/auth/yahoo/callback
```

### Deployment Checklist

#### Frontend (Vercel)
- [ ] Set all environment variables
- [ ] Configure custom domain
- [ ] Enable HTTPS
- [ ] Set up preview deployments
- [ ] Configure headers for security
- [ ] Test PWA manifest
- [ ] Verify service worker registration

#### Backend Requirements
- [ ] CORS configured for frontend domain
- [ ] WebSocket endpoint enabled
- [ ] FCM credentials configured
- [ ] Rate limiting enabled
- [ ] Health check endpoint

### Security Headers

```typescript
// next.config.js

const securityHeaders = [
  {
    key: 'X-DNS-Prefetch-Control',
    value: 'on',
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload',
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY',
  },
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block',
  },
  {
    key: 'Referrer-Policy',
    value: 'origin-when-cross-origin',
  },
];

module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: securityHeaders,
      },
    ];
  },
};
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| CORS errors | Backend not configured | Add frontend domain to CORS origins |
| 401 Unauthorized | Token expired | Check token refresh logic |
| WebSocket disconnects | Network issues | Implement reconnection with backoff |
| Push notifications not received | FCM token not registered | Re-register FCM token on app start |
| Offline data stale | IndexedDB not synced | Implement background sync |
| Slow initial load | Large bundle | Enable code splitting, lazy loading |

### Debug Mode

```typescript
// lib/debug.ts

export const DEBUG = process.env.NODE_ENV === 'development';

export const debugLog = (...args: any[]) => {
  if (DEBUG) {
    console.log('[Fantasy Debug]', ...args);
  }
};

export const debugWarn = (...args: any[]) => {
  if (DEBUG) {
    console.warn('[Fantasy Debug]', ...args);
  }
};

export const debugError = (...args: any[]) => {
  if (DEBUG) {
    console.error('[Fantasy Debug]', ...args);
  }
};
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-11 | Initial release |
| 2.0 | 2025-01-15 | Added WebSocket, PWA, mobile-first, push notifications, enhanced auth |

---

**Questions or Issues?**
- Backend API docs: `https://api.fantasyhoops.com/docs`
- WebSocket events: See [WebSocket Integration](#websocket-integration)
- Offline support: See [PWA & Offline Support](#pwa--offline-support)
