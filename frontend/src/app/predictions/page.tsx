'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart';
import { Bar, BarChart, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Target,
  Zap,
  Search,
  Check,
  ChevronsUpDown,
  AlertCircle,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { playersApi, predictionsApi } from '@/lib/api';
import type { Player, PlayerPrediction, PlayerGameStats } from '@/types';

const statTypes = [
  { value: 'points', label: 'Points', short: 'PTS' },
  { value: 'rebounds', label: 'Rebounds', short: 'REB' },
  { value: 'assists', label: 'Assists', short: 'AST' },
  { value: 'steals', label: 'Steals', short: 'STL' },
  { value: 'blocks', label: 'Blocks', short: 'BLK' },
  { value: 'fg3m', label: '3-Pointers Made', short: '3PM' },
  { value: 'turnovers', label: 'Turnovers', short: 'TO' },
  { value: 'minutes_played', label: 'Minutes', short: 'MIN' },
];

const chartConfig: ChartConfig = {
  actual: {
    label: 'Actual',
    color: 'hsl(var(--chart-1))',
  },
  predicted: {
    label: 'Predicted',
    color: 'hsl(var(--chart-2))',
  },
};

function PredictionsContent() {
  const searchParams = useSearchParams();
  const playerIdParam = searchParams.get('player');

  const [open, setOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [players, setPlayers] = useState<Player[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [statType, setStatType] = useState('points');
  const [bettingLine, setBettingLine] = useState('');
  const [prediction, setPrediction] = useState<PlayerPrediction | null>(null);
  const [recentGames, setRecentGames] = useState<PlayerGameStats[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Search players
  useEffect(() => {
    if (searchQuery.length >= 2) {
      playersApi.autocomplete(searchQuery, 10).then(setPlayers).catch(console.error);
    } else {
      setPlayers([]);
    }
  }, [searchQuery]);

  // Load player from URL param
  useEffect(() => {
    if (playerIdParam) {
      playersApi.get(parseInt(playerIdParam)).then((player) => {
        setSelectedPlayer(player);
      }).catch(console.error);
    }
  }, [playerIdParam]);

  // Load recent games when player selected
  useEffect(() => {
    if (selectedPlayer) {
      playersApi.getStats(selectedPlayer.id, 10).then((stats) => {
        setRecentGames(stats.recent_games);
      }).catch(console.error);
    }
  }, [selectedPlayer]);

  const getPrediction = async () => {
    if (!selectedPlayer) return;

    setLoading(true);
    setError(null);

    try {
      const result = await predictionsApi.create({
        player_id: selectedPlayer.id,
        game_date: new Date().toISOString().split('T')[0],
        stat_type: statType,
        betting_line: bettingLine ? parseFloat(bettingLine) : undefined,
      });
      setPrediction(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get prediction');
    } finally {
      setLoading(false);
    }
  };

  const chartData = recentGames.slice(0, 10).reverse().map((game, index) => {
    const statValue = game[statType as keyof PlayerGameStats] as number || 0;
    return {
      game: `Game ${index + 1}`,
      date: game.game_date,
      actual: statValue,
      predicted: prediction?.predicted_value,
    };
  });

  const selectedStatLabel = statTypes.find(s => s.value === statType)?.label || statType;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Player Predictions</h1>
        <p className="text-muted-foreground">
          Get AI-powered predictions for NBA player statistics using our ML models.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Prediction Form */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Get Prediction</CardTitle>
            <CardDescription>
              Select a player and stat type to generate predictions.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Player Search */}
            <div className="space-y-2">
              <Label>Player</Label>
              <Popover open={open} onOpenChange={setOpen}>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    role="combobox"
                    aria-expanded={open}
                    className="w-full justify-between"
                  >
                    {selectedPlayer ? selectedPlayer.full_name : 'Search players...'}
                    <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-full p-0" align="start">
                  <Command>
                    <CommandInput
                      placeholder="Search players..."
                      value={searchQuery}
                      onValueChange={setSearchQuery}
                    />
                    <CommandList>
                      <CommandEmpty>
                        {searchQuery.length < 2 ? 'Type to search...' : 'No players found.'}
                      </CommandEmpty>
                      <CommandGroup>
                        {players.map((player) => (
                          <CommandItem
                            key={player.id}
                            value={player.full_name}
                            onSelect={() => {
                              setSelectedPlayer(player);
                              setOpen(false);
                              setSearchQuery('');
                            }}
                          >
                            <Check
                              className={cn(
                                'mr-2 h-4 w-4',
                                selectedPlayer?.id === player.id ? 'opacity-100' : 'opacity-0'
                              )}
                            />
                            <div>
                              <p className="font-medium">{player.full_name}</p>
                              <p className="text-xs text-muted-foreground">
                                {player.team_abbreviation} • {player.position}
                              </p>
                            </div>
                          </CommandItem>
                        ))}
                      </CommandGroup>
                    </CommandList>
                  </Command>
                </PopoverContent>
              </Popover>
            </div>

            {/* Stat Type */}
            <div className="space-y-2">
              <Label>Stat Type</Label>
              <Select value={statType} onValueChange={setStatType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {statTypes.map((stat) => (
                    <SelectItem key={stat.value} value={stat.value}>
                      {stat.label} ({stat.short})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Betting Line (Optional) */}
            <div className="space-y-2">
              <Label>Betting Line (Optional)</Label>
              <Input
                type="number"
                step="0.5"
                placeholder="e.g., 25.5"
                value={bettingLine}
                onChange={(e) => setBettingLine(e.target.value)}
              />
            </div>

            {/* Submit */}
            <Button
              className="w-full"
              onClick={getPrediction}
              disabled={!selectedPlayer || loading}
            >
              {loading ? (
                'Generating...'
              ) : (
                <>
                  <Zap className="mr-2 h-4 w-4" />
                  Get Prediction
                </>
              )}
            </Button>

            {error && (
              <div className="flex items-center gap-2 text-destructive text-sm">
                <AlertCircle className="h-4 w-4" />
                {error}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Results */}
        <div className="lg:col-span-2 space-y-6">
          {/* Prediction Result */}
          {prediction && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      <Target className="h-5 w-5 text-primary" />
                      Prediction Result
                    </CardTitle>
                    <CardDescription>
                      {selectedPlayer?.full_name} - {selectedStatLabel}
                    </CardDescription>
                  </div>
                  <Badge variant="outline" className="text-sm">
                    {Math.round(prediction.confidence * 100)}% Confidence
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 sm:grid-cols-3">
                  <div className="text-center p-4 rounded-lg bg-muted">
                    <p className="text-sm text-muted-foreground mb-1">Predicted</p>
                    <p className="text-3xl font-bold text-primary">
                      {prediction.predicted_value.toFixed(1)}
                    </p>
                  </div>

                  {prediction.betting_line && (
                    <>
                      <div className="text-center p-4 rounded-lg bg-green-500/10">
                        <p className="text-sm text-muted-foreground mb-1 flex items-center justify-center gap-1">
                          <TrendingUp className="h-4 w-4 text-green-500" />
                          Over {prediction.betting_line}
                        </p>
                        <p className="text-2xl font-bold text-green-500">
                          {((prediction.over_probability || 0) * 100).toFixed(0)}%
                        </p>
                      </div>
                      <div className="text-center p-4 rounded-lg bg-red-500/10">
                        <p className="text-sm text-muted-foreground mb-1 flex items-center justify-center gap-1">
                          <TrendingDown className="h-4 w-4 text-red-500" />
                          Under {prediction.betting_line}
                        </p>
                        <p className="text-2xl font-bold text-red-500">
                          {((prediction.under_probability || 0) * 100).toFixed(0)}%
                        </p>
                      </div>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Recent Performance Chart */}
          {selectedPlayer && recentGames.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Recent Performance</CardTitle>
                <CardDescription>
                  Last 10 games - {selectedStatLabel}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[300px] w-full">
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis
                      dataKey="game"
                      tickLine={false}
                      axisLine={false}
                      tickMargin={8}
                    />
                    <YAxis tickLine={false} axisLine={false} tickMargin={8} />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <Bar
                      dataKey="actual"
                      fill="var(--color-actual)"
                      radius={[4, 4, 0, 0]}
                    />
                  </BarChart>
                </ChartContainer>
              </CardContent>
            </Card>
          )}

          {/* Empty State */}
          {!selectedPlayer && (
            <Card className="lg:col-span-2">
              <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                <Search className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">Select a Player</h3>
                <p className="text-muted-foreground max-w-sm">
                  Search for an NBA player to view their recent performance and generate predictions.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

export default function PredictionsPage() {
  return (
    <Suspense fallback={
      <div className="container mx-auto px-4 py-8">
        <Skeleton className="h-8 w-64 mb-8" />
        <div className="grid gap-6 lg:grid-cols-3">
          <Skeleton className="h-96" />
          <Skeleton className="h-96 lg:col-span-2" />
        </div>
      </div>
    }>
      <PredictionsContent />
    </Suspense>
  );
}
