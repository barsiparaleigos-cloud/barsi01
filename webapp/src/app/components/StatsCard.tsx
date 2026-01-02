import { Card, CardContent } from './ui/card';
import { LucideIcon } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon: LucideIcon;
  trend?: 'up' | 'down' | 'neutral';
}

export function StatsCard({ title, value, subtitle, icon: Icon, trend = 'neutral' }: StatsCardProps) {
  const trendColors = {
    up: 'text-green-600',
    down: 'text-red-600',
    neutral: 'text-muted-foreground'
  };

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
            {subtitle && (
              <p className={`text-xs ${trendColors[trend]}`}>
                {subtitle}
              </p>
            )}
          </div>
          <div className="bg-primary/10 p-3 rounded-lg">
            <Icon className="size-5 text-primary" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
