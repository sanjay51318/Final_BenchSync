import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Bot, AlertTriangle, CheckCircle, Clock, RefreshCw } from 'lucide-react';

export interface AgentTask {
  id: string;
  type: 'resume_analysis' | 'opportunity_matching' | 'training_recommendation' | 'attendance_report';
  status: 'queued' | 'processing' | 'completed' | 'error';
  consultantName: string;
  createdAt: string;
  completedAt?: string;
  progress: number;
  error?: string;
  latency: number;
}

interface AIAgentQueueProps {
  tasks: AgentTask[];
  onRefresh: () => void;
  onRetryTask: (taskId: string) => void;
}

export function AIAgentQueue({ tasks, onRefresh, onRetryTask }: AIAgentQueueProps) {
  const getTaskIcon = (type: string) => {
    switch (type) {
      case 'resume_analysis':
        return '📄';
      case 'opportunity_matching':
        return '🎯';
      case 'training_recommendation':
        return '🎓';
      case 'attendance_report':
        return '📊';
      default:
        return '⚙️';
    }
  };

  const getTaskLabel = (type: string) => {
    switch (type) {
      case 'resume_analysis':
        return 'Resume Analysis';
      case 'opportunity_matching':
        return 'Opportunity Matching';
      case 'training_recommendation':
        return 'Training Recommendation';
      case 'attendance_report':
        return 'Attendance Report';
      default:
        return 'Unknown Task';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'queued':
        return <Badge variant="outline"><Clock className="w-3 h-3 mr-1" />Queued</Badge>;
      case 'processing':
        return <Badge className="bg-status-in-progress text-white"><RefreshCw className="w-3 h-3 mr-1 animate-spin" />Processing</Badge>;
      case 'completed':
        return <Badge className="bg-status-completed text-white"><CheckCircle className="w-3 h-3 mr-1" />Completed</Badge>;
      case 'error':
        return <Badge className="bg-status-missed text-white"><AlertTriangle className="w-3 h-3 mr-1" />Error</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  const getLatencyColor = (latency: number) => {
    if (latency < 2000) return 'text-status-completed';
    if (latency < 5000) return 'text-status-pending';
    return 'text-status-missed';
  };

  const stats = {
    total: tasks.length,
    queued: tasks.filter(t => t.status === 'queued').length,
    processing: tasks.filter(t => t.status === 'processing').length,
    completed: tasks.filter(t => t.status === 'completed').length,
    errors: tasks.filter(t => t.status === 'error').length
  };

  return (
    <div className="space-y-4">
      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-foreground">{stats.total}</div>
            <div className="text-sm text-muted-foreground">Total Tasks</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-muted-foreground">{stats.queued}</div>
            <div className="text-sm text-muted-foreground">Queued</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-status-in-progress">{stats.processing}</div>
            <div className="text-sm text-muted-foreground">Processing</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-status-completed">{stats.completed}</div>
            <div className="text-sm text-muted-foreground">Completed</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-status-missed">{stats.errors}</div>
            <div className="text-sm text-muted-foreground">Errors</div>
          </CardContent>
        </Card>
      </div>

      {/* Task Queue */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5 text-primary" aria-hidden="true" />
              AI Agent Task Queue
            </CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={onRefresh}
              aria-label="Refresh task queue"
            >
              <RefreshCw className="h-4 w-4 mr-2" aria-hidden="true" />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {tasks.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No active tasks in the queue.
              </div>
            ) : (
              tasks.map((task) => (
                <div key={task.id} className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl" aria-hidden="true">
                        {getTaskIcon(task.type)}
                      </span>
                      <div>
                        <h4 className="font-medium">{getTaskLabel(task.type)}</h4>
                        <p className="text-sm text-muted-foreground">{task.consultantName}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {getStatusBadge(task.status)}
                      {task.status === 'error' && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => onRetryTask(task.id)}
                          aria-label={`Retry task for ${task.consultantName}`}
                        >
                          Retry
                        </Button>
                      )}
                    </div>
                  </div>

                  {/* Progress Bar for Processing Tasks */}
                  {task.status === 'processing' && (
                    <div className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span>Progress</span>
                        <span>{task.progress}%</span>
                      </div>
                      <Progress value={task.progress} className="h-2" />
                    </div>
                  )}

                  {/* Task Details */}
                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <span>Created: {task.createdAt}</span>
                    <div className="flex items-center gap-4">
                      <span className={getLatencyColor(task.latency)}>
                        Latency: {task.latency}ms
                      </span>
                      {task.completedAt && (
                        <span>Completed: {task.completedAt}</span>
                      )}
                    </div>
                  </div>

                  {/* Error Message */}
                  {task.error && (
                    <div className="bg-destructive/10 border border-destructive/20 rounded p-2">
                      <p className="text-sm text-destructive">{task.error}</p>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}