import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { StatusCard } from '@/components/Dashboard/StatusCard';
import { WorkflowProgressBar } from '@/components/Dashboard/WorkflowProgressBar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import ConsultantOpportunityDashboard from "@/components/ConsultantOpportunityDashboard";
import { 
  FileText, 
  Calendar, 
  Briefcase, 
  GraduationCap,
  TrendingUp,
  Brain,
  Zap,
  Star,
  Target,
  RefreshCw,
  Upload
} from 'lucide-react';

// API configuration
const API_BASE_URL = 'http://localhost:8000';

// Types
interface SkillsAnalysisData {
  ai_summary: string;
  skills: string[];
  competencies: string[];
  ai_feedback: string;
  ai_suggestions: string;
  confidence_score: number;
}

interface Consultant {
  id: number;
  email: string;
  name: string;
}

// Skills Analysis Component
function SkillsAnalysisCard({ userEmail }: { userEmail: string }) {
  const [skillsData, setSkillsData] = useState<SkillsAnalysisData | null>(null);
  const [loadingSkills, setLoadingSkills] = useState(false);
  const [uploadingResume, setUploadingResume] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const fetchSkillsAnalysis = useCallback(async () => {
    if (!userEmail) return;
    
    try {
      setLoadingSkills(true);
      // Find consultant ID first
      const consultantsResponse = await fetch(`${API_BASE_URL}/api/consultants`);
      if (!consultantsResponse.ok) return;
      
      const consultants: Consultant[] = await consultantsResponse.json();
      const consultant = consultants.find((c: Consultant) => c.email === userEmail);
      
      if (consultant) {
        const analysisResponse = await fetch(`${API_BASE_URL}/api/consultant/${consultant.id}/resume-analysis`);
        if (analysisResponse.ok) {
          const analysis: SkillsAnalysisData = await analysisResponse.json();
          setSkillsData(analysis);
        }
      }
    } catch (error) {
      console.error('Error fetching skills analysis:', error);
    } finally {
      setLoadingSkills(false);
    }
  }, [userEmail]);

  const handleResumeUpload = async () => {
    if (!selectedFile) {
      setUploadMessage('Please select a file to upload');
      return;
    }

    if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setUploadMessage('Please upload a PDF file only.');
      return;
    }

    try {
      setUploadingResume(true);
      setUploadMessage('');

      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('consultant_email', userEmail);

      const response = await fetch(`${API_BASE_URL}/upload-resume`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setUploadMessage(`✅ Resume uploaded successfully! Analysis complete.`);
        setSelectedFile(null);
        // Refresh skills analysis
        await fetchSkillsAnalysis();
      } else {
        setUploadMessage(`❌ Upload failed: ${result.detail}`);
      }
    } catch (error) {
      setUploadMessage('❌ Upload failed. Please try again.');
      console.error('Resume upload error:', error);
    } finally {
      setUploadingResume(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setUploadMessage('');
    }
  };

  useEffect(() => {
    fetchSkillsAnalysis();
  }, [fetchSkillsAnalysis]);

  if (loadingSkills) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            AI Skills Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">Loading skills analysis...</p>
        </CardContent>
      </Card>
    );
  }

  if (!skillsData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            AI Skills Analysis
          </CardTitle>
          <CardDescription>
            Upload your resume to see AI-powered skills analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">No resume analysis available. Upload your resume to get started!</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Brain className="h-5 w-5 text-primary" />
          AI Skills Analysis
        </CardTitle>
        <CardDescription>
          Based on your latest resume analysis
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* AI Summary */}
        <div className="space-y-2">
          <h4 className="font-medium flex items-center gap-2">
            <Zap className="h-4 w-4" />
            AI Summary
          </h4>
          <p className="text-sm text-muted-foreground">{skillsData.ai_summary}</p>
        </div>

        {/* Extracted Skills */}
        <div className="space-y-2">
          <h4 className="font-medium">Technical Skills ({skillsData.skills?.length || 0})</h4>
          <div className="flex flex-wrap gap-2">
            {(skillsData.skills || []).slice(0, 10).map((skill: string, index: number) => (
              <Badge key={index} variant="secondary" className="text-xs">
                {skill}
              </Badge>
            ))}
            {(skillsData.skills || []).length > 10 && (
              <Badge variant="outline" className="text-xs">
                +{(skillsData.skills || []).length - 10} more
              </Badge>
            )}
          </div>
        </div>

        {/* Competencies */}
        {skillsData.competencies && skillsData.competencies.length > 0 && (
          <div className="space-y-2">
            <h4 className="font-medium">Soft Skills</h4>
            <div className="flex flex-wrap gap-2">
              {skillsData.competencies.map((comp: string, index: number) => (
                <Badge key={index} variant="outline" className="text-xs bg-blue-50 text-blue-700">
                  {comp}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* AI Feedback */}
        <div className="space-y-2">
          <h4 className="font-medium">AI Feedback</h4>
          <p className="text-sm text-muted-foreground">{skillsData.ai_feedback}</p>
        </div>

        {/* AI Suggestions */}
        <div className="space-y-2">
          <h4 className="font-medium">Skill Development Recommendations</h4>
          <p className="text-sm text-muted-foreground">{skillsData.ai_suggestions}</p>
        </div>

        <div className="text-xs text-muted-foreground pt-2 border-t">
          Analysis confidence: {Math.round((skillsData.confidence_score || 0) * 100)}%
        </div>
      </CardContent>
    </Card>
  );
}

// Interfaces for API data
interface ConsultantData {
  resumeStatus: string;
  attendanceReport: {
    completed: number;
    missed: number;
    total: number;
  };
  opportunities: number;
  trainingProgress: string;
  workflowSteps: WorkflowStep[];
  recentOpportunities: Opportunity[];
  trainingModules: TrainingModule[];
}

interface WorkflowStep {
  id: string;
  label: string;
  completed: boolean;
  inProgress: boolean;
}

interface Opportunity {
  id: number;
  title: string;
  company: string;
  date: string;
  status: string;
}

interface TrainingModule {
  id: number;
  name: string;
  progress: number;
  status: string;
}

export default function ConsultantDashboard() {
  const { user } = useAuth();
  const [consultantData, setConsultantData] = useState<ConsultantData | null>(null);
  const [loading, setLoading] = useState(true);

  // Fetch consultant-specific data
  const fetchConsultantData = useCallback(async () => {
    if (!user?.email) return;
    
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/consultant/dashboard/${encodeURIComponent(user.email)}`);
      
      if (response.ok) {
        const data = await response.json();
        
        // Transform API data to component format
        const transformedData: ConsultantData = {
          resumeStatus: data.resume_status || 'not updated',
          attendanceReport: {
            completed: Math.floor(data.attendance_rate || 0),
            missed: Math.max(0, 100 - Math.floor(data.attendance_rate || 0)),
            total: 100
          },
          opportunities: data.opportunities_count || 0,
          trainingProgress: data.training_progress || 'not-started',
          workflowSteps: data.workflow_steps || [
            { id: 'resume', label: 'Resume Updated', completed: data.resume_status === 'updated', inProgress: false },
            { id: 'attendance', label: 'Attendance Reported', completed: data.attendance_rate > 80, inProgress: false },
            { id: 'opportunities', label: 'Opportunities Documented', completed: data.opportunities_count > 0, inProgress: false },
            { id: 'training', label: 'Training Completed', completed: data.training_progress === 'completed', inProgress: data.training_progress === 'in-progress' }
          ],
          recentOpportunities: [], // Will be populated separately if needed
          trainingModules: [
            { id: 1, name: 'Advanced React Patterns', progress: 85, status: 'in-progress' },
            { id: 2, name: 'System Design Fundamentals', progress: 100, status: 'completed' },
            { id: 3, name: 'Cloud Architecture AWS', progress: 30, status: 'in-progress' }
          ]
        };
        
        setConsultantData(transformedData);
      }
    } catch (error) {
      console.error('Error fetching consultant data:', error);
    } finally {
      setLoading(false);
    }
  }, [user?.email]);

  useEffect(() => {
    fetchConsultantData();
  }, [fetchConsultantData]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-8">
          <p className="text-muted-foreground">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (!consultantData) {
    return (
      <div className="space-y-6">
        <div className="text-center py-8">
          <p className="text-muted-foreground">Unable to load dashboard data.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">
          Welcome back, {user?.name}
        </h1>
        <p className="text-muted-foreground mt-2">
          Track your bench period progress and opportunities
        </p>
      </div>

      {/* Workflow Progress */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary" aria-hidden="true" />
            Workflow Progress
          </CardTitle>
          <CardDescription>
            Complete all steps to optimize your bench period
          </CardDescription>
        </CardHeader>
        <CardContent>
          <WorkflowProgressBar steps={consultantData.workflowSteps} />
        </CardContent>
      </Card>

      {/* Status Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatusCard
          title="Resume Status"
          value={consultantData.resumeStatus === 'updated' ? 'Updated' : 'Not Updated'}
          status={consultantData.resumeStatus === 'updated' ? 'completed' : 'pending'}
          description="Resume status from database"
          icon={<FileText className="h-4 w-4" />}
        />

        
        
        <StatusCard
          title="Attendance Rate"
          value={`${Math.round((consultantData.attendanceReport.completed / consultantData.attendanceReport.total) * 100)}%`}
          status="completed"
          description={`${consultantData.attendanceReport.completed}/${consultantData.attendanceReport.total} sessions`}
          icon={<Calendar className="h-4 w-4" />}
        />
        
        <StatusCard
          title="Opportunities"
          value={consultantData.opportunities}
          status="completed"
          description="Applications submitted"
          icon={<Briefcase className="h-4 w-4" />}
        />
        
        <StatusCard
          title="Training Progress"
          value="67%"
          status={consultantData.trainingProgress as 'completed' | 'in-progress' | 'pending'}
          description="2 of 3 modules completed"
          icon={<GraduationCap className="h-4 w-4" />}
        />
      </div>

      {/* AI Skills Analysis Section */}
      <SkillsAnalysisCard userEmail={user?.email || ''} />

      {/* Detailed Information Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Opportunities */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Briefcase className="h-5 w-5 text-primary" aria-hidden="true" />
              Recent Opportunities
            </CardTitle>
            <CardDescription>
              Your latest job applications and their status
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {consultantData.recentOpportunities.length > 0 ? (
                consultantData.recentOpportunities.map((opportunity) => (
                  <div key={opportunity.id} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                    <div className="flex-1">
                      <h4 className="font-medium text-foreground">{opportunity.title}</h4>
                      <p className="text-sm text-muted-foreground">{opportunity.company}</p>
                      <p className="text-xs text-muted-foreground mt-1">{opportunity.date}</p>
                    </div>
                    <Badge variant="outline" className="ml-4">
                      {opportunity.status}
                    </Badge>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No recent opportunities found. Check the Opportunities tab for available projects.</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Training Progress */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <GraduationCap className="h-5 w-5 text-primary" aria-hidden="true" />
              Training Modules
            </CardTitle>
            <CardDescription>
              Your current learning progress
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {consultantData.trainingModules.map((module) => (
                <div key={module.id} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-foreground">{module.name}</h4>
                    <Badge 
                      className={module.status === 'completed' ? 'bg-status-completed text-white' : 'bg-status-in-progress text-white'}
                    >
                      {module.progress}%
                    </Badge>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${
                        module.status === 'completed' ? 'bg-status-completed' : 'bg-status-in-progress'
                      }`}
                      style={{ width: `${module.progress}%` }}
                      role="progressbar"
                      aria-valuenow={module.progress}
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-label={`${module.name} progress: ${module.progress}%`}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Attendance Details */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-primary" aria-hidden="true" />
            Attendance Report
          </CardTitle>
          <CardDescription>
            Detailed breakdown of your session attendance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-success/10 rounded-lg">
              <div className="text-2xl font-bold text-status-completed">
                {consultantData.attendanceReport.completed}
              </div>
              <div className="text-sm text-muted-foreground">Completed Sessions</div>
            </div>
            <div className="text-center p-4 bg-destructive/10 rounded-lg">
              <div className="text-2xl font-bold text-status-missed">
                {consultantData.attendanceReport.missed}
              </div>
              <div className="text-sm text-muted-foreground">Missed Sessions</div>
            </div>
            <div className="text-center p-4 bg-primary/10 rounded-lg">
              <div className="text-2xl font-bold text-primary">
                {Math.round((consultantData.attendanceReport.completed / consultantData.attendanceReport.total) * 100)}%
              </div>
              <div className="text-sm text-muted-foreground">Attendance Rate</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}