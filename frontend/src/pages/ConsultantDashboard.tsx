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
  Target
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
interface AttendanceData {
  user_name: string;
  user_email: string;
  attendance_rate: number;
  total_days: number;
  present_days: number;
  absent_days: number;
  leave_days: number;
  period_days: number;
}

interface ConsultantData {
  resumeStatus: string;
  attendanceReport: {
    completed: number;
    missed: number;
    total: number;
    rate: number;
    details?: AttendanceData;
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
  name?: string;
  program_name?: string;
  progress?: number;
  progress_percentage?: number;
  status: string;
  description?: string;
  category?: string;
  enrollment_date?: string;
  estimated_completion?: string;
}

interface TrainingRecommendation {
  name: string;
  priority: string;
  reason: string;
  missing_skill?: string;
  opportunities_count?: number;
  sample_opportunities?: string[];
  duration_hours?: number;
  provider?: string;
  cost?: number;
  difficulty?: string;
  rating?: number;
  certification_available?: boolean;
  url?: string;
  recommendation_score?: number;
  ai_generated?: boolean;
}

interface SkillGap {
  skill: string;
  opportunities: string[];
  priority: string;
}

interface TrainingCourse {
  name: string;
  category: string;
  duration: string;
  rating: number;
}

interface TrainingDashboardData {
  current_enrollments: TrainingModule[];
  opportunity_based_recommendations?: {
    missing_skills: SkillGap[];
    training_courses: TrainingRecommendation[];
    total_missing: number;
  };
  dashboard_metrics?: {
    skills_to_develop: number;
    active_trainings: number;
    missed_opportunities: number;
  };
  recommendations?: TrainingRecommendation[];
  skill_gaps?: SkillGap[];
  catalog?: TrainingCourse[];
}

export default function ConsultantDashboard() {
  const { user } = useAuth();
  const [consultantData, setConsultantData] = useState<ConsultantData | null>(null);
  const [trainingData, setTrainingData] = useState<TrainingDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploadingResume, setUploadingResume] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const [enrollmentLoading, setEnrollmentLoading] = useState(false);
  const [refreshingTraining, setRefreshingTraining] = useState(false);

  // Resume upload handler
  const handleResumeUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Allow both PDF and TXT files for testing
    const allowedExtensions = ['.pdf', '.txt'];
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
    if (!allowedExtensions.includes(fileExtension)) {
      setUploadMessage('Please upload a PDF or TXT file only.');
      return;
    }

    setUploadingResume(true);
    setUploadMessage('');

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('consultant_email', user?.email || '');

      const response = await fetch(`${API_BASE_URL}/upload-resume`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        setUploadMessage(`✅ Resume uploaded successfully! Analyzed ${result.analysis.skills.length} skills.`);
        // Refresh consultant data to show updated resume status
        await fetchConsultantData();
      } else {
        setUploadMessage(`❌ Upload failed: ${result.detail}`);
      }
    } catch (error) {
      setUploadMessage('❌ Upload failed. Please try again.');
      console.error('Resume upload error:', error);
    } finally {
      setUploadingResume(false);
      // Clear the file input
      event.target.value = '';
    }
  };

  // Fetch training dashboard data
  const fetchTrainingData = useCallback(async () => {
    if (!user?.email) return;
    
    try {
      setRefreshingTraining(true);
      
      // Find consultant ID first
      const consultantsResponse = await fetch(`${API_BASE_URL}/api/consultants`);
      if (!consultantsResponse.ok) return;
      
      const consultants: Consultant[] = await consultantsResponse.json();
      const consultant = consultants.find((c: Consultant) => c.email === user.email);
      
      if (consultant) {
        const trainingResponse = await fetch(`${API_BASE_URL}/api/consultant/${consultant.id}/training-dashboard`);
        if (trainingResponse.ok) {
          const training = await trainingResponse.json();
          console.log('Training data received:', training);
          console.log('Current enrollments:', training.current_enrollments);
          setTrainingData(training);
        }
      }
    } catch (error) {
      console.error('Error fetching training data:', error);
    } finally {
      setRefreshingTraining(false);
    }
  }, [user?.email]);

  // Handle training enrollment
  const handleTrainingEnrollment = async (course: {
    name?: string;
    title?: string;
    provider?: string;
    duration_hours?: number;
    cost?: number;
    difficulty?: string;
  }) => {
    if (!user?.email) return;
    
    try {
      setEnrollmentLoading(true);
      
      // Find consultant ID first
      const consultantsResponse = await fetch(`${API_BASE_URL}/api/consultants`);
      if (!consultantsResponse.ok) return;
      
      const consultants: Consultant[] = await consultantsResponse.json();
      const consultant = consultants.find((c: Consultant) => c.email === user.email);
      
      if (consultant) {
        // Enroll in training
        const enrollResponse = await fetch(`${API_BASE_URL}/api/consultant/${consultant.id}/enroll-training`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            training_program: course.name || course.title,
            provider: course.provider,
            duration_hours: course.duration_hours
          })
        });
        
        if (enrollResponse.ok) {
          const enrollResult = await enrollResponse.json();
          
          // Update progress to simulate starting the course
          const progressResponse = await fetch(`${API_BASE_URL}/api/consultant/${consultant.id}/update-training-progress`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              progress_percentage: 10, // Start with 10% to show enrollment
              training_program: course.name || course.title
            })
          });
          
          if (progressResponse.ok) {
            // Refresh all data to show updated progress
            await fetchTrainingData();
            await fetchConsultantData();
            
            // Simulate progress updates over time
            setTimeout(async () => {
              await updateTrainingProgress(consultant.id, course.name || course.title, 30);
            }, 5000); // Update to 30% after 5 seconds
            
            setTimeout(async () => {
              await updateTrainingProgress(consultant.id, course.name || course.title, 65);
            }, 10000); // Update to 65% after 10 seconds
            
            setTimeout(async () => {
              await updateTrainingProgress(consultant.id, course.name || course.title, 100);
            }, 15000); // Complete after 15 seconds
            
            alert(`Successfully enrolled in ${course.name || course.title}! Watch your progress update automatically.`);
          }
        }
      }
    } catch (error) {
      console.error('Error enrolling in training:', error);
      alert('Failed to enroll in training. Please try again.');
    } finally {
      setEnrollmentLoading(false);
    }
  };

  // Function to update training progress
  const updateTrainingProgress = async (consultantId: number, trainingProgram: string, progressPercentage: number) => {
    try {
      const progressResponse = await fetch(`${API_BASE_URL}/api/consultant/${consultantId}/update-training-progress`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          progress_percentage: progressPercentage,
          training_program: trainingProgram
        })
      });
      
      if (progressResponse.ok) {
        // Refresh data to show updated progress
        await fetchTrainingData();
        await fetchConsultantData();
      }
    } catch (error) {
      console.error('Error updating training progress:', error);
    }
  };

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
            total: 100,
            rate: data.attendance_rate || 0
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
    fetchTrainingData();
  }, [fetchConsultantData, fetchTrainingData]);

  // Auto-refresh training data every 5 seconds to show progress updates
  useEffect(() => {
    const interval = setInterval(() => {
      fetchTrainingData();
    }, 5000); // Refresh every 5 seconds for faster updates

    return () => clearInterval(interval);
  }, [fetchTrainingData]);

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

      {/* Main Dashboard Tabs */}
      <Tabs defaultValue="dashboard" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="dashboard" className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Dashboard
          </TabsTrigger>
          <TabsTrigger value="opportunities" className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            My Opportunities
          </TabsTrigger>
        </TabsList>

        {/* Dashboard Tab Content */}
        <TabsContent value="dashboard" className="space-y-6">
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
        {/* Enhanced Resume Status Card with Upload */}
        <Card className="col-span-1 md:col-span-2 lg:col-span-1">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-sm font-medium">
              <FileText className="h-4 w-4" />
              Resume Status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-2">
              <Badge 
                variant={consultantData.resumeStatus === 'updated' ? 'default' : 'secondary'}
                className={consultantData.resumeStatus === 'updated' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}
              >
                {consultantData.resumeStatus === 'updated' ? 'Updated' : 'Not Updated'}
              </Badge>
            </div>
            
            {/* Resume Upload Section */}
            <div className="space-y-2">
              <label 
                htmlFor="resume-upload" 
                className={`block w-full text-xs py-2 px-3 border border-dashed border-gray-300 rounded-md text-center cursor-pointer hover:border-primary hover:bg-primary/5 transition-colors ${uploadingResume ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {uploadingResume ? 'Uploading...' : 'Upload New Resume (PDF/TXT)'}
              </label>
              <input
                id="resume-upload"
                type="file"
                accept=".pdf,.txt"
                onChange={handleResumeUpload}
                disabled={uploadingResume}
                className="hidden"
              />
            </div>
            
            {/* Upload Message */}
            {uploadMessage && (
              <div className={`text-xs p-2 rounded ${uploadMessage.includes('✅') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                {uploadMessage}
              </div>
            )}
          </CardContent>
        </Card>

        
        
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
          value={(() => {
            if (trainingData?.current_enrollments && trainingData.current_enrollments.length > 0) {
              // Calculate average progress from current enrollments
              const totalProgress = trainingData.current_enrollments.reduce((sum, enrollment) => 
                sum + (enrollment.progress_percentage || 0), 0);
              const averageProgress = Math.round(totalProgress / trainingData.current_enrollments.length);
              return `${averageProgress}%`;
            }
            return consultantData?.trainingProgress || "0%";
          })()}
          status={(() => {
            if (trainingData?.current_enrollments && trainingData.current_enrollments.length > 0) {
              const completedCount = trainingData.current_enrollments.filter(e => e.status === 'completed').length;
              const totalCount = trainingData.current_enrollments.length;
              if (completedCount === totalCount) return 'completed';
              if (completedCount > 0 || trainingData.current_enrollments.some(e => e.status === 'in_progress')) return 'in-progress';
              return 'pending';
            }
            return consultantData.trainingProgress as 'completed' | 'in-progress' | 'pending';
          })()}
          description={(() => {
            if (trainingData?.current_enrollments && trainingData.current_enrollments.length > 0) {
              const completedCount = trainingData.current_enrollments.filter(e => e.status === 'completed').length;
              const totalCount = trainingData.current_enrollments.length;
              const lastUpdated = new Date().toLocaleTimeString();
              return `${completedCount} of ${totalCount} courses completed • Updated: ${lastUpdated}`;
            }
            return "No active training courses";
          })()}
          icon={<GraduationCap className="h-4 w-4" />}
        />
      </div>

      {/* AI Skills Analysis Section */}
      <SkillsAnalysisCard userEmail={user?.email || ''} />

      {/* Training Dashboard Section */}
      <div className="w-full">
        {/* Training Progress */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <GraduationCap className="h-5 w-5 text-primary" aria-hidden="true" />
              Training & Development Dashboard
              <div className="ml-auto flex items-center gap-2">
                {refreshingTraining && (
                  <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full"></div>
                )}
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => fetchTrainingData()}
                  disabled={refreshingTraining}
                >
                  Refresh
                </Button>
              </div>
            </CardTitle>
            <CardDescription>
              Your personalized learning journey with AI-powered recommendations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="current" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="current">Current Training</TabsTrigger>
                <TabsTrigger value="recommendations">Recommended Training</TabsTrigger>
              </TabsList>
              
              <TabsContent value="current" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Show training data from API first, then fall back to consultant data */}
                  {trainingData?.current_enrollments && trainingData.current_enrollments.length > 0 ? (
                    trainingData.current_enrollments.map((module) => (
                      <div key={module.id} className="p-4 border rounded-lg bg-card">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-foreground">{module.program_name}</h4>
                          <Badge 
                            className={module.status === 'completed' ? 'bg-status-completed text-white' : 'bg-status-in-progress text-white'}
                          >
                            {module.progress_percentage}%
                          </Badge>
                        </div>
                        <div className="w-full bg-muted rounded-full h-2 mb-2">
                          <div 
                            className={`h-2 rounded-full transition-all duration-300 ${
                              module.status === 'completed' ? 'bg-status-completed' : 'bg-status-in-progress'
                            }`}
                            style={{ width: `${module.progress_percentage}%` }}
                            role="progressbar"
                            aria-valuenow={module.progress_percentage}
                            aria-valuemin={0}
                            aria-valuemax={100}
                            aria-label={`${module.program_name} progress: ${module.progress_percentage}%`}
                          />
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {module.category || 'Building your expertise in this area'}
                        </p>
                        <div className="mt-2 flex items-center justify-between">
                          <span className="text-xs text-muted-foreground">
                            Status: {module.status === 'completed' ? 'Completed' : module.status === 'in_progress' ? 'In Progress' : 'Enrolled'}
                          </span>
                          <Button variant="outline" size="sm">
                            Continue
                          </Button>
                        </div>
                        {module.estimated_completion && (
                          <div className="mt-2 text-xs text-muted-foreground">
                            Target completion: {module.estimated_completion}
                          </div>
                        )}
                      </div>
                    ))
                  ) : consultantData?.trainingModules && consultantData.trainingModules.length > 0 ? (
                    consultantData.trainingModules.map((module) => (
                      <div key={module.id} className="p-4 border rounded-lg bg-card">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-foreground">{module.name}</h4>
                          <Badge 
                            className={module.status === 'completed' ? 'bg-status-completed text-white' : 'bg-status-in-progress text-white'}
                          >
                            {module.progress}%
                          </Badge>
                        </div>
                        <div className="w-full bg-muted rounded-full h-2 mb-2">
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
                        <p className="text-sm text-muted-foreground">
                          {module.description || 'Building your expertise in this area'}
                        </p>
                        <div className="mt-2 flex items-center justify-between">
                          <span className="text-xs text-muted-foreground">
                            Status: {module.status === 'completed' ? 'Completed' : module.status === 'in_progress' ? 'In Progress' : 'Enrolled'}
                          </span>
                          <Button variant="outline" size="sm">
                            Continue
                          </Button>
                        </div>
                        {module.estimated_completion && (
                          <div className="mt-2 text-xs text-muted-foreground">
                            Target completion: {module.estimated_completion}
                          </div>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className="col-span-2 text-center py-8">
                      <GraduationCap className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                      <p className="text-muted-foreground">No active training programs</p>
                      <p className="text-sm text-muted-foreground">Check recommendations to start learning</p>
                    </div>
                  )}
                </div>
              </TabsContent>
              
              <TabsContent value="recommendations" className="space-y-4">
                <div className="space-y-4">
                  <div className="p-4 border rounded-lg bg-card">
                    <h4 className="font-medium text-foreground mb-2">Skills-Based Recommendations</h4>
                    <p className="text-sm text-muted-foreground mb-4">
                      Based on missed opportunities and skill gaps analysis:
                    </p>
                    <div className="space-y-3">
                      {/* Show training courses based on skill gaps */}
                      {trainingData?.opportunity_based_recommendations?.training_courses?.length > 0 ? (
                        trainingData.opportunity_based_recommendations.training_courses.map((course, index) => (
                          <div key={index} className="p-3 bg-muted/30 rounded-lg">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <h5 className="font-medium text-foreground">{course.name}</h5>
                                <p className="text-sm text-muted-foreground mt-1">
                                  {course.reason}
                                </p>
                                <p className="text-xs text-muted-foreground mt-1">
                                  Missing skill: <span className="font-medium">{course.missing_skill}</span>
                                </p>
                                {course.sample_opportunities && course.sample_opportunities.length > 0 && (
                                  <p className="text-xs text-muted-foreground mt-1">
                                    Required for: {course.sample_opportunities.slice(0, 2).join(', ')}
                                    {course.sample_opportunities.length > 2 && ` +${course.sample_opportunities.length - 2} more`}
                                  </p>
                                )}
                                <div className="flex items-center gap-2 mt-2">
                                  <Badge 
                                    variant={course.priority === 'High' ? 'destructive' : course.priority === 'Medium' ? 'default' : 'secondary'} 
                                  >
                                    {course.priority} Priority
                                  </Badge>
                                  <span className="text-xs text-muted-foreground">
                                    {course.duration_hours || 40}h • {course.provider || 'Professional Training'} • ${course.cost || 0}
                                  </span>
                                </div>
                              </div>
                              <div className="flex flex-col gap-2 ml-4">
                                <Button 
                                  variant="outline" 
                                  size="sm"
                                  onClick={() => handleTrainingEnrollment(course)}
                                  disabled={enrollmentLoading}
                                >
                                  {enrollmentLoading ? 'Enrolling...' : 'Enroll Now'}
                                </Button>
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  onClick={() => updateTrainingProgress(1, course.name, Math.floor(Math.random() * 100))}
                                >
                                  Demo Progress
                                </Button>
                              </div>
                            </div>
                          </div>
                        ))
                      ) : trainingData?.opportunity_based_recommendations?.missing_skills?.length > 0 ? (
                        // Show skill gaps if no training courses available
                        trainingData.opportunity_based_recommendations.missing_skills.map((skillData, index) => (
                          <div key={index} className="p-3 bg-muted/30 rounded-lg">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <h5 className="font-medium text-foreground">{skillData.skill}</h5>
                                <p className="text-sm text-muted-foreground mt-1">
                                  Required for: {Array.isArray(skillData.opportunities) 
                                    ? skillData.opportunities.join(', ')
                                    : skillData.opportunities || 'Multiple opportunities'}
                                </p>
                                <Badge 
                                  variant={skillData.priority === 'High' ? 'destructive' : 'default'} 
                                  className="mt-2"
                                >
                                  {skillData.priority || 'High'} Priority
                                </Badge>
                              </div>
                              <Button 
                                variant="outline" 
                                size="sm" 
                                className="ml-4"
                                onClick={() => handleTrainingEnrollment({
                                  name: `${skillData.skill} Training`,
                                  provider: 'Professional Development',
                                  duration_hours: 40
                                })}
                                disabled={enrollmentLoading}
                              >
                                {enrollmentLoading ? 'Enrolling...' : 'Find Training'}
                              </Button>
                            </div>
                          </div>
                        ))
                      ) : (
                        // Fallback recommendations only if no real data
                        <div className="text-center py-8">
                          <GraduationCap className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                          <p className="text-muted-foreground">No skill gaps identified</p>
                          <p className="text-sm text-muted-foreground">Great job! Your skills match current market opportunities.</p>
                        </div>
                      )}
                    </div>
                    {trainingData?.dashboard_metrics && trainingData.dashboard_metrics.skills_to_develop > 0 && (
                      <div className="mt-4 p-3 bg-primary/10 rounded-lg">
                        <div className="flex items-center justify-between text-sm">
                          <span>Skills to develop: {trainingData.dashboard_metrics.skills_to_develop}</span>
                          <span>Missed opportunities: {trainingData.dashboard_metrics.missed_opportunities}</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </TabsContent>
            </Tabs>
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
        </TabsContent>

        {/* Opportunities Tab Content */}
        <TabsContent value="opportunities">
          <ConsultantOpportunityDashboard consultantEmail={user?.email || ''} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
