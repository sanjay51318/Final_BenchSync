import React from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Eye, Download, Users } from 'lucide-react';

export interface Consultant {
  id: string;
  name: string;
  email: string;
  department: string;
  primarySkill: string;
  resumeStatus: 'updated' | 'pending' | 'outdated';
  attendanceRate: number;
  trainingStatus: 'completed' | 'in-progress' | 'not-started' | 'overdue';
  opportunitiesCount: number;
  benchStartDate: string;
}

interface ConsultantTableProps {
  consultants: Consultant[];
  onViewDetails: (consultant: Consultant) => void;
  onExportData: () => void;
}

export function ConsultantTable({ consultants, onViewDetails, onExportData }: ConsultantTableProps) {
  const getStatusBadge = (status: string, type: 'resume' | 'training') => {
    if (type === 'resume') {
      switch (status) {
        case 'updated':
          return <Badge className="bg-status-completed text-white">Updated</Badge>;
        case 'pending':
          return <Badge className="bg-status-pending text-foreground">Pending</Badge>;
        case 'outdated':
          return <Badge className="bg-status-missed text-white">Outdated</Badge>;
        default:
          return <Badge variant="outline">Unknown</Badge>;
      }
    } else {
      switch (status) {
        case 'completed':
          return <Badge className="bg-status-completed text-white">Completed</Badge>;
        case 'in-progress':
          return <Badge className="bg-status-in-progress text-white">In Progress</Badge>;
        case 'not-started':
          return <Badge variant="outline">Not Started</Badge>;
        case 'overdue':
          return <Badge className="bg-status-missed text-white">Overdue</Badge>;
        default:
          return <Badge variant="outline">Unknown</Badge>;
      }
    }
  };

  const getAttendanceColor = (rate: number) => {
    if (rate >= 90) return 'text-status-completed';
    if (rate >= 75) return 'text-status-in-progress';
    if (rate >= 60) return 'text-status-pending';
    return 'text-status-missed';
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5 text-primary" aria-hidden="true" />
            Consultant Overview ({consultants.length})
          </CardTitle>
          <Button
            onClick={onExportData}
            variant="outline"
            size="sm"
            aria-label="Export consultant data to CSV"
          >
            <Download className="h-4 w-4 mr-2" aria-hidden="true" />
            Export CSV
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Consultant</TableHead>
                <TableHead>Department</TableHead>
                <TableHead>Primary Skill</TableHead>
                <TableHead>Resume Status</TableHead>
                <TableHead>Attendance</TableHead>
                <TableHead>Training</TableHead>
                <TableHead>Opportunities</TableHead>
                <TableHead>Bench Start</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {consultants.map((consultant) => (
                <TableRow key={consultant.id}>
                  <TableCell>
                    <div>
                      <div className="font-medium">{consultant.name}</div>
                      <div className="text-sm text-muted-foreground">{consultant.email}</div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{consultant.department}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant="secondary">{consultant.primarySkill}</Badge>
                  </TableCell>
                  <TableCell>
                    {getStatusBadge(consultant.resumeStatus, 'resume')}
                  </TableCell>
                  <TableCell>
                    <span className={`font-medium ${getAttendanceColor(consultant.attendanceRate)}`}>
                      {consultant.attendanceRate}%
                    </span>
                  </TableCell>
                  <TableCell>
                    {getStatusBadge(consultant.trainingStatus, 'training')}
                  </TableCell>
                  <TableCell>
                    <span className="font-medium">{consultant.opportunitiesCount}</span>
                  </TableCell>
                  <TableCell>
                    <span className="text-sm">{consultant.benchStartDate}</span>
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onViewDetails(consultant)}
                      aria-label={`View details for ${consultant.name}`}
                    >
                      <Eye className="h-4 w-4 mr-2" aria-hidden="true" />
                      View
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          
          {consultants.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              No consultants found matching your criteria.
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}