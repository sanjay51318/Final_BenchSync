import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Star, Clock, DollarSign, Brain, FileText, TrendingUp, CheckCircle, XCircle, Briefcase } from 'lucide-react';

interface Opportunity {
  id: number;
  title: string;
  description: string;
  client_name: string;
  required_skills?: string[];
  experience_level: string;
  project_duration?: string;
  budget_range?: string;
  status: string;
}

interface MatchedOpportunity {
  opportunity: Opportunity;
  match_score: number;
  match_reasoning: string;
  strengths: string[];
  potential_gaps: string[];
}

interface Application {
  application_id: number;
  opportunity: Opportunity;
  application_status: string;
  match_score: number;
  applied_at: string;
}

interface ConsultantOpportunityData {
  recommended_opportunities: MatchedOpportunity[];
  applied_opportunities: Application[];
  total_recommended: number;
  total_applied: number;
}

const ConsultantOpportunityDashboard = ({ consultantEmail }: { consultantEmail: string }) => {
  const [opportunityData, setOpportunityData] = useState<ConsultantOpportunityData>({
    recommended_opportunities: [],
    applied_opportunities: [],
    total_recommended: 0,
    total_applied: 0
  });
  const [loading, setLoading] = useState(true);
  const [selectedOpportunity, setSelectedOpportunity] = useState<MatchedOpportunity | null>(null);
  const [isApplyDialogOpen, setIsApplyDialogOpen] = useState(false);
  const [applicationData, setApplicationData] = useState({
    cover_letter: '',
    proposed_rate: '',
    availability_start: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (consultantEmail) {
      fetchConsultantOpportunities();
    }
  }, [consultantEmail]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchConsultantOpportunities = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/consultant-opportunities/${consultantEmail}`);
      const data = await response.json();
      
      if (response.ok) {
        console.log('Received opportunity data:', data);
        // Ensure required_skills is always an array
        if (data.recommended_opportunities) {
          data.recommended_opportunities = data.recommended_opportunities.map((match: MatchedOpportunity) => ({
            ...match,
            opportunity: {
              ...match.opportunity,
              required_skills: Array.isArray(match.opportunity.required_skills) ? match.opportunity.required_skills : []
            }
          }));
        }
        if (data.applied_opportunities) {
          data.applied_opportunities = data.applied_opportunities.map((app: Application) => ({
            ...app,
            opportunity: {
              ...app.opportunity,
              required_skills: Array.isArray(app.opportunity.required_skills) ? app.opportunity.required_skills : []
            }
          }));
        }
        setOpportunityData(data);
      } else {
        setError(data.detail || 'Failed to fetch opportunities');
      }
    } catch (error) {
      setError('Error connecting to backend');
    } finally {
      setLoading(false);
    }
  };

  const applyToOpportunity = async (opportunityId: number) => {
    try {
      setLoading(true);
      
      const response = await fetch(`http://localhost:8000/api/opportunities/${opportunityId}/apply`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          consultant_email: consultantEmail,
          ...applicationData
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(`Application submitted successfully! Match Score: ${data.match_score?.toFixed(1) || 'N/A'}`);
        setIsApplyDialogOpen(false);
        setApplicationData({
          cover_letter: '',
          proposed_rate: '',
          availability_start: ''
        });
        fetchConsultantOpportunities(); // Refresh data
      } else {
        setError(data.detail || 'Failed to submit application');
      }
    } catch (error) {
      setError('Error submitting application');
    } finally {
      setLoading(false);
    }
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-100';
    if (score >= 0.6) return 'text-blue-600 bg-blue-100';
    if (score >= 0.4) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getApplicationStatusColor = (status: string) => {
    switch (status) {
      case 'applied': return 'bg-blue-100 text-blue-800';
      case 'under_review': return 'bg-yellow-100 text-yellow-800';
      case 'accepted': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getExperienceColor = (level: string) => {
    switch (level) {
      case 'junior': return 'bg-green-100 text-green-800';
      case 'mid': return 'bg-blue-100 text-blue-800';
      case 'senior': return 'bg-purple-100 text-purple-800';
      case 'architect': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading && opportunityData.recommended_opportunities.length === 0) {
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
          <h1 className="text-3xl font-bold text-gray-900">My Opportunities</h1>
          <p className="text-gray-600 mt-1">AI-powered opportunity matching based on your profile</p>
        </div>
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

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Recommended Matches</p>
                <p className="text-2xl font-bold text-blue-600">{opportunityData.total_recommended}</p>
              </div>
              <Star className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Applications Submitted</p>
                <p className="text-2xl font-bold text-green-600">{opportunityData.total_applied}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Success Rate</p>
                <p className="text-2xl font-bold text-purple-600">
                  {opportunityData.total_applied > 0 
                    ? (opportunityData.applied_opportunities.filter(app => app.application_status === 'accepted').length / opportunityData.total_applied * 100).toFixed(1)
                    : 0}%
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Opportunities Tabs */}
      <Tabs defaultValue="recommended" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="recommended">
            Recommended for You ({opportunityData.total_recommended})
          </TabsTrigger>
          <TabsTrigger value="applied">
            My Applications ({opportunityData.total_applied})
          </TabsTrigger>
        </TabsList>

        {/* Recommended Opportunities */}
        <TabsContent value="recommended" className="space-y-4">
          {opportunityData.recommended_opportunities.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center">
                <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No recommended opportunities at the moment.</p>
                <p className="text-sm text-gray-400 mt-1">Keep your profile updated to get better matches!</p>
              </CardContent>
            </Card>
          ) : (
            opportunityData.recommended_opportunities.map((match, index) => (
              <Card key={match.opportunity.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{match.opportunity.title}</h3>
                        <Badge className={getExperienceColor(match.opportunity.experience_level)}>
                          {match.opportunity.experience_level}
                        </Badge>
                        <Badge className={`${getMatchScoreColor(match.match_score)} px-2 py-1 rounded-full text-xs font-medium`}>
                          <Brain className="w-3 h-3 mr-1" />
                          {(match.match_score * 100).toFixed(0)}% Match
                        </Badge>
                      </div>
                      
                      <p className="text-gray-600 mb-2">Client: {match.opportunity.client_name}</p>
                      <p className="text-gray-700 mb-3 line-clamp-2">{match.opportunity.description}</p>
                      
                      <div className="flex flex-wrap gap-2 mb-3">
                        {(match.opportunity.required_skills || []).slice(0, 4).map((skill, skillIndex) => (
                          <Badge key={skillIndex} variant="outline" className={
                            match.strengths?.includes(skill) ? 'border-green-300 bg-green-50 text-green-700' : ''
                          }>
                            {skill}
                            {match.strengths?.includes(skill) && <CheckCircle className="w-3 h-3 ml-1" />}
                          </Badge>
                        ))}
                        {(match.opportunity.required_skills || []).length > 4 && (
                          <Badge variant="outline">
                            +{(match.opportunity.required_skills || []).length - 4} more
                          </Badge>
                        )}
                      </div>

                      {/* AI Insights */}
                      <div className="bg-blue-50 p-3 rounded-lg mb-3">
                        <h4 className="text-sm font-medium text-blue-900 mb-1">AI Match Analysis:</h4>
                        <p className="text-sm text-blue-800">{match.match_reasoning}</p>
                        
                        {match.strengths && match.strengths.length > 0 && (
                          <div className="mt-2">
                            <span className="text-xs font-medium text-green-700">Your Strengths: </span>
                            <span className="text-xs text-green-600">{match.strengths.join(', ')}</span>
                          </div>
                        )}
                        
                        {match.potential_gaps && match.potential_gaps.length > 0 && (
                          <div className="mt-1">
                            <span className="text-xs font-medium text-orange-700">Growth Areas: </span>
                            <span className="text-xs text-orange-600">{match.potential_gaps.join(', ')}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="text-right flex flex-col gap-2">
                      {match.opportunity.project_duration && (
                        <div className="flex items-center gap-1 text-sm text-gray-600">
                          <Clock className="w-4 h-4" />
                          {match.opportunity.project_duration}
                        </div>
                      )}
                      
                      {match.opportunity.budget_range && (
                        <div className="flex items-center gap-1 text-sm text-gray-600">
                          <DollarSign className="w-4 h-4" />
                          {match.opportunity.budget_range}
                        </div>
                      )}
                      
                      <div className="flex gap-2 mt-2">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => setSelectedOpportunity(match)}
                        >
                          View Details
                        </Button>
                        <Button 
                          size="sm"
                          onClick={() => {
                            setSelectedOpportunity(match);
                            setIsApplyDialogOpen(true);
                          }}
                          className="bg-blue-600 hover:bg-blue-700"
                        >
                          Apply Now
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>

        {/* Applied Opportunities */}
        <TabsContent value="applied" className="space-y-4">
          {opportunityData.applied_opportunities.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No applications submitted yet.</p>
                <p className="text-sm text-gray-400 mt-1">Check out the recommended opportunities tab to get started!</p>
              </CardContent>
            </Card>
          ) : (
            opportunityData.applied_opportunities.map((application) => (
              <Card key={application.application_id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{application.opportunity.title}</h3>
                        <Badge className={getApplicationStatusColor(application.application_status)}>
                          {application.application_status.replace('_', ' ')}
                        </Badge>
                        {application.match_score && (
                          <Badge className={`${getMatchScoreColor(application.match_score)} px-2 py-1 rounded-full text-xs font-medium`}>
                            <Brain className="w-3 h-3 mr-1" />
                            {(application.match_score * 100).toFixed(0)}% Match
                          </Badge>
                        )}
                      </div>
                      
                      <p className="text-gray-600 mb-2">Client: {application.opportunity.client_name}</p>
                      <p className="text-gray-700 mb-3 line-clamp-2">{application.opportunity.description}</p>
                      
                      <div className="flex flex-wrap gap-2 mb-3">
                        {(application.opportunity.required_skills || []).slice(0, 5).map((skill, index) => (
                          <Badge key={index} variant="outline">
                            {skill}
                          </Badge>
                        ))}
                        {(application.opportunity.required_skills || []).length > 5 && (
                          <Badge variant="outline">
                            +{(application.opportunity.required_skills || []).length - 5} more
                          </Badge>
                        )}
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <p className="text-sm text-gray-500 mb-2">
                        Applied: {new Date(application.applied_at).toLocaleDateString()}
                      </p>
                      
                      <div className="flex items-center gap-1">
                        {application.application_status === 'accepted' && <CheckCircle className="w-4 h-4 text-green-600" />}
                        {application.application_status === 'rejected' && <XCircle className="w-4 h-4 text-red-600" />}
                        <span className={`text-sm font-medium ${
                          application.application_status === 'accepted' ? 'text-green-600' :
                          application.application_status === 'rejected' ? 'text-red-600' :
                          'text-blue-600'
                        }`}>
                          {application.application_status === 'applied' ? 'Under Review' :
                           application.application_status === 'under_review' ? 'Being Reviewed' :
                           application.application_status === 'accepted' ? 'Accepted!' :
                           application.application_status === 'rejected' ? 'Not Selected' :
                           application.application_status}
                        </span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>
      </Tabs>

      {/* Opportunity Details Dialog */}
      {selectedOpportunity && (
        <Dialog open={!!selectedOpportunity} onOpenChange={() => setSelectedOpportunity(null)}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                {selectedOpportunity.opportunity.title}
                <Badge className={getExperienceColor(selectedOpportunity.opportunity.experience_level)}>
                  {selectedOpportunity.opportunity.experience_level}
                </Badge>
                <Badge className={`${getMatchScoreColor(selectedOpportunity.match_score)} px-2 py-1 rounded-full text-xs font-medium`}>
                  <Brain className="w-3 h-3 mr-1" />
                  {(selectedOpportunity.match_score * 100).toFixed(0)}% Match
                </Badge>
              </DialogTitle>
              <DialogDescription>
                {selectedOpportunity.opportunity.client_name}
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-6">
              <div>
                <h4 className="font-semibold mb-2">Project Description</h4>
                <p className="text-gray-700">{selectedOpportunity.opportunity.description}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold mb-2">Project Details</h4>
                  <div className="space-y-2 text-sm">
                    <p><span className="font-medium">Duration:</span> {selectedOpportunity.opportunity.project_duration || 'Not specified'}</p>
                    <p><span className="font-medium">Budget:</span> {selectedOpportunity.opportunity.budget_range || 'Not specified'}</p>
                    <p><span className="font-medium">Experience Level:</span> {selectedOpportunity.opportunity.experience_level}</p>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-2">Match Analysis</h4>
                  <div className="space-y-2 text-sm">
                    <p><span className="font-medium">Overall Match:</span> {(selectedOpportunity.match_score * 100).toFixed(0)}%</p>
                    <p className="text-blue-700">{selectedOpportunity.match_reasoning}</p>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Required Skills</h4>
                <div className="flex flex-wrap gap-2">
                  {(selectedOpportunity.opportunity.required_skills || []).map((skill, index) => (
                    <Badge 
                      key={index} 
                      variant="outline"
                      className={selectedOpportunity.strengths?.includes(skill) ? 'border-green-300 bg-green-50 text-green-700' : ''}
                    >
                      {skill}
                      {selectedOpportunity.strengths?.includes(skill) && <CheckCircle className="w-3 h-3 ml-1" />}
                    </Badge>
                  ))}
                </div>
              </div>

              {selectedOpportunity.strengths && selectedOpportunity.strengths.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2 text-green-700">Your Strengths for This Role</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedOpportunity.strengths.map((strength, index) => (
                      <Badge key={index} className="bg-green-100 text-green-800">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        {strength}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {selectedOpportunity.potential_gaps && selectedOpportunity.potential_gaps.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2 text-orange-700">Areas for Growth</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedOpportunity.potential_gaps.map((gap, index) => (
                      <Badge key={index} className="bg-orange-100 text-orange-800">
                        {gap}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex justify-end space-x-2 pt-4">
                <Button 
                  variant="outline" 
                  onClick={() => setSelectedOpportunity(null)}
                >
                  Close
                </Button>
                <Button 
                  onClick={() => setIsApplyDialogOpen(true)}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  Apply for This Position
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* Apply Dialog */}
      {isApplyDialogOpen && selectedOpportunity && (
        <Dialog open={isApplyDialogOpen} onOpenChange={setIsApplyDialogOpen}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Apply for {selectedOpportunity.opportunity.title}</DialogTitle>
              <DialogDescription>
                Submit your application for this opportunity
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="cover_letter">Cover Letter</Label>
                <Textarea
                  id="cover_letter"
                  value={applicationData.cover_letter}
                  onChange={(e) => setApplicationData({...applicationData, cover_letter: e.target.value})}
                  placeholder="Tell the client why you're the perfect fit for this project..."
                  rows={6}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="proposed_rate">Proposed Rate</Label>
                  <Input
                    id="proposed_rate"
                    value={applicationData.proposed_rate}
                    onChange={(e) => setApplicationData({...applicationData, proposed_rate: e.target.value})}
                    placeholder="$75/hour or $5000 fixed"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="availability_start">Available From</Label>
                  <Input
                    id="availability_start"
                    type="date"
                    value={applicationData.availability_start}
                    onChange={(e) => setApplicationData({...applicationData, availability_start: e.target.value})}
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-2 pt-4">
                <Button 
                  variant="outline" 
                  onClick={() => setIsApplyDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button 
                  onClick={() => applyToOpportunity(selectedOpportunity.opportunity.id)}
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {loading ? 'Submitting...' : 'Submit Application'}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

export default ConsultantOpportunityDashboard;
