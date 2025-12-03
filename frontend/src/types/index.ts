// Player types
export interface Player {
  id: number;
  full_name: string;
  first_name?: string;
  last_name?: string;
  position?: string;
  team_abbreviation?: string;
  jersey_number?: string;
  height?: string;
  weight?: string;
  birth_date?: string;
  country?: string;
  is_active: boolean;
  injury_status: string;
  injury_detail?: string;
}

export interface PlayerListResponse {
  players: Player[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export interface PlayerGameStats {
  game_date: string;
  opponent_team_id?: number;
  is_home?: boolean;
  minutes_played?: number;
  points?: number;
  rebounds?: number;
  assists?: number;
  steals?: number;
  blocks?: number;
  turnovers?: number;
  fg_pct?: number;
  fg3m?: number;
  ft_pct?: number;
}

export interface PlayerStatsResponse {
  player: Player;
  recent_games: PlayerGameStats[];
  season_averages: Record<string, number>;
}

// Prediction types
export interface PlayerPrediction {
  id: number;
  player_id: number;
  game_date: string;
  stat_type: string;
  predicted_value: number;
  confidence: number;
  over_probability?: number;
  under_probability?: number;
  betting_line?: number;
  model_version?: string;
  created_at: string;
}

export interface PredictionRequest {
  player_id: number;
  game_date: string;
  stat_type: string;
  betting_line?: number;
}

// Auth types
export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  tier: 'free' | 'pro' | 'premium';
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Team types
export interface Team {
  id: number;
  full_name: string;
  abbreviation: string;
  nickname: string;
  city: string;
  conference: string;
  division: string;
}
