'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { Search, ChevronLeft, ChevronRight, User, TrendingUp } from 'lucide-react';
import Link from 'next/link';
import { playersApi } from '@/lib/api';
import type { Player, PlayerListResponse } from '@/types';

const positions = ['All', 'PG', 'SG', 'SF', 'PF', 'C'];
const teams = [
  'All', 'ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW',
  'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC',
  'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS'
];

function PlayerRowSkeleton() {
  return (
    <TableRow>
      <TableCell><Skeleton className="h-4 w-32" /></TableCell>
      <TableCell><Skeleton className="h-4 w-12" /></TableCell>
      <TableCell><Skeleton className="h-4 w-10" /></TableCell>
      <TableCell><Skeleton className="h-5 w-16" /></TableCell>
      <TableCell><Skeleton className="h-8 w-20" /></TableCell>
    </TableRow>
  );
}

export default function PlayersPage() {
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [position, setPosition] = useState('All');
  const [team, setTeam] = useState('All');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const perPage = 20;

  const fetchPlayers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response: PlayerListResponse = await playersApi.list({
        query: search || undefined,
        team: team !== 'All' ? team : undefined,
        position: position !== 'All' ? position : undefined,
        page,
        per_page: perPage,
      });
      setPlayers(response.players);
      setTotalPages(response.pages);
      setTotal(response.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load players');
      setPlayers([]);
    } finally {
      setLoading(false);
    }
  }, [search, position, team, page]);

  useEffect(() => {
    const debounce = setTimeout(() => {
      fetchPlayers();
    }, 300);
    return () => clearTimeout(debounce);
  }, [fetchPlayers]);

  const getInjuryBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
        return <Badge variant="default" className="bg-green-500">Healthy</Badge>;
      case 'questionable':
        return <Badge variant="secondary" className="bg-yellow-500 text-black">GTD</Badge>;
      case 'out':
        return <Badge variant="destructive">Out</Badge>;
      case 'injured':
        return <Badge variant="destructive">INJ</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">NBA Players</h1>
        <p className="text-muted-foreground">
          Browse and search for NBA players to view their stats and predictions.
        </p>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search players..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
                className="pl-10"
              />
            </div>
            <Select value={position} onValueChange={(v) => { setPosition(v); setPage(1); }}>
              <SelectTrigger className="w-full sm:w-32">
                <SelectValue placeholder="Position" />
              </SelectTrigger>
              <SelectContent>
                {positions.map((pos) => (
                  <SelectItem key={pos} value={pos}>{pos}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={team} onValueChange={(v) => { setTeam(v); setPage(1); }}>
              <SelectTrigger className="w-full sm:w-32">
                <SelectValue placeholder="Team" />
              </SelectTrigger>
              <SelectContent>
                {teams.map((t) => (
                  <SelectItem key={t} value={t}>{t}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Results */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-lg">
            {loading ? 'Loading...' : `${total} Players Found`}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {error ? (
            <div className="text-center py-8 text-destructive">
              <p>{error}</p>
              <Button variant="outline" onClick={fetchPlayers} className="mt-4">
                Try Again
              </Button>
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Player</TableHead>
                    <TableHead>Team</TableHead>
                    <TableHead>Position</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loading ? (
                    Array.from({ length: 10 }).map((_, i) => (
                      <PlayerRowSkeleton key={i} />
                    ))
                  ) : players.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                        No players found matching your criteria.
                      </TableCell>
                    </TableRow>
                  ) : (
                    players.map((player) => (
                      <TableRow key={player.id}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center">
                              <User className="h-5 w-5 text-muted-foreground" />
                            </div>
                            <div>
                              <Link
                                href={`/players/${player.id}`}
                                className="font-medium hover:underline"
                              >
                                {player.full_name}
                              </Link>
                              {player.jersey_number && (
                                <p className="text-xs text-muted-foreground">
                                  #{player.jersey_number}
                                </p>
                              )}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{player.team_abbreviation || 'FA'}</Badge>
                        </TableCell>
                        <TableCell>{player.position || '-'}</TableCell>
                        <TableCell>{getInjuryBadge(player.injury_status)}</TableCell>
                        <TableCell>
                          <Button variant="ghost" size="sm" asChild>
                            <Link href={`/predictions?player=${player.id}`}>
                              <TrendingUp className="h-4 w-4 mr-1" />
                              Predict
                            </Link>
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between mt-4 pt-4 border-t">
                  <p className="text-sm text-muted-foreground">
                    Page {page} of {totalPages}
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      disabled={page === 1}
                    >
                      <ChevronLeft className="h-4 w-4" />
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                      disabled={page === totalPages}
                    >
                      Next
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
