import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  User, 
  Brain, 
  Upload, 
  Plus, 
  Edit, 
  CheckCircle, 
  XCircle, 
  FileText, 
  Star,
  Clock,
  Award,
  TrendingUp,
  RefreshCw,
  GraduationCap
} from 'lucide-react';

// API configuration
const API_BASE_URL = 'http://localhost:8000';

interface Skill {
  id: number;
  name: string;
  proficiency_level: string;
  years_experience: number;
  source: string;
  confidence_score: number;
  is_primary: boolean;
  created_at?: string;
}

interface ConsultantProfile {
  id: number;
  name: string;
  email: string;
  primary_skill: string;
  years_of_experience: number;
  current_status: string;
  bench_status: string;
  resume_status: string;
}

interface ProfileData {
  id: string;
  name: string;
  email: string;
  phone: string;
  location: string;
  experience_years: number;
  department: string;
  primary_skill: string;
  status: string;
  attendance_rate: number;
  training_status: string;
  availability_status: string;
  technical_skills: string[];
  soft_skills: string[];
  resume_analysis?: {
    ai_summary?: string;
    confidence_score?: number;
    skills?: string[];
    competencies?: string[];
    analysis_method?: string;
    file_name?: string;
    created_at?: string;
  };
  resume_status?: boolean;
  resume_uploaded?: boolean;
  has_resume_analysis?: boolean;
  created_at?: string;
  updated_at?: string;
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
}

interface TrainingDashboardData {
  current_enrollments: TrainingModule[];
  opportunity_based_recommendations: {
    missing_skills: {
      skill: string;
      opportunities: string[];
      priority: string;
    }[];
    training_courses: TrainingRecommendation[];
    total_missing: number;
  };
  dashboard_metrics: {
    skills_to_develop: number;
    active_trainings: number;
    missed_opportunities: number;
  };
}

const ConsultantProfile = ({ consultantEmail }: { consultantEmail: string }) => {
  const [profileData, setProfileData] = useState<ProfileData | null>(null);
  const [trainingData, setTrainingData] = useState<TrainingDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [uploadingResume, setUploadingResume] = useState(false);
  const [addingSkill, setAddingSkill] = useState(false);
  const [syncingSkills, setSyncingSkills] = useState(false);
  
  // Add skill form state
  const [newSkill, setNewSkill] = useState({
    skill_name: '',
    category: 'technical',
    proficiency_level: 'intermediate',
    years_experience: 1
  });
  
  // File upload state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  useEffect(() => {
    fetchProfile();
    fetchTrainingData();
  }, [consultantEmail]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/consultant/${consultantEmail}/profile`);
      const data = await response.json();
      
      if (response.ok) {
        setProfileData(data);
      } else {
        setError(data.detail || 'Failed to fetch profile');
      }
    } catch (error) {
      setError('Error connecting to backend');
    } finally {
      setLoading(false);
    }
  };

  // Fetch training dashboard data
  const fetchTrainingData = async () => {
    try {
      // Find consultant ID first
      const consultantsResponse = await fetch(`${API_BASE_URL}/api/consultants`);
      if (!consultantsResponse.ok) return;
      
      const consultants: { id: number; email: string; name: string }[] = await consultantsResponse.json();
      const consultant = consultants.find((c) => c.email === consultantEmail);
      
      if (consultant) {
        const trainingResponse = await fetch(`${API_BASE_URL}/api/consultant/${consultant.id}/training-dashboard`);
        if (trainingResponse.ok) {
          const training = await trainingResponse.json();
          setTrainingData(training);
        }
      }
    } catch (error) {
      console.error('Error fetching training data:', error);
    }
  };

  const handleResumeUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }

    try {
      setUploadingResume(true);
      setError('');
      setSuccess('');

      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch(`${API_BASE_URL}/api/consultant/${consultantEmail}/upload-resume-enhanced`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(`Resume processed successfully! Extracted ${data.skills_extracted} skills.`);
        setSelectedFile(null);
        fetchProfile(); // Refresh profile data
      } else {
        setError(data.detail || 'Resume upload failed');
      }
    } catch (error) {
      setError('Error uploading resume');
    } finally {
      setUploadingResume(false);
    }
  };

  const handleAddSkill = async () => {
    try {
      setAddingSkill(true);
      setError('');

      const response = await fetch(`${API_BASE_URL}/api/consultant/${consultantEmail}/add-skill`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSkill),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess('Skill added successfully!');
        setNewSkill({
          skill_name: '',
          category: 'technical',
          proficiency_level: 'intermediate',
          years_experience: 1
        });
        fetchProfile(); // Refresh profile data
      } else {
        setError(data.detail || 'Failed to add skill');
      }
    } catch (error) {
      setError('Error adding skill');
    } finally {
      setAddingSkill(false);
    }
  };

  const handleSyncSkills = async () => {
    if (!profileData) return;
    
    setSyncingSkills(true);
    setError('');
    setSuccessMessage('');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/consultant/${profileData.email}/sync-skills`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setSuccessMessage(`Successfully synchronized ${data.total_new_skills} new skills from resume analysis!`);
        fetchProfile(); // Refresh profile data to show synchronized skills
      } else {
        setError(data.detail || 'Failed to sync skills');
      }
    } catch (error) {
      setError('Error syncing skills from resume analysis');
    } finally {
      setSyncingSkills(false);
    }
  };

  const getSourceIcon = (source: string) => {
    switch (source) {
      case 'resume':
        return <FileText className="w-4 h-4 text-blue-500" />;
      case 'manual':
        return <User className="w-4 h-4 text-green-500" />;
      case 'resume_verified':
        return <CheckCircle className="w-4 h-4 text-emerald-500" />;
      default:
        return <Brain className="w-4 h-4 text-purple-500" />;
    }
  };

  const getProficiencyColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'expert':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'advanced':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'beginner':
        return 'bg-gray-100 text-gray-800 border-gray-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'programming_languages':
        return '💻';
      case 'frameworks':
        return '🔧';
      case 'databases':
        return '🗄️';
      case 'cloud_platforms':
        return '☁️';
      case 'tools':
        return '🛠️';
      case 'methodologies':
        return '📋';
      default:
        return '🎯';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="h-64 bg-gray-200 rounded"></div>
              <div className="h-64 bg-gray-200 rounded"></div>
              <div className="h-64 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error && !profileData) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Alert className="bg-red-50 border-red-200">
            <XCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">My Profile</h1>
              <p className="text-gray-600 mt-1">Manage your skills and resume</p>
            </div>
            <Button onClick={fetchProfile} variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>

        {/* Alerts */}
        {error && (
          <Alert className="mb-6 bg-red-50 border-red-200">
            <XCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-6 bg-green-50 border-green-200">
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>{success}</AlertDescription>
          </Alert>
        )}

        {successMessage && (
          <Alert className="mb-6 bg-blue-50 border-blue-200">
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>{successMessage}</AlertDescription>
          </Alert>
        )}

        {successMessage && (
          <Alert className="mb-6 bg-blue-50 border-blue-200">
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>{successMessage}</AlertDescription>
          </Alert>
        )}

        {profileData && (
          <div className="space-y-6">
            {/* Profile Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Basic Info Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <User className="w-5 h-5" />
                    Profile Overview
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label className="text-sm font-medium text-gray-500">Name</Label>
                    <p className="text-lg font-semibold">{profileData.name}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-500">Email</Label>
                    <p className="text-sm text-gray-700">{profileData.email}</p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-500">Primary Skill</Label>
                    <Badge variant="secondary" className="mt-1">
                      {profileData.primary_skill || 'Not set'}
                    </Badge>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-500">Experience</Label>
                    <p className="text-sm text-gray-700">
                      {profileData.experience_years || 0} years
                    </p>
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-500">Status</Label>
                    <Badge className={
                      profileData.status === 'available' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }>
                      {profileData.status}
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              {/* Skills Summary Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Brain className="w-5 h-5" />
                    Skills Summary
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600">
                      {(profileData.technical_skills?.length || 0) + (profileData.soft_skills?.length || 0)}
                    </div>
                    <p className="text-sm text-gray-500">Total Skills</p>
                  </div>
                  
                  <div className="space-y-2">
                    {profileData.technical_skills && profileData.technical_skills.length > 0 && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600 capitalize flex items-center gap-1">
                          <span>💻</span>
                          Technical Skills
                        </span>
                        <Badge variant="outline" className="text-xs">
                          {profileData.technical_skills.length}
                        </Badge>
                      </div>
                    )}
                    {profileData.soft_skills && profileData.soft_skills.length > 0 && (
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-gray-600 capitalize flex items-center gap-1">
                          <span>🤝</span>
                          Soft Skills
                        </span>
                        <Badge variant="outline" className="text-xs">
                          {profileData.soft_skills.length}
                        </Badge>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Resume Status Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Resume Status
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {profileData.resume_uploaded || profileData.has_resume_analysis ? (
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        <span className="text-sm text-green-700">
                          Resume uploaded and analyzed
                        </span>
                        {profileData.resume_analysis?.analysis_method && (
                          <Badge variant="secondary" className="text-xs">
                            {profileData.resume_analysis.analysis_method}
                          </Badge>
                        )}
                      </div>
                      
                      {profileData.resume_analysis?.file_name && (
                        <div>
                          <Label className="text-sm font-medium text-gray-500">File Name</Label>
                          <p className="text-sm text-gray-700">
                            {profileData.resume_analysis.file_name}
                          </p>
                        </div>
                      )}
                      
                      <div>
                        <Label className="text-sm font-medium text-gray-500">Last Upload</Label>
                        <p className="text-sm text-gray-700">
                          {profileData.resume_analysis?.created_at 
                            ? new Date(profileData.resume_analysis.created_at).toLocaleDateString()
                            : profileData.updated_at
                            ? new Date(profileData.updated_at).toLocaleDateString()
                            : 'Unknown'
                          }
                        </p>
                      </div>
                      
                      <div>
                        <Label className="text-sm font-medium text-gray-500">Extracted Skills</Label>
                        <p className="text-sm text-gray-700">
                          {(profileData.technical_skills?.length || 0) + (profileData.soft_skills?.length || 0)} skills
                          <span className="text-xs text-gray-500 ml-2">
                            ({profileData.technical_skills?.length || 0} technical, {profileData.soft_skills?.length || 0} soft)
                          </span>
                        </p>
                      </div>
                      
                      {profileData.resume_analysis?.ai_summary && (
                        <div>
                          <Label className="text-sm font-medium text-gray-500">AI Summary</Label>
                          <p className="text-sm text-gray-700">
                            {profileData.resume_analysis.ai_summary}
                          </p>
                        </div>
                      )}
                      
                      {profileData.resume_analysis?.confidence_score && (
                        <div>
                          <Label className="text-sm font-medium text-gray-500">Analysis Confidence</Label>
                          <Badge 
                            className={`${
                              profileData.resume_analysis.confidence_score >= 0.8 
                                ? 'bg-green-100 text-green-800' 
                                : profileData.resume_analysis.confidence_score >= 0.6
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-red-100 text-red-800'
                            }`}
                          >
                            {(profileData.resume_analysis.confidence_score * 100).toFixed(0)}% confidence
                          </Badge>
                        </div>
                      )}
                      
                      {/* Upload new resume button */}
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={() => document.getElementById('file-upload')?.click()}
                        className="w-full"
                      >
                        <Upload className="w-4 h-4 mr-2" />
                        Update Resume
                      </Button>
                    </div>
                  ) : (
                    <div className="text-center space-y-3">
                      <XCircle className="w-12 h-12 text-gray-400 mx-auto" />
                      <p className="text-sm text-gray-500">No resume uploaded</p>
                      <Button 
                        onClick={() => document.getElementById('file-upload')?.click()}
                        className="w-full"
                      >
                        <Upload className="w-4 h-4 mr-2" />
                        Upload Resume
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Main Content Tabs */}
            <Tabs defaultValue="skills" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="skills">Skills Management</TabsTrigger>
                <TabsTrigger value="training">Training & Development</TabsTrigger>
                <TabsTrigger value="resume">Resume Upload</TabsTrigger>
                <TabsTrigger value="analytics">Analytics</TabsTrigger>
              </TabsList>

              {/* Skills Management Tab */}
              <TabsContent value="skills" className="space-y-6">
                <div className="flex justify-between items-center">
                  <h3 className="text-xl font-semibold">My Skills</h3>
                  
                  <div className="flex gap-2">
                    {/* Sync Skills Button */}
                    <Button 
                      onClick={handleSyncSkills} 
                      variant="outline"
                      disabled={syncingSkills || !profileData?.resume_analysis}
                    >
                      {syncingSkills ? (
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <RefreshCw className="w-4 h-4 mr-2" />
                      )}
                      Sync from Resume
                    </Button>
                    
                    {/* Add Skill Dialog */}
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button>
                          <Plus className="w-4 h-4 mr-2" />
                          Add Skill
                        </Button>
                      </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Add New Skill</DialogTitle>
                        <DialogDescription>
                          Add a skill to your profile manually
                        </DialogDescription>
                      </DialogHeader>
                      
                      <div className="space-y-4">
                        <div>
                          <Label htmlFor="skill_name">Skill Name</Label>
                          <Input
                            id="skill_name"
                            value={newSkill.skill_name}
                            onChange={(e) => setNewSkill({...newSkill, skill_name: e.target.value})}
                            placeholder="e.g., React, Python, AWS"
                          />
                        </div>
                        
                        <div>
                          <Label htmlFor="category">Category</Label>
                          <Select
                            value={newSkill.category}
                            onValueChange={(value) => setNewSkill({...newSkill, category: value})}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="programming_languages">Programming Languages</SelectItem>
                              <SelectItem value="frameworks">Frameworks</SelectItem>
                              <SelectItem value="databases">Databases</SelectItem>
                              <SelectItem value="cloud_platforms">Cloud Platforms</SelectItem>
                              <SelectItem value="tools">Tools</SelectItem>
                              <SelectItem value="methodologies">Methodologies</SelectItem>
                              <SelectItem value="other">Other</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        
                        <div>
                          <Label htmlFor="proficiency_level">Proficiency Level</Label>
                          <Select
                            value={newSkill.proficiency_level}
                            onValueChange={(value) => setNewSkill({...newSkill, proficiency_level: value})}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="beginner">Beginner</SelectItem>
                              <SelectItem value="intermediate">Intermediate</SelectItem>
                              <SelectItem value="advanced">Advanced</SelectItem>
                              <SelectItem value="expert">Expert</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        
                        <div>
                          <Label htmlFor="years_experience">Years of Experience</Label>
                          <Input
                            id="years_experience"
                            type="number"
                            min="0"
                            max="30"
                            value={newSkill.years_experience}
                            onChange={(e) => setNewSkill({...newSkill, years_experience: parseInt(e.target.value) || 1})}
                          />
                        </div>
                        
                        <Button 
                          onClick={handleAddSkill} 
                          disabled={addingSkill || !newSkill.skill_name.trim()}
                          className="w-full"
                        >
                          {addingSkill ? 'Adding...' : 'Add Skill'}
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                  </div>
                </div>

                {/* Skills by Category */}
                <div className="space-y-6">
                  {/* Technical Skills */}
                  {profileData.technical_skills && profileData.technical_skills.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-lg">
                          <span>💻</span>
                          TECHNICAL SKILLS
                          <Badge variant="outline">{profileData.technical_skills.length}</Badge>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="flex flex-wrap gap-2">
                          {profileData.technical_skills.map((skill, index) => (
                            <Badge key={index} variant="secondary">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {/* Soft Skills */}
                  {profileData.soft_skills && profileData.soft_skills.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-lg">
                          <span>🤝</span>
                          SOFT SKILLS
                          <Badge variant="outline">{profileData.soft_skills.length}</Badge>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="flex flex-wrap gap-2">
                          {profileData.soft_skills.map((skill, index) => (
                            <Badge key={index} variant="outline">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              </TabsContent>

              {/* Training & Development Tab */}
              <TabsContent value="training" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <GraduationCap className="h-5 w-5 text-primary" />
                      Training & Development Dashboard
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
                          {trainingData?.current_enrollments?.map((module) => (
                            <div key={module.id} className="p-4 border rounded-lg bg-card">
                              <div className="flex items-center justify-between mb-2">
                                <h4 className="font-medium text-foreground">{module.name || module.program_name}</h4>
                                <Badge 
                                  className={module.status === 'completed' ? 'bg-green-600 text-white' : 'bg-blue-600 text-white'}
                                >
                                  {module.progress || module.progress_percentage}%
                                </Badge>
                              </div>
                              <div className="w-full bg-muted rounded-full h-2 mb-2">
                                <div 
                                  className={`h-2 rounded-full transition-all duration-300 ${
                                    module.status === 'completed' ? 'bg-green-600' : 'bg-blue-600'
                                  }`}
                                  style={{ width: `${module.progress || module.progress_percentage}%` }}
                                />
                              </div>
                              <p className="text-sm text-muted-foreground">
                                {module.description || module.category || 'Building your expertise in this area'}
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
                          )) || []}
                          {(!trainingData?.current_enrollments || trainingData.current_enrollments.length === 0) && (
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
                              {trainingData?.opportunity_based_recommendations?.missing_skills?.length > 0 ? (
                                trainingData.opportunity_based_recommendations.missing_skills.map((skillData, index) => (
                                  <div key={index} className="p-3 bg-muted/30 rounded-lg">
                                    <div className="flex items-start justify-between">
                                      <div className="flex-1">
                                        <h5 className="font-medium text-foreground">{skillData.skill}</h5>
                                        <p className="text-sm text-muted-foreground mt-1">
                                          Required for: {skillData.opportunities.join(', ')}
                                        </p>
                                        <Badge variant="destructive" className="mt-2">
                                          High Priority
                                        </Badge>
                                      </div>
                                      <Button variant="outline" size="sm" className="ml-4">
                                        Find Training
                                      </Button>
                                    </div>
                                  </div>
                                ))
                              ) : (
                                // Fallback recommendations
                                [
                                  { name: "Advanced React Patterns", priority: "High", reason: "Gap identified in recent opportunities" },
                                  { name: "Cloud Architecture on AWS", priority: "Medium", reason: "Emerging market demand" },
                                  { name: "API Design Best Practices", priority: "Medium", reason: "Complement current skills" }
                                ].map((rec, index) => (
                                  <div key={index} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                                    <div>
                                      <h5 className="font-medium">{rec.name}</h5>
                                      <p className="text-sm text-muted-foreground">{rec.reason}</p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <Badge variant={rec.priority === 'High' ? 'destructive' : 'secondary'}>
                                        {rec.priority}
                                      </Badge>
                                      <Button variant="outline" size="sm">
                                        Enroll
                                      </Button>
                                    </div>
                                  </div>
                                ))
                              )}
                            </div>
                            {trainingData?.dashboard_metrics && (
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
              </TabsContent>

              {/* Resume Upload Tab */}
              <TabsContent value="resume" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Upload className="w-5 h-5" />
                      Upload Resume
                    </CardTitle>
                    <CardDescription>
                      Upload your resume to automatically extract skills and update your profile
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <Label htmlFor="resume-file">Select Resume File</Label>
                      <Input
                        id="resume-file"
                        type="file"
                        accept=".pdf,.txt,.docx"
                        onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                        className="mt-1"
                      />
                      <p className="text-sm text-gray-500 mt-1">
                        Supported formats: PDF, TXT, DOCX
                      </p>
                    </div>
                    
                    {selectedFile && (
                      <div className="p-3 bg-blue-50 rounded-lg">
                        <p className="text-sm text-blue-700">
                          Selected: {selectedFile.name}
                        </p>
                      </div>
                    )}
                    
                    <Button 
                      onClick={handleResumeUpload}
                      disabled={!selectedFile || uploadingResume}
                      className="w-full"
                    >
                      {uploadingResume ? (
                        <>
                          <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                          Processing Resume...
                        </>
                      ) : (
                        <>
                          <Upload className="w-4 h-4 mr-2" />
                          Upload & Analyze Resume
                        </>
                      )}
                    </Button>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Analytics Tab */}
              <TabsContent value="analytics" className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-600">Total Skills</p>
                          <p className="text-2xl font-bold">{(profileData.technical_skills?.length || 0) + (profileData.soft_skills?.length || 0)}</p>
                        </div>
                        <TrendingUp className="w-8 h-8 text-blue-500" />
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-600">Resume Skills</p>
                          <p className="text-2xl font-bold">
                            {(profileData.technical_skills?.length || 0) + (profileData.soft_skills?.length || 0)}
                          </p>
                        </div>
                        <FileText className="w-8 h-8 text-green-500" />
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-600">Technical Skills</p>
                          <p className="text-2xl font-bold">
                            {profileData.technical_skills?.length || 0}
                          </p>
                        </div>
                        <User className="w-8 h-8 text-purple-500" />
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-gray-600">Soft Skills</p>
                          <p className="text-2xl font-bold">
                            {profileData.soft_skills?.length || 0}
                          </p>
                        </div>
                        <Award className="w-8 h-8 text-yellow-500" />
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        )}
      </div>
      
      {/* Hidden file input for resume upload buttons in profile cards */}
      <input
        id="file-upload"
        type="file"
        accept=".pdf,.txt,.docx"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) {
            setSelectedFile(file);
            handleResumeUpload();
          }
        }}
        style={{ display: 'none' }}
      />
    </div>
  );
};

export default ConsultantProfile;
