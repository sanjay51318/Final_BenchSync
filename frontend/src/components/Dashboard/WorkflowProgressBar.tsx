import React from 'react';
import { CheckCircle, Circle, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';

interface WorkflowStep {
  id: string;
  label: string;
  completed: boolean;
  inProgress: boolean;
}

interface WorkflowProgressBarProps {
  steps: WorkflowStep[];
  className?: string;
}

export function WorkflowProgressBar({ steps, className }: WorkflowProgressBarProps) {
  return (
    <div className={cn("w-full", className)} role="progressbar" aria-label="Workflow progress">
      <div className="flex flex-col space-y-4 md:flex-row md:space-y-0 md:space-x-2">
        {steps.map((step, index) => {
          const isLast = index === steps.length - 1;
          
          return (
            <div key={step.id} className="flex flex-1 items-center">
              <div className="flex flex-col items-center flex-1 space-y-2">
                {/* Step Icon */}
                <div
                  className={cn(
                    "flex items-center justify-center w-10 h-10 rounded-full border-2 transition-colors",
                    step.completed && "bg-status-completed border-status-completed text-white",
                    step.inProgress && !step.completed && "bg-status-in-progress border-status-in-progress text-white",
                    !step.completed && !step.inProgress && "bg-background border-border text-muted-foreground"
                  )}
                  aria-label={`Step ${index + 1}: ${step.label} - ${
                    step.completed ? 'Completed' : step.inProgress ? 'In Progress' : 'Not Started'
                  }`}
                >
                  {step.completed ? (
                    <CheckCircle className="w-5 h-5" aria-hidden="true" />
                  ) : step.inProgress ? (
                    <Clock className="w-5 h-5" aria-hidden="true" />
                  ) : (
                    <Circle className="w-5 h-5" aria-hidden="true" />
                  )}
                </div>

                {/* Step Label */}
                <span
                  className={cn(
                    "text-sm font-medium text-center max-w-[120px]",
                    step.completed && "text-status-completed",
                    step.inProgress && !step.completed && "text-status-in-progress",
                    !step.completed && !step.inProgress && "text-muted-foreground"
                  )}
                >
                  {step.label}
                </span>
              </div>

              {/* Connector Line */}
              {!isLast && (
                <div 
                  className={cn(
                    "hidden md:block w-full h-0.5 mx-2 transition-colors",
                    step.completed ? "bg-status-completed" : "bg-border"
                  )}
                  aria-hidden="true"
                />
              )}
            </div>
          );
        })}
      </div>

      {/* Mobile connector lines */}
      <div className="md:hidden absolute left-5 top-10 bottom-0 w-0.5 bg-border" aria-hidden="true">
        {steps.slice(0, -1).map((step, index) => (
          <div
            key={`connector-${step.id}`}
            className={cn(
              "w-0.5 h-16 transition-colors",
              step.completed ? "bg-status-completed" : "bg-border"
            )}
          />
        ))}
      </div>
    </div>
  );
}