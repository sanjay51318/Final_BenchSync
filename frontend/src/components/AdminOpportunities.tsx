import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Plus, Search, Filter, Users, TrendingUp, Clock, DollarSign, Brain } from 'lucide-react';

interface Application {
  id: string;
  consultant_id: string;
  consultant_name: string;
  consultant_email: string;
  consultant_skills: string[];
  experience_years: number;
  status: string;
  applied_date: string;
  applied_at: string;
  cover_letter: string;
  proposed_rate?: string;
}

interface Opportunity {
  id: number;
  title: string;
  description: string;
  client_name: string;
  required_skills: string[];
  experience_level: string;
  project_duration?: string;
  budget_range?: string;
  status: string;
  ai_score?: number;
  ai_recommendations?: string;
  created_at: string;
  start_date?: string;
  end_date?: string;
  applications?: Application[];
  accepted_count?: number;
}

interface Analytics {
  current_metrics?: {
    total_opportunities: number;
    open_opportunities: number;
    filled_opportunities: number;
    total_applications: number;
    fill_rate: number;
  };
  ai_metrics?: {
    avg_opportunity_score: number;
    avg_match_score: number;
    ai_matches_generated: number;
  };
  historical_data?: {
    avg_time_to_fill?: number;
    consultant_satisfaction?: number;
    client_satisfaction?: number;
  };
}

const AdminOpportunities = () => {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<Analytics>({});
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);
  const [activeTab, setActiveTab] = useState('details');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Form state for creating opportunities
  const [newOpportunity, setNewOpportunity] = useState({
    title: '',
    company: 'Default Company', // Hidden field with default value
    client_name: '',
    description: '',
    required_skills: '',
    experience_required: 1,
    location: 'Remote', // Hidden field with default value
    status: 'open',
    project_duration: '',
    budget_range: '',
    start_date: '',
    end_date: ''
  });

  useEffect(() => {
    const loadData = async () => {
      await fetchOpportunities();
      await fetchAnalytics();
    };
    loadData();
  }, [statusFilter]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchOpportunities = async () => {
    try {
      const params = new URLSearchParams();
      if (statusFilter !== 'all') {
        params.append('status', statusFilter);
      }
      
      const response = await fetch(`http://localhost:8000/api/opportunities-with-applications?${params}`);
      const data = await response.json();
      
      if (response.ok) {
        setOpportunities(data || []);
      } else {
        setError(data.detail || 'Failed to fetch opportunities');
      }
    } catch (error) {
      setError('Error connecting to backend');
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/opportunity-analytics');
      const data = await response.json();
      
      if (response.ok) {
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const createOpportunity = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const skillsArray = newOpportunity.required_skills
        .split(',')
        .map(skill => skill.trim())
        .filter(skill => skill);

      // Only send fields that the backend expects
      const opportunityData = {
        title: newOpportunity.title,
        company: newOpportunity.company,
        client_name: newOpportunity.client_name,
        description: newOpportunity.description,
        required_skills: skillsArray,
        experience_required: newOpportunity.experience_required,
        location: newOpportunity.location,
        status: newOpportunity.status
      };

      console.log('Sending opportunity data:', opportunityData); // Debug log

      const response = await fetch('http://localhost:8000/api/opportunities', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(opportunityData),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess('Opportunity created successfully!');
        setIsCreateDialogOpen(false);
        setNewOpportunity({
          title: '',
          company: 'Default Company', // Reset to default
          client_name: '',
          description: '',
          required_skills: '',
          experience_required: 1,
          location: 'Remote', // Reset to default
          status: 'open',
          project_duration: '',
          budget_range: '',
          start_date: '',
          end_date: ''
        });
        fetchOpportunities();
        fetchAnalytics();
      } else {
        console.error('Error response:', data); // Debug log
        if (data.detail) {
          if (Array.isArray(data.detail)) {
            // Handle validation errors from Pydantic
            const errorMessages = data.detail.map(err => `${err.loc?.[1] || 'Field'}: ${err.msg}`).join(', ');
            setError(`Validation errors: ${errorMessages}`);
          } else if (typeof data.detail === 'string') {
            setError(data.detail);
          } else {
            setError('Failed to create opportunity');
          }
        } else {
          setError('Failed to create opportunity');
        }
      }
    } catch (error) {
      console.error('Network or other error:', error); // Debug log
      setError('Error creating opportunity: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredOpportunities = opportunities.filter(opp =>
    opp.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    opp.client_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    opp.required_skills.some(skill => 
      skill.toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

  const getStatusColor = (status) => {
    switch (status) {
      case 'open': return 'bg-green-100 text-green-800';
      case 'in_progress': return 'bg-yellow-100 text-yellow-800';
      case 'filled': return 'bg-blue-100 text-blue-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      case 'on_hold': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getExperienceColor = (level) => {
    switch (level) {
      case 'junior': return 'bg-green-100 text-green-800';
      case 'mid': return 'bg-blue-100 text-blue-800';
      case 'senior': return 'bg-purple-100 text-purple-800';
      case 'architect': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleApplicationAction = async (applicationId, action) => {
    try {
      const response = await fetch(`http://localhost:8000/api/opportunity-applications/${applicationId}/${action}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        // Refresh opportunities to get updated application status
        await fetchOpportunities();
        // Show success message
        setError(`Application ${action}ed successfully`);
        // Clear success message after 3 seconds
        setTimeout(() => setError(''), 3000);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || `Failed to ${action} application`);
      }
    } catch (error) {
      setError(`Error ${action}ing application`);
    }
  };

  if (loading && opportunities.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading opportunities...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Opportunity Management</h1>
          <p className="text-gray-600 mt-1">AI-powered opportunity matching and management</p>
        </div>
        
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 mr-2" />
              Create Opportunity
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create New Opportunity</DialogTitle>
              <DialogDescription>
                Create a new opportunity with AI-powered analysis
              </DialogDescription>
            </DialogHeader>
            
            <form onSubmit={createOpportunity} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Title *</Label>
                  <Input
                    id="title"
                    value={newOpportunity.title}
                    onChange={(e) => setNewOpportunity({...newOpportunity, title: e.target.value})}
                    placeholder="Senior React Developer"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="client_name">Client Name *</Label>
                  <Input
                    id="client_name"
                    value={newOpportunity.client_name}
                    onChange={(e) => setNewOpportunity({...newOpportunity, client_name: e.target.value})}
                    placeholder="TechCorp Inc."
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description *</Label>
                <Textarea
                  id="description"
                  value={newOpportunity.description}
                  onChange={(e) => setNewOpportunity({...newOpportunity, description: e.target.value})}
                  placeholder="Detailed project description..."
                  rows={4}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="required_skills">Required Skills * (comma-separated)</Label>
                <Input
                  id="required_skills"
                  value={newOpportunity.required_skills}
                  onChange={(e) => setNewOpportunity({...newOpportunity, required_skills: e.target.value})}
                  placeholder="React, TypeScript, Node.js, AWS"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="experience_required">Experience Required (Years)</Label>
                  <Input
                    type="number"
                    min="0"
                    max="50"
                    value={newOpportunity.experience_required}
                    onChange={(e) => setNewOpportunity({...newOpportunity, experience_required: parseInt(e.target.value) || 0})}
                    placeholder="3"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="project_duration">Project Duration</Label>
                  <Input
                    id="project_duration"
                    value={newOpportunity.project_duration}
                    onChange={(e) => setNewOpportunity({...newOpportunity, project_duration: e.target.value})}
                    placeholder="3-6 months"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="start_date">Start Date</Label>
                  <Input
                    id="start_date"
                    type="date"
                    value={newOpportunity.start_date}
                    onChange={(e) => setNewOpportunity({...newOpportunity, start_date: e.target.value})}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="budget_range">Budget Range</Label>
                  <Input
                    id="budget_range"
                    value={newOpportunity.budget_range}
                    onChange={(e) => setNewOpportunity({...newOpportunity, budget_range: e.target.value})}
                    placeholder="$5000-10000"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-2 pt-4">
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setIsCreateDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={loading}>
                  {loading ? 'Creating...' : 'Create Opportunity'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Alerts */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}
      
      {success && (
        <Alert className="border-green-200 bg-green-50">
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      {/* Analytics Cards */}
      {analytics.current_metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Opportunities</p>
                  <p className="text-2xl font-bold text-gray-900">{analytics.current_metrics.total_opportunities}</p>
                </div>
                <Users className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Open Positions</p>
                  <p className="text-2xl font-bold text-green-600">{analytics.current_metrics.open_opportunities}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Fill Rate</p>
                  <p className="text-2xl font-bold text-purple-600">{analytics.current_metrics.fill_rate.toFixed(1)}%</p>
                </div>
                <DollarSign className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>

        </div>
      )}

      {/* Filters and Search */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search opportunities by title, client, or skills..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="open">Open</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="filled">Filled</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
                <SelectItem value="on_hold">On Hold</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Opportunities List */}
      <div className="grid gap-4">
        {filteredOpportunities.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <p className="text-gray-500">No opportunities found matching your criteria.</p>
            </CardContent>
          </Card>
        ) : (
          filteredOpportunities.map((opportunity) => (
            <Card key={opportunity.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{opportunity.title}</h3>
                      <Badge className={getStatusColor(opportunity.status)}>
                        {opportunity.status.replace('_', ' ')}
                      </Badge>
                      <Badge className={getExperienceColor(opportunity.experience_level)}>
                        {opportunity.experience_level}
                      </Badge>
                    </div>
                    
                    <p className="text-gray-600 mb-2">Client: {opportunity.client_name}</p>
                    <p className="text-gray-700 mb-3 line-clamp-2">{opportunity.description}</p>
                    
                    <div className="flex flex-wrap gap-2 mb-3">
                      {opportunity.required_skills.slice(0, 5).map((skill, index) => (
                        <Badge key={index} variant="outline">
                          {skill}
                        </Badge>
                      ))}
                      {opportunity.required_skills.length > 5 && (
                        <Badge variant="outline">
                          +{opportunity.required_skills.length - 5} more
                        </Badge>
                      )}
                    </div>
                  </div>
                  
                  <div className="text-right">
                    {opportunity.project_duration && (
                      <div className="flex items-center gap-1 text-sm text-gray-600">
                        <Clock className="w-4 h-4" />
                        {opportunity.project_duration}
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex justify-between items-center text-sm text-gray-500">
                  <span>Created: {new Date(opportunity.created_at).toLocaleDateString()}</span>
                  
                  <div className="flex gap-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => {
                        setSelectedOpportunity(opportunity);
                        setActiveTab('details');
                      }}
                    >
                      View Details
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => {
                        console.log('View Applications clicked for opportunity:', opportunity.id);
                        setSelectedOpportunity(opportunity);
                        setActiveTab('applications');
                      }}
                    >
                      View Applications
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Opportunity Details Dialog */}
      {selectedOpportunity && (
        <Dialog open={!!selectedOpportunity} onOpenChange={() => setSelectedOpportunity(null)}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                {selectedOpportunity.title}
                <Badge className={getStatusColor(selectedOpportunity.status)}>
                  {selectedOpportunity.status.replace('_', ' ')}
                </Badge>
              </DialogTitle>
              <DialogDescription>
                {selectedOpportunity.client_name} • Created {new Date(selectedOpportunity.created_at).toLocaleDateString()}
              </DialogDescription>
            </DialogHeader>

            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="details">Details</TabsTrigger>
                <TabsTrigger value="ai-analysis">AI Analysis</TabsTrigger>
                <TabsTrigger value="applications">Applications</TabsTrigger>
              </TabsList>

              <TabsContent value="details" className="space-y-4">
                <div>
                  <h4 className="font-semibold mb-2">Description</h4>
                  <p className="text-gray-700">{selectedOpportunity.description}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold mb-2">Project Details</h4>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">Duration:</span> {selectedOpportunity.project_duration || 'Not specified'}</p>
                      <p><span className="font-medium">Budget:</span> {selectedOpportunity.budget_range || 'Not specified'}</p>
                      <p><span className="font-medium">Experience Level:</span> {selectedOpportunity.experience_level}</p>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold mb-2">Timeline</h4>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">Start Date:</span> {selectedOpportunity.start_date ? new Date(selectedOpportunity.start_date).toLocaleDateString() : 'Not specified'}</p>
                      <p><span className="font-medium">End Date:</span> {selectedOpportunity.end_date ? new Date(selectedOpportunity.end_date).toLocaleDateString() : 'Not specified'}</p>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-2">Required Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedOpportunity.required_skills.map((skill, index) => (
                      <Badge key={index} variant="outline">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="ai-analysis" className="space-y-4">
                <div>
                  <h4 className="font-semibold mb-2 flex items-center gap-2">
                    <Brain className="w-5 h-5 text-blue-600" />
                    AI Analysis Results
                  </h4>
                  
                  {selectedOpportunity.applications && selectedOpportunity.applications.length > 0 ? (
                    <div className="space-y-4">
                      <h5 className="font-medium text-gray-700">Skills Match Analysis:</h5>
                      {selectedOpportunity.applications.map((application) => {
                        // Calculate skills match percentage
                        const requiredSkills = selectedOpportunity.required_skills || [];
                        const consultantSkills = application.consultant_skills || [];
                        
                        const matchedSkills = requiredSkills.filter(skill => 
                          consultantSkills.some(cSkill => 
                            cSkill.toLowerCase().includes(skill.toLowerCase()) || 
                            skill.toLowerCase().includes(cSkill.toLowerCase())
                          )
                        );
                        
                        const matchPercentage = requiredSkills.length > 0 
                          ? Math.round((matchedSkills.length / requiredSkills.length) * 100) 
                          : 0;
                        
                        return (
                          <div key={application.id} className="bg-blue-50 p-4 rounded-lg border">
                            <div className="flex items-center justify-between mb-2">
                              <h6 className="font-medium text-blue-900">{application.consultant_name}</h6>
                              <div className="flex items-center gap-2">
                                <Badge 
                                  variant={matchPercentage >= 70 ? "default" : matchPercentage >= 40 ? "secondary" : "destructive"}
                                >
                                  {matchPercentage}% Match
                                </Badge>
                              </div>
                            </div>
                            <p className="text-sm text-blue-700">
                              Matched {matchedSkills.length} out of {requiredSkills.length} required skills
                            </p>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <p className="text-blue-700">No applications to analyze yet.</p>
                    </div>
                  )}
                  
                  {selectedOpportunity.ai_recommendations && (
                    <div className="bg-blue-50 p-4 rounded-lg mt-4">
                      <h5 className="font-medium text-blue-800 mb-1">AI Recommendations:</h5>
                      <p className="text-blue-700">{selectedOpportunity.ai_recommendations}</p>
                    </div>
                  )}
                </div>
              </TabsContent>

              <TabsContent value="applications">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="font-semibold">Applications ({selectedOpportunity.applications?.length || 0})</h4>
                    <Badge variant="secondary">
                      {selectedOpportunity.accepted_count || 0} Accepted
                    </Badge>
                  </div>
                  
                  {selectedOpportunity.applications && selectedOpportunity.applications.length > 0 ? (
                    <div className="space-y-4">
                      {selectedOpportunity.applications.map((application) => (
                        <Card key={application.id} className="border-l-4 border-l-blue-500">
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <h5 className="font-medium">{application.consultant_name}</h5>
                                  <Badge 
                                    variant={
                                      application.status === 'accepted' ? 'default' :
                                      application.status === 'rejected' ? 'destructive' : 
                                      'secondary'
                                    }
                                  >
                                    {application.status}
                                  </Badge>
                                </div>
                                
                                <p className="text-sm text-gray-600 mb-2">{application.consultant_email}</p>
                                <p className="text-sm mb-2">
                                  <strong>Experience:</strong> {application.experience_years} years
                                </p>
                                <p className="text-sm mb-2">
                                  <strong>Skills:</strong> {application.consultant_skills.join(', ')}
                                </p>
                                {application.proposed_rate && (
                                  <p className="text-sm mb-2">
                                    <strong>Proposed Rate:</strong> {application.proposed_rate}
                                  </p>
                                )}
                                <p className="text-sm mb-2">
                                  <strong>Applied:</strong> {new Date(application.applied_at).toLocaleDateString()}
                                </p>
                                
                                {application.cover_letter && (
                                  <div className="mt-3 p-3 bg-gray-50 rounded">
                                    <p className="text-sm"><strong>Cover Letter:</strong></p>
                                    <p className="text-sm text-gray-700 mt-1">{application.cover_letter}</p>
                                  </div>
                                )}
                              </div>
                              
                              {application.status === 'pending' && (
                                <div className="flex gap-2 ml-4">
                                  <Button 
                                    size="sm" 
                                    onClick={() => handleApplicationAction(application.id, 'accept')}
                                    className="bg-green-600 hover:bg-green-700"
                                  >
                                    Accept
                                  </Button>
                                  <Button 
                                    size="sm" 
                                    variant="outline"
                                    onClick={() => handleApplicationAction(application.id, 'reject')}
                                  >
                                    Reject
                                  </Button>
                                </div>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-gray-500">No applications received yet</p>
                    </div>
                  )}
                </div>
              </TabsContent>
            </Tabs>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

export default AdminOpportunities;
