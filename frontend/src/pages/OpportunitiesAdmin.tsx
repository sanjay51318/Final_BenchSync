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
