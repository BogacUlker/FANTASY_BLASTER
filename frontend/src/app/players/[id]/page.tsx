'use client';

import { useState, useEffect, use } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart';
import { Line, LineChart, XAxis, YAxis, CartesianGrid } from 'recharts';
import {
  ArrowLeft,
  TrendingUp,
  Calendar,
  MapPin,
  Ruler,
  Scale,
  User,
} from 'lucide-react';
import { playersApi } from '@/lib/api';
import type { Player, PlayerStatsResponse, PlayerGameStats } from '@/types';

const chartConfig: ChartConfig = {
  points: { label: 'Points', color: 'hsl(var(--chart-1))' },
  rebounds: { label: 'Rebounds', color: 'hsl(var(--chart-2))' },
  assists: { label: 'Assists', color: 'hsl(var(--chart-3))' },
};

interface PlayerDetailPageProps {
  params: Promise<{ id: string }>;
}

export default function PlayerDetailPage({ params }: PlayerDetailPageProps) {
  const resolvedParams = use(params);
  const playerId = parseInt(resolvedParams.id);

  const [player, setPlayer] = useState<Player | null>(null);
  const [stats, setStats] = useState<PlayerStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const [playerData, statsData] = await Promise.all([
          playersApi.get(playerId),
          playersApi.getStats(playerId, 20),
        ]);
        setPlayer(playerData);
        setStats(statsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load player');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [playerId]);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Skeleton className="h-8 w-32 mb-8" />
        <div className="grid gap-6 lg:grid-cols-3">
          <Skeleton className="h-64" />
          <Skeleton className="h-64 lg:col-span-2" />
        </div>
      </div>
    );
  }

  if (error || !player) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="max-w-md mx-auto">
          <CardContent className="pt-6 text-center">
            <p className="text-destructive mb-4">{error || 'Player not found'}</p>
            <Button asChild>
              <Link href="/players">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Players
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const chartData = stats?.recent_games.slice(0, 10).reverse().map((game, index) => ({
    game: `G${index + 1}`,
    points: game.points || 0,
    rebounds: game.rebounds || 0,
    assists: game.assists || 0,
  })) || [];

  const getInjuryBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
        return <Badge className="bg-green-500">Healthy</Badge>;
      case 'questionable':
        return <Badge className="bg-yellow-500 text-black">Questionable</Badge>;
      case 'out':
        return <Badge variant="destructive">Out</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Back Button */}
      <Button variant="ghost" className="mb-6" asChild>
        <Link href="/players">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Players
        </Link>
      </Button>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Player Info Card */}
        <Card>
          <CardHeader className="text-center">
            <div className="mx-auto h-24 w-24 rounded-full bg-muted flex items-center justify-center mb-4">
              <User className="h-12 w-12 text-muted-foreground" />
            </div>
            <CardTitle className="text-2xl">{player.full_name}</CardTitle>
            <CardDescription className="flex items-center justify-center gap-2">
              <Badge variant="outline">{player.team_abbreviation || 'FA'}</Badge>
              <Badge variant="secondary">{player.position || 'N/A'}</Badge>
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground flex items-center gap-2">
                  <Ruler className="h-4 w-4" /> Height
                </span>
                <span className="font-medium">{player.height || 'N/A'}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground flex items-center gap-2">
                  <Scale className="h-4 w-4" /> Weight
                </span>
                <span className="font-medium">{player.weight ? `${player.weight} lbs` : 'N/A'}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground flex items-center gap-2">
                  <Calendar className="h-4 w-4" /> Birth Date
                </span>
                <span className="font-medium">
                  {player.birth_date
                    ? new Date(player.birth_date).toLocaleDateString()
                    : 'N/A'}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground flex items-center gap-2">
                  <MapPin className="h-4 w-4" /> Country
                </span>
                <span className="font-medium">{player.country || 'USA'}</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Status</span>
                {getInjuryBadge(player.injury_status)}
              </div>
            </div>

            <div className="mt-6">
              <Button className="w-full" asChild>
                <Link href={`/predictions?player=${player.id}`}>
                  <TrendingUp className="mr-2 h-4 w-4" />
                  Get Predictions
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Stats Section */}
        <div className="lg:col-span-2 space-y-6">
          {/* Season Averages */}
          {stats?.season_averages && Object.keys(stats.season_averages).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Season Averages</CardTitle>
                <CardDescription>
                  Based on {stats.season_averages.games_played || 0} games
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-4 gap-4 text-center">
                  {[
                    { label: 'PTS', value: stats.season_averages.points },
                    { label: 'REB', value: stats.season_averages.rebounds },
                    { label: 'AST', value: stats.season_averages.assists },
                    { label: 'MIN', value: stats.season_averages.minutes },
                  ].map((stat) => (
                    <div key={stat.label} className="p-3 rounded-lg bg-muted">
                      <p className="text-2xl font-bold">{stat.value?.toFixed(1) || '0.0'}</p>
                      <p className="text-xs text-muted-foreground">{stat.label}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Performance Chart & Game Log */}
          <Tabs defaultValue="chart">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="chart">Performance Chart</TabsTrigger>
              <TabsTrigger value="games">Game Log</TabsTrigger>
            </TabsList>

            <TabsContent value="chart">
              <Card>
                <CardHeader>
                  <CardTitle>Recent Performance</CardTitle>
                  <CardDescription>Points, Rebounds, and Assists over last 10 games</CardDescription>
                </CardHeader>
                <CardContent>
                  {chartData.length > 0 ? (
                    <ChartContainer config={chartConfig} className="h-[300px] w-full">
                      <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="game" tickLine={false} axisLine={false} />
                        <YAxis tickLine={false} axisLine={false} />
                        <ChartTooltip content={<ChartTooltipContent />} />
                        <Line
                          type="monotone"
                          dataKey="points"
                          stroke="var(--color-points)"
                          strokeWidth={2}
                          dot={false}
                        />
                        <Line
                          type="monotone"
                          dataKey="rebounds"
                          stroke="var(--color-rebounds)"
                          strokeWidth={2}
                          dot={false}
                        />
                        <Line
                          type="monotone"
                          dataKey="assists"
                          stroke="var(--color-assists)"
                          strokeWidth={2}
                          dot={false}
                        />
                      </LineChart>
                    </ChartContainer>
                  ) : (
                    <p className="text-center text-muted-foreground py-8">
                      No game data available
                    </p>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="games">
              <Card>
                <CardHeader>
                  <CardTitle>Recent Games</CardTitle>
                </CardHeader>
                <CardContent>
                  {stats?.recent_games && stats.recent_games.length > 0 ? (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Date</TableHead>
                          <TableHead className="text-center">MIN</TableHead>
                          <TableHead className="text-center">PTS</TableHead>
                          <TableHead className="text-center">REB</TableHead>
                          <TableHead className="text-center">AST</TableHead>
                          <TableHead className="text-center">STL</TableHead>
                          <TableHead className="text-center">BLK</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {stats.recent_games.slice(0, 10).map((game, i) => (
                          <TableRow key={i}>
                            <TableCell>
                              {new Date(game.game_date).toLocaleDateString()}
                            </TableCell>
                            <TableCell className="text-center">
                              {game.minutes_played?.toFixed(0) || '-'}
                            </TableCell>
                            <TableCell className="text-center font-medium">
                              {game.points || 0}
                            </TableCell>
                            <TableCell className="text-center">{game.rebounds || 0}</TableCell>
                            <TableCell className="text-center">{game.assists || 0}</TableCell>
                            <TableCell className="text-center">{game.steals || 0}</TableCell>
                            <TableCell className="text-center">{game.blocks || 0}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  ) : (
                    <p className="text-center text-muted-foreground py-8">
                      No game data available
                    </p>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
