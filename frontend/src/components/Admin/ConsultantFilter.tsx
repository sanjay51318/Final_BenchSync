import React from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Search, Filter, X } from 'lucide-react';

export interface FilterCriteria {
  searchTerm: string;
  department: string;
  skill: string;
  resumeStatus: string;
  attendanceRate: string;
  trainingStatus: string;
}

interface ConsultantFilterProps {
  filters: FilterCriteria;
  onFiltersChange: (filters: FilterCriteria) => void;
  onClearFilters: () => void;
}

export function ConsultantFilter({ filters, onFiltersChange, onClearFilters }: ConsultantFilterProps) {
  const updateFilter = (key: keyof FilterCriteria, value: string) => {
    onFiltersChange({
      ...filters,
      [key]: value
    });
  };

  const hasActiveFilters = Object.values(filters).some(value => value !== '');

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Filter className="h-5 w-5 text-primary" aria-hidden="true" />
          Search & Filter Consultants
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Search */}
        <div className="space-y-2">
          <Label htmlFor="search">Search</Label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" aria-hidden="true" />
            <Input
              id="search"
              placeholder="Search by name, email, or ID..."
              value={filters.searchTerm}
              onChange={(e) => updateFilter('searchTerm', e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Filter Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="space-y-2">
            <Label htmlFor="department">Department</Label>
            <Select value={filters.department} onValueChange={(value) => updateFilter('department', value)}>
              <SelectTrigger id="department">
                <SelectValue placeholder="All Departments" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Departments</SelectItem>
                <SelectItem value="development">Development</SelectItem>
                <SelectItem value="design">Design</SelectItem>
                <SelectItem value="qa">Quality Assurance</SelectItem>
                <SelectItem value="devops">DevOps</SelectItem>
                <SelectItem value="data">Data Science</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="skill">Primary Skill</Label>
            <Select value={filters.skill} onValueChange={(value) => updateFilter('skill', value)}>
              <SelectTrigger id="skill">
                <SelectValue placeholder="All Skills" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Skills</SelectItem>
                <SelectItem value="react">React</SelectItem>
                <SelectItem value="angular">Angular</SelectItem>
                <SelectItem value="vue">Vue.js</SelectItem>
                <SelectItem value="node">Node.js</SelectItem>
                <SelectItem value="python">Python</SelectItem>
                <SelectItem value="java">Java</SelectItem>
                <SelectItem value="dotnet">.NET</SelectItem>
                <SelectItem value="aws">AWS</SelectItem>
                <SelectItem value="azure">Azure</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="resumeStatus">Resume Status</Label>
            <Select value={filters.resumeStatus} onValueChange={(value) => updateFilter('resumeStatus', value)}>
              <SelectTrigger id="resumeStatus">
                <SelectValue placeholder="All Statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Statuses</SelectItem>
                <SelectItem value="updated">Updated</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="outdated">Outdated</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="attendanceRate">Attendance Rate</Label>
            <Select value={filters.attendanceRate} onValueChange={(value) => updateFilter('attendanceRate', value)}>
              <SelectTrigger id="attendanceRate">
                <SelectValue placeholder="All Rates" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Rates</SelectItem>
                <SelectItem value="excellent">90%+ (Excellent)</SelectItem>
                <SelectItem value="good">75-89% (Good)</SelectItem>
                <SelectItem value="average">60-74% (Average)</SelectItem>
                <SelectItem value="poor">Below 60% (Needs Improvement)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="trainingStatus">Training Status</Label>
            <Select value={filters.trainingStatus} onValueChange={(value) => updateFilter('trainingStatus', value)}>
              <SelectTrigger id="trainingStatus">
                <SelectValue placeholder="All Training Statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Training Statuses</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="in-progress">In Progress</SelectItem>
                <SelectItem value="not-started">Not Started</SelectItem>
                <SelectItem value="overdue">Overdue</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Clear Filters Button */}
          <div className="flex items-end">
            <Button
              variant="outline"
              onClick={onClearFilters}
              disabled={!hasActiveFilters}
              className="w-full"
              aria-label="Clear all filters"
            >
              <X className="h-4 w-4 mr-2" aria-hidden="true" />
              Clear Filters
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}