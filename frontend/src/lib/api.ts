import type {
  Player,
  PlayerListResponse,
  PlayerStatsResponse,
  PlayerPrediction,
  PredictionRequest,
  User,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  Team,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
    throw new ApiError(response.status, error.detail || 'An error occurred');
  }

  return response.json();
}

// Player API
export const playersApi = {
  list: (params?: {
    query?: string;
    team?: string;
    position?: string;
    is_active?: boolean;
    page?: number;
    per_page?: number;
  }): Promise<PlayerListResponse> => {
    const searchParams = new URLSearchParams();
    if (params?.query) searchParams.set('query', params.query);
    if (params?.team) searchParams.set('team', params.team);
    if (params?.position) searchParams.set('position', params.position);
    if (params?.is_active !== undefined) searchParams.set('is_active', String(params.is_active));
    if (params?.page) searchParams.set('page', String(params.page));
    if (params?.per_page) searchParams.set('per_page', String(params.per_page));

    const query = searchParams.toString();
    return fetchApi<PlayerListResponse>(`/players${query ? `?${query}` : ''}`);
  },

  get: (id: number): Promise<Player> => {
    return fetchApi<Player>(`/players/${id}`);
  },

  getStats: (id: number, games?: number): Promise<PlayerStatsResponse> => {
    const query = games ? `?games=${games}` : '';
    return fetchApi<PlayerStatsResponse>(`/players/${id}/stats${query}`);
  },

  autocomplete: (query: string, limit?: number): Promise<Player[]> => {
    const params = new URLSearchParams({ q: query });
    if (limit) params.set('limit', String(limit));
    return fetchApi<Player[]>(`/players/search/autocomplete?${params}`);
  },
};

// Predictions API
export const predictionsApi = {
  get: (playerId: number, statType: string, gameDate?: string): Promise<PlayerPrediction> => {
    const params = new URLSearchParams({ stat_type: statType });
    if (gameDate) params.set('game_date', gameDate);
    return fetchApi<PlayerPrediction>(`/predictions/player/${playerId}?${params}`);
  },

  create: (request: PredictionRequest): Promise<PlayerPrediction> => {
    return fetchApi<PlayerPrediction>('/predictions', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  getRecent: (limit?: number): Promise<PlayerPrediction[]> => {
    const query = limit ? `?limit=${limit}` : '';
    return fetchApi<PlayerPrediction[]>(`/predictions/recent${query}`);
  },
};

// Auth API
export const authApi = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new ApiError(response.status, error.detail);
    }

    const data = await response.json();
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', data.access_token);
    }
    return data;
  },

  register: (data: RegisterRequest): Promise<User> => {
    return fetchApi<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  me: (): Promise<User> => {
    return fetchApi<User>('/auth/me');
  },

  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
    }
  },
};

// Teams API
export const teamsApi = {
  list: (): Promise<Team[]> => {
    return fetchApi<Team[]>('/teams');
  },

  get: (id: number): Promise<Team> => {
    return fetchApi<Team>(`/teams/${id}`);
  },
};

export { ApiError };
