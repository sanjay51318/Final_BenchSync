import React, { useState, useEffect, useMemo } from 'react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { differenceInDays, parseISO } from "date-fns";
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Loader2,
  Eye,
  Activity,
  Target
} from 'lucide-react';

// API configuration
const API_BASE_URL = 'http://localhost:8000';

// Opportunity interface
interface Opportunity {
  id: string;
  title: string;
  description: string;
  client_name: string;
  required_skills: string[];
  experience_level: string;
  project_duration: string;
  budget_range: string;
  start_date: string;
  end_date: string;
  status: string;
  created_at: string;
  applications?: Application[];
  accepted_count?: number;
}

// Application interface
interface Application {
  id: string;
  consultant_id: string;
  consultant_name: string;
  consultant_email: string;
  consultant_skills: string[];
  experience_years: number;
  status: 'pending' | 'accepted' | 'declined';
  applied_date: string;
  match_score?: number;
}

// Enhanced consultant interface
interface Consultant {
  id: string;
}

// Analytics interface
interface OpportunityAnalytics {
  success: boolean;
  analytics: {
    overview: {
      total_opportunities: number;
      open_opportunities: number;
      closed_opportunities: number;
      in_progress_opportunities: number;
      total_applications: number;
      pending_applications: number;
      accepted_applications: number;
      declined_applications: number;
      overall_success_rate: number;
    };
    opportunity_details: Array<{
      opportunity_id: string;
      title: string;
      company: string;
      total_applications: number;
      pending_applications: number;
      accepted_applications: number;
      declined_applications: number;
      match_rate: number;
      status: string;
      created_date: string;
    }>;
    consultant_engagement: Array<{
      consultant_id: string;
      name: string;
      email: string;
      total_applications: number;
      accepted_applications: number;
      pending_applications: number;
      success_rate: number;
      status: string;
    }>;
    skills_demand: {
      top_skills: Array<{ skill: string; demand_count: number }>;
      total_unique_skills: number;
    };
    market_trends: {
      opportunities_created_last_30_days: number;
      applications_last_30_days: number;
      average_time_to_fill: string;
      most_active_companies: Array<{ company: string; opportunities: number }>;
    };
    last_updated: string;
  };
}

// Enhanced consultant interface
interface Consultant {
  id: string;
  name: string;
  email: string;
  skills: string[];
  experience_years: number;
  status: string;
  availability_status: string;
}

// Helper for CSV export
const exportToCSV = (data: Opportunity[], filename = "opportunities.csv") => {
  const csvRows = [
    ["Title", "Description", "Client", "Start Date", "End Date", "Status", "Budget"],
    ...data.map(opp => [
      opp.title, opp.description, opp.client_name, opp.start_date, opp.end_date, opp.status, opp.budget_range
    ])
  ];
  const csvContent = csvRows.map(e => e.join(",")).join("\n");
  const blob = new Blob([csvContent], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
};

const OpportunitiesAdmin: React.FC = () => {
  // State for opportunities from API
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(false);
  const [processingApplications, setProcessingApplications] = useState<Set<string>>(new Set());
  
  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [clientName, setClientName] = useState('');
  const [requiredSkills, setRequiredSkills] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('mid');
  const [projectDuration, setProjectDuration] = useState('');
  const [budgetRange, setBudgetRange] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  // Search, filter, sort, pagination
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [sortBy, setSortBy] = useState<'startDate' | 'endDate' | 'duration' | 'status'>('startDate');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');
  const [page, setPage] = useState(1);
  const pageSize = 5;

  // Analytics state
  const [analytics, setAnalytics] = useState<OpportunityAnalytics | null>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);

  // Fetch analytics data
  const fetchAnalytics = async () => {
    try {
      setAnalyticsLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/opportunity-analytics`);
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      } else {
        console.error('Failed to fetch analytics');
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setAnalyticsLoading(false);
    }
  };

  // Fetch opportunities from API with applications
  const fetchOpportunities = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/opportunities-with-applications`);
      if (response.ok) {
        const data = await response.json();
        setOpportunities(Array.isArray(data) ? data : []);
      } else {
        console.error('Failed to fetch opportunities');
      }
    } catch (error) {
      console.error('Error fetching opportunities:', error);
    } finally {
      setLoading(false);
    }
  };

  // Accept application
  const handleAcceptApplication = async (opportunityId: string, applicationId: string) => {
    try {
      setProcessingApplications(prev => new Set([...prev, applicationId]));
      
      const response = await fetch(`${API_BASE_URL}/api/opportunities/${opportunityId}/applications/${applicationId}/accept`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        // Refresh opportunities to get updated data
        await fetchOpportunities();
      } else {
        console.error('Failed to accept application');
      }
    } catch (error) {
      console.error('Error accepting application:', error);
    } finally {
      setProcessingApplications(prev => {
        const newSet = new Set(prev);
        newSet.delete(applicationId);
        return newSet;
      });
    }
  };

  // Decline application
  const handleDeclineApplication = async (opportunityId: string, applicationId: string) => {
    try {
      setProcessingApplications(prev => new Set([...prev, applicationId]));
      
      const response = await fetch(`${API_BASE_URL}/api/opportunities/${opportunityId}/applications/${applicationId}/decline`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        // Refresh opportunities to get updated data
        await fetchOpportunities();
      } else {
        console.error('Failed to decline application');
      }
    } catch (error) {
      console.error('Error declining application:', error);
    } finally {
      setProcessingApplications(prev => {
        const newSet = new Set(prev);
        newSet.delete(applicationId);
        return newSet;
      });
    }
  };

  // Calculate match score
  const calculateMatchScore = (consultantSkills: string[], requiredSkills: string[]): number => {
    if (!consultantSkills || !requiredSkills || requiredSkills.length === 0) return 0;
    
    const matches = requiredSkills.filter(skill => 
      consultantSkills.some(cSkill => 
        cSkill.toLowerCase().includes(skill.toLowerCase()) || 
        skill.toLowerCase().includes(cSkill.toLowerCase())
      )
    ).length;
    
    return Math.round((matches / requiredSkills.length) * 100);
  };

  useEffect(() => {
    fetchOpportunities();
    fetchAnalytics();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !description || !clientName || !startDate || !endDate) return;

    try {
      const newOpportunityData = {
        title,
        description,
        client_name: clientName,
        required_skills: requiredSkills.split(',').map(skill => skill.trim()).filter(skill => skill),
        experience_level: experienceLevel,
        project_duration: projectDuration,
        budget_range: budgetRange,
        start_date: startDate,
        end_date: endDate
      };

      const response = await fetch(`${API_BASE_URL}/api/opportunities`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newOpportunityData),
      });

      if (response.ok) {
        // Refresh opportunities list
        await fetchOpportunities();
        
        // Clear form
        setTitle('');
        setDescription('');
        setClientName('');
        setRequiredSkills('');
        setProjectDuration('');
        setBudgetRange('');
        setStartDate('');
        setEndDate('');
      } else {
        console.error('Failed to create opportunity');
      }
    } catch (error) {
      console.error('Error creating opportunity:', error);
    }
  };

  const deleteOpportunity = async (id: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/opportunities/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        // Refresh opportunities list
        await fetchOpportunities();
      } else {
        console.error('Failed to delete opportunity');
      }
    } catch (error) {
      console.error('Error deleting opportunity:', error);
      // Fallback to local state update if API fails
      setOpportunities(prev => prev.filter(o => o.id !== id));
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge variant="outline">Pending</Badge>;
      case 'accepted':
        return <Badge className="bg-green-500">Accepted</Badge>;
      case 'declined':
        return <Badge variant="destructive">Declined</Badge>;
      default:
        return <Badge>Unknown</Badge>;
    }
  };

  const getDuration = (start: string, end: string) => {
    if (!start || !end) return "-";
    try {
      const days = differenceInDays(parseISO(end), parseISO(start));
      return days >= 0 ? `${days} day${days !== 1 ? "s" : ""}` : "-";
    } catch {
      return "-";
    }
  };

  // Filter, search, sort, paginate
  let filtered = opportunities.filter(opp =>
    (!search || opp.title.toLowerCase().includes(search.toLowerCase()) || opp.client_name.toLowerCase().includes(search.toLowerCase())) &&
    (!statusFilter || opp.status === statusFilter)
  );
  
  filtered = filtered.sort((a, b) => {
    let valA: number | string = '';
    let valB: number | string = '';
    switch (sortBy) {
      case 'startDate':
        valA = new Date(String(a.start_date)).getTime();
        valB = new Date(String(b.start_date)).getTime();
        break;
      case 'endDate':
        valA = new Date(String(a.end_date)).getTime();
        valB = new Date(String(b.end_date)).getTime();
        break;
      case 'duration':
        valA = differenceInDays(parseISO(String(a.end_date)), parseISO(String(a.start_date)));
        valB = differenceInDays(parseISO(String(b.end_date)), parseISO(String(b.start_date)));
        break;
      case 'status':
        valA = a.status;
        valB = b.status;
        break;
      default:
        valA = new Date(String(a.start_date)).getTime();
        valB = new Date(String(b.start_date)).getTime();
    }
    if (typeof valA === 'string' && typeof valB === 'string') {
      if (valA < valB) return sortDir === 'asc' ? -1 : 1;
      if (valA > valB) return sortDir === 'asc' ? 1 : -1;
      return 0;
    } else {
      return sortDir === 'asc'
        ? (valA as number) - (valB as number)
        : (valB as number) - (valA as number);
    }
  });
  
  const totalPages = Math.ceil(filtered.length / pageSize);
  const paged = filtered.slice((page - 1) * pageSize, page * pageSize);

  // Metrics calculation for opportunities
  const opportunityMetrics = useMemo(() => {
    const total = opportunities.length;
    const open = opportunities.filter(o => o.status === 'open').length;
    const assigned = opportunities.filter(o => o.status === 'assigned').length;
    const completed = opportunities.filter(o => o.status === 'completed').length;
    
    return { total, open, assigned, completed };
  }, [opportunities]);

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-primary">Manage Opportunities</h1>
        <p className="text-muted-foreground text-sm mt-1">
          View and manage project opportunities from the database
        </p>
      </div>

      {/* Analytics Dashboard */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Opportunity Analytics
            </CardTitle>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={fetchAnalytics}
                disabled={analyticsLoading}
              >
                {analyticsLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Loading...
                  </>
                ) : (
                  <>
                    <Activity className="mr-2 h-4 w-4" />
                    Refresh Analytics
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowAnalytics(!showAnalytics)}
              >
                <Eye className="mr-2 h-4 w-4" />
                {showAnalytics ? 'Hide' : 'Show'} Analytics
              </Button>
            </div>
          </div>
        </CardHeader>
        {showAnalytics && (
          <CardContent>
            {analytics ? (
              <div className="space-y-6">
                {/* Overview Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="flex items-center gap-2">
                      <Target className="h-5 w-5 text-blue-600" />
                      <span className="text-sm font-medium text-blue-700">Total Opportunities</span>
                    </div>
                    <div className="text-2xl font-bold text-blue-900">
                      {analytics.analytics.overview.total_opportunities}
                    </div>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <span className="text-sm font-medium text-green-700">Success Rate</span>
                    </div>
                    <div className="text-2xl font-bold text-green-900">
                      {analytics.analytics.overview.overall_success_rate}%
                    </div>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <div className="flex items-center gap-2">
                      <Clock className="h-5 w-5 text-yellow-600" />
                      <span className="text-sm font-medium text-yellow-700">Pending Apps</span>
                    </div>
                    <div className="text-2xl font-bold text-yellow-900">
                      {analytics.analytics.overview.pending_applications}
                    </div>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <div className="flex items-center gap-2">
                      <Users className="h-5 w-5 text-purple-600" />
                      <span className="text-sm font-medium text-purple-700">Total Apps</span>
                    </div>
                    <div className="text-2xl font-bold text-purple-900">
                      {analytics.analytics.overview.total_applications}
                    </div>
                  </div>
                </div>

                {/* Top Skills in Demand */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-3">Top Skills in Demand</h3>
                    <div className="space-y-2">
                      {analytics.analytics.skills_demand.top_skills.slice(0, 5).map((skill, index) => (
                        <div key={index} className="flex justify-between items-center p-2 bg-muted/50 rounded">
                          <span className="font-medium">{skill.skill}</span>
                          <Badge variant="secondary">{skill.demand_count} opportunities</Badge>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold mb-3">Market Trends</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">New Opportunities (30d)</span>
                        <span className="font-semibold">{analytics.analytics.market_trends.opportunities_created_last_30_days}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Applications (30d)</span>
                        <span className="font-semibold">{analytics.analytics.market_trends.applications_last_30_days}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Avg. Time to Fill</span>
                        <span className="font-semibold">{analytics.analytics.market_trends.average_time_to_fill}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Opportunity Performance */}
                <div>
                  <h3 className="text-lg font-semibold mb-3">Top Performing Opportunities</h3>
                  <div className="space-y-2">
                    {analytics.analytics.opportunity_details
                      .sort((a, b) => b.match_rate - a.match_rate)
                      .slice(0, 3)
                      .map((opp, index) => (
                        <div key={index} className="flex justify-between items-center p-3 border rounded-lg">
                          <div>
                            <span className="font-medium">{opp.title}</span>
                            <span className="text-muted-foreground ml-2">({opp.company})</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <Badge variant={opp.status === 'open' ? 'default' : 'secondary'}>
                              {opp.status}
                            </Badge>
                            <span className="text-sm text-muted-foreground">
                              {opp.total_applications} applications
                            </span>
                            <span className="font-semibold text-green-600">
                              {opp.match_rate}% match rate
                            </span>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>

                <div className="text-xs text-muted-foreground">
                  Last updated: {new Date(analytics.analytics.last_updated).toLocaleString()}
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <AlertCircle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground">Click "Refresh Analytics" to load opportunity analytics</p>
              </div>
            )}
          </CardContent>
        )}
      </Card>

      {/* Create New Opportunity Form */}
      <Card>
        <CardHeader>
          <CardTitle>Create New Opportunity</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input placeholder="Opportunity Title" value={title} onChange={(e) => setTitle(e.target.value)} required />
            <Input placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} required />
            <Input placeholder="Client Name" value={clientName} onChange={(e) => setClientName(e.target.value)} required />
            <Input placeholder="Required Skills (comma-separated)" value={requiredSkills} onChange={(e) => setRequiredSkills(e.target.value)} />
            <div className="flex gap-4">
              <select 
                value={experienceLevel} 
                onChange={(e) => setExperienceLevel(e.target.value)} 
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
              >
                <option value="junior">Junior</option>
                <option value="mid">Mid-level</option>
                <option value="senior">Senior</option>
                <option value="lead">Lead</option>
              </select>
              <Input placeholder="Project Duration (e.g., 6 months)" value={projectDuration} onChange={(e) => setProjectDuration(e.target.value)} />
            </div>
            <Input placeholder="Budget Range (e.g., $50,000 - $80,000)" value={budgetRange} onChange={(e) => setBudgetRange(e.target.value)} />
            <div className="flex gap-4">
              <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} required />
              <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} required />
            </div>
            <Button type="submit">Create Opportunity</Button>
          </form>
        </CardContent>
      </Card>

      <Separator />

      {/* Opportunity Metrics */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Opportunity Overview</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <Card>
            <CardContent className="py-3">
              <p className="text-2xl font-bold">{opportunityMetrics.total}</p>
              <p className="text-sm text-muted-foreground">Total Opportunities</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="py-3">
              <p className="text-2xl font-bold text-green-600">{opportunityMetrics.open}</p>
              <p className="text-sm text-muted-foreground">Open</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="py-3">
              <p className="text-2xl font-bold text-blue-600">{opportunityMetrics.assigned}</p>
              <p className="text-sm text-muted-foreground">Assigned</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="py-3">
              <p className="text-2xl font-bold text-gray-600">{opportunityMetrics.completed}</p>
              <p className="text-sm text-muted-foreground">Completed</p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Opportunities with Applications */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Opportunities & Applications Management</h2>
        {loading ? (
          <p className="text-muted-foreground">Loading opportunities...</p>
        ) : (
          <div className="space-y-6">
            {paged.map((opp) => (
              <Card key={opp.id} className="overflow-hidden">
                <CardHeader className="bg-muted/30">
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg">{opp.title}</CardTitle>
                      <p className="text-sm text-muted-foreground mt-1">Client: {opp.client_name}</p>
                    </div>
                    <div className="flex gap-2 items-center">
                      {getStatusBadge(opp.status)}
                      <Badge variant="outline">
                        {opp.accepted_count || 0} Accepted
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-0">
                  {/* Opportunity Details */}
                  <div className="p-4 border-b">
                    <p className="mb-2">{opp.description}</p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs text-muted-foreground">
                      <div>
                        <strong>Skills:</strong> {opp.required_skills.join(', ')}
                      </div>
                      <div>
                        <strong>Experience:</strong> {opp.experience_level}
                      </div>
                      <div>
                        <strong>Duration:</strong> {getDuration(opp.start_date, opp.end_date)}
                      </div>
                      <div>
                        <strong>Budget:</strong> {opp.budget_range}
                      </div>
                    </div>
                    <div className="flex gap-2 mt-3">
                      <Button size="sm" variant="destructive" onClick={() => deleteOpportunity(opp.id)}>
                        Delete Opportunity
                      </Button>
                    </div>
                  </div>

                  {/* Applications Section */}
                  <div className="p-4">
                    <h4 className="font-medium mb-3 flex items-center gap-2">
                      Applications ({opp.applications?.length || 0})
                      {(opp.applications?.length || 0) > 0 && (
                        <Badge variant="secondary">
                          {opp.applications?.filter(app => app.status === 'pending').length || 0} Pending
                        </Badge>
                      )}
                    </h4>

                    {!opp.applications || opp.applications.length === 0 ? (
                      <div className="text-center py-8 text-muted-foreground bg-muted/20 rounded-lg">
                        <p>No applications yet for this opportunity</p>
                        <p className="text-xs mt-1">Consultants can apply through their dashboard</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {opp.applications.map((application) => (
                          <div 
                            key={application.id} 
                            className={`p-4 border rounded-lg ${
                              application.status === 'accepted' ? 'bg-green-50 border-green-200' :
                              application.status === 'declined' ? 'bg-red-50 border-red-200' :
                              'bg-white border-gray-200'
                            }`}
                          >
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <h5 className="font-medium">{application.consultant_name}</h5>
                                  <Badge 
                                    variant={
                                      application.status === 'accepted' ? 'default' :
                                      application.status === 'declined' ? 'destructive' :
                                      'secondary'
                                    }
                                  >
                                    {application.status}
                                  </Badge>
                                  <Badge variant="outline">
                                    {calculateMatchScore(application.consultant_skills, opp.required_skills)}% Match
                                  </Badge>
                                </div>
                                
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                                  <div>
                                    <strong>Email:</strong> {application.consultant_email}
                                  </div>
                                  <div>
                                    <strong>Experience:</strong> {application.experience_years} years
                                  </div>
                                  <div>
                                    <strong>Applied:</strong> {application.applied_date}
                                  </div>
                                </div>
                                
                                <div className="mt-2">
                                  <strong>Skills:</strong>
                                  <div className="flex flex-wrap gap-1 mt-1">
                                    {application.consultant_skills.map((skill, index) => (
                                      <Badge 
                                        key={index} 
                                        variant="outline" 
                                        className={`text-xs ${
                                          opp.required_skills.some(reqSkill => 
                                            reqSkill.toLowerCase().includes(skill.toLowerCase()) ||
                                            skill.toLowerCase().includes(reqSkill.toLowerCase())
                                          ) ? 'bg-blue-50 text-blue-700 border-blue-200' : ''
                                        }`}
                                      >
                                        {skill}
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              </div>

                              {/* Action Buttons */}
                              {application.status === 'pending' && (
                                <div className="flex gap-2 ml-4">
                                  <Button
                                    size="sm"
                                    variant="default"
                                    disabled={processingApplications.has(application.id)}
                                    onClick={() => handleAcceptApplication(opp.id, application.id)}
                                    className="bg-green-600 hover:bg-green-700"
                                  >
                                    {processingApplications.has(application.id) ? 'Processing...' : 'Accept'}
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="destructive"
                                    disabled={processingApplications.has(application.id)}
                                    onClick={() => handleDeclineApplication(opp.id, application.id)}
                                  >
                                    {processingApplications.has(application.id) ? 'Processing...' : 'Decline'}
                                  </Button>
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
            
            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex gap-2 mt-6 justify-center">
                <Button size="sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>
                  Previous
                </Button>
                <span className="text-sm mt-2 px-4">
                  Page {page} of {totalPages} ({filtered.length} opportunities)
                </span>
                <Button size="sm" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>
                  Next
                </Button>
              </div>
            )}

            {/* No opportunities message only if truly empty */}
            {opportunities.length === 0 && !loading && (
              <div className="text-center py-12">
                <p className="text-muted-foreground text-lg">No opportunities available</p>
                <p className="text-sm text-muted-foreground mt-2">Create your first opportunity using the form above</p>
              </div>
            )}
          </div>
        )}
      </div>

      {loading && (
        <div className="text-center py-4">
          <p>Loading opportunities...</p>
        </div>
      )}
    </div>
  );
};

export default OpportunitiesAdmin;
