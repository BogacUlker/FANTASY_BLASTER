'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';
import {
  Users,
  TrendingUp,
  BarChart3,
  Target,
  ArrowRight,
  Zap,
  Trophy,
  Activity,
} from 'lucide-react';

const stats = [
  {
    title: 'Active Players',
    value: '450+',
    description: 'NBA players tracked',
    icon: Users,
    trend: '+12 this week',
    color: 'text-blue-500',
  },
  {
    title: 'Predictions Today',
    value: '1,234',
    description: 'ML-powered forecasts',
    icon: TrendingUp,
    trend: '89% accuracy',
    color: 'text-green-500',
  },
  {
    title: 'Stat Categories',
    value: '8',
    description: 'PTS, REB, AST, 3PM...',
    icon: BarChart3,
    trend: 'All major stats',
    color: 'text-purple-500',
  },
  {
    title: 'Model Confidence',
    value: '94%',
    description: 'Average prediction confidence',
    icon: Target,
    trend: 'XGBoost + LightGBM',
    color: 'text-orange-500',
  },
];

const features = [
  {
    title: 'Player Analytics',
    description: 'Deep dive into player stats, trends, and performance metrics over time.',
    icon: Activity,
    href: '/players',
  },
  {
    title: 'ML Predictions',
    description: 'Get AI-powered predictions for points, rebounds, assists, and more.',
    icon: Zap,
    href: '/predictions',
  },
  {
    title: 'Fantasy Rankings',
    description: 'See top performers and optimize your fantasy lineup.',
    icon: Trophy,
    href: '/players',
  },
];

export default function HomePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Hero Section */}
      <div className="mb-12 text-center">
        <Badge variant="secondary" className="mb-4">
          Powered by Machine Learning
        </Badge>
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl mb-4">
          Fantasy Basketball
          <span className="text-primary"> Predictions</span>
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
          AI-powered player statistics predictions using advanced ensemble models.
          Make smarter fantasy decisions with data-driven insights.
        </p>
        <div className="flex gap-4 justify-center">
          <Button size="lg" asChild>
            <Link href="/predictions">
              Get Predictions
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link href="/players">Browse Players</Link>
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-12">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">{stat.description}</p>
                <Badge variant="secondary" className="mt-2 text-xs">
                  {stat.trend}
                </Badge>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Features Section */}
      <div className="mb-12">
        <h2 className="text-2xl font-bold mb-6 text-center">Key Features</h2>
        <div className="grid gap-6 md:grid-cols-3">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Card key={feature.title} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-primary/10">
                      <Icon className="h-5 w-5 text-primary" />
                    </div>
                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="mb-4">{feature.description}</CardDescription>
                  <Button variant="ghost" size="sm" asChild>
                    <Link href={feature.href}>
                      Learn More
                      <ArrowRight className="ml-2 h-3 w-3" />
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* CTA Section */}
      <Card className="bg-primary text-primary-foreground">
        <CardContent className="p-8 text-center">
          <h2 className="text-2xl font-bold mb-2">Ready to dominate your fantasy league?</h2>
          <p className="text-primary-foreground/80 mb-6">
            Start using our ML-powered predictions to make smarter decisions.
          </p>
          <Button size="lg" variant="secondary" asChild>
            <Link href="/register">
              Get Started Free
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
