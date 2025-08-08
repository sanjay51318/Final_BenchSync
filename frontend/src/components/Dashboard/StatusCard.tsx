import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface StatusCardProps {
  title: string;
  value: string | number;
  status?: 'completed' | 'pending' | 'missed' | 'in-progress';
  description?: string;
  icon?: React.ReactNode;
  className?: string;
}

export function StatusCard({ 
  title, 
  value, 
  status, 
  description, 
  icon, 
  className 
}: StatusCardProps) {
  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'completed':
        return 'bg-status-completed text-white';
      case 'pending':
        return 'bg-status-pending text-foreground';
      case 'missed':
        return 'bg-status-missed text-white';
      case 'in-progress':
        return 'bg-status-in-progress text-white';
      default:
        return 'bg-muted text-muted-foreground';
    }
  };

  const getStatusLabel = (status?: string) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'pending':
        return 'Pending';
      case 'missed':
        return 'Missed';
      case 'in-progress':
        return 'In Progress';
      default:
        return 'Unknown';
    }
  };

  return (
    <Card className={cn("h-full", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        {icon && (
          <div className="text-muted-foreground" aria-hidden="true">
            {icon}
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div>
            <div className="text-2xl font-bold text-foreground">
              {value}
            </div>
            {description && (
              <p className="text-xs text-muted-foreground mt-1">
                {description}
              </p>
            )}
          </div>
          {status && (
            <Badge 
              className={cn(getStatusColor(status))}
              aria-label={`Status: ${getStatusLabel(status)}`}
            >
              {getStatusLabel(status)}
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
}