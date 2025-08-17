import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { Users, Briefcase, FileText, TrendingUp, Plus, Edit, Trash2, UserPlus, X, MessageSquare, Send } from "lucide-react";
import { ConsultantFilter } from "@/components/Admin/ConsultantFilter";
import { ConsultantTable } from "@/components/Admin/ConsultantTable";
import { AIAgentQueue } from "@/components/Admin/AIAgentQueue";

// API configuration
const API_BASE_URL = 'http://localhost:8000';

interface AttendanceRecord {
  date: string;
  status: string;
  check_in: string | null;
  check_out: string | null;
}

// Types for chatbot responses
interface AttendanceUser {
  name: string;
  email: string;
  check_in?: string;
  status: string;
}

// Interface for API data
interface DashboardMetrics {
  totalConsultants: number;
  benchConsultants: number;
  ongoingProjects: number;
  reportsGenerated: number;
  activeAssignments: number;
  openOpportunities: number;
}

interface Consultant {
  id: string;
  name: string;
  email: string;
  phone?: string;
  location?: string;
  primary_skill: string;
  skills?: string[];
  soft_skills?: string[];
  experience_years: number;
  department: string;
  status: string;
  attendance_rate: number;
  training_status: string;
  availability_status?: string;
  active_assignments: Assignment[];
}

interface NewConsultantForm {
  name: string;
  email: string;
  phone: string;
  location: string;
  experience_years: number;
  department: string;
  primary_skill: string;
  skills: string[];
  soft_skills: string[];
  availability_status: string;
}

interface Assignment {
  opportunity_id: number;
  opportunity_name: string;
  client_name: string;
  status: string;
}

const AdminDashboard: React.FC = () => {
  const [showReport, setShowReport] = useState(false);
  const [showLogs, setShowLogs] = useState(false);
  const [showConsultantTable, setShowConsultantTable] = useState(false);
  const [showAttendanceChatbot, setShowAttendanceChatbot] = useState(false);
  const [showAddConsultant, setShowAddConsultant] = useState(false);
  const [dashboardMetrics, setDashboardMetrics] = useState<DashboardMetrics | null>(null);
  const [consultants, setConsultants] = useState<Consultant[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Temporary variables for the form elements that still exist in JSX (will be cleaned up)
  const [newSkill, setNewSkill] = useState('');
  const [newSoftSkill, setNewSoftSkill] = useState('');
  const [addingConsultant, setAddingConsultant] = useState(false);
  const [newConsultant, setNewConsultant] = useState({
    name: '',
    email: '',
    phone: '',
    location: '',
    experience_years: 0,
    department: '',
    primary_skill: '',
    skills: [] as string[],
    soft_skills: [] as string[],
    availability_status: 'available'
  });
  
  // Attendance Chatbot state
  const [chatbotMessages, setChatbotMessages] = useState<Array<{id: number, type: 'user' | 'bot', message: string, timestamp: Date}>>([]);
  const [chatbotInput, setChatbotInput] = useState('');
  const [chatbotLoading, setChatbotLoading] = useState(false);

  // Fetch data from API
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch metrics
      const metricsResponse = await fetch(`${API_BASE_URL}/api/dashboard/metrics`);
      if (metricsResponse.ok) {
        const metricsData = await metricsResponse.json();
        setDashboardMetrics(metricsData);
      }

      // Fetch consultants
      const consultantsResponse = await fetch(`${API_BASE_URL}/api/consultants`);
      if (consultantsResponse.ok) {
        const consultantsData = await consultantsResponse.json();
        setConsultants(consultantsData);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Delete consultant
  const handleDeleteConsultant = async (consultantId: string) => {
    if (!confirm('Are you sure you want to delete this consultant?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/consultants/${consultantId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        await fetchDashboardData();
        alert('Consultant deleted successfully!');
      } else {
        alert('Failed to delete consultant');
      }
    } catch (error) {
      console.error('Error deleting consultant:', error);
      alert('Failed to delete consultant. Please try again.');
    }
  };

  // Handle attendance chatbot query
  const handleChatbotQuery = async () => {
    if (!chatbotInput.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user' as const,
      message: chatbotInput.trim(),
      timestamp: new Date()
    };

    setChatbotMessages(prev => [...prev, userMessage]);
    setChatbotLoading(true);
    
    const currentInput = chatbotInput;
    setChatbotInput('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/attendance/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: currentInput })
      });

      if (response.ok) {
        const data = await response.json();
        
        // Format the response properly
        let formattedMessage = '';
        
        if (typeof data.response === 'string') {
          formattedMessage = data.response;
        } else if (data.response && typeof data.response === 'object') {
          // Handle structured response from chatbot
          if (data.response.error) {
            formattedMessage = data.response.error;
          } else if (data.response.message && data.response.data) {
            // Format structured data into readable message
            const responseData = data.response.data;
            let message = data.response.message + '\n\n';
            
            if (data.response.type === 'today_summary') {
              message += `**Today's Stats:**\n`;
              message += `• Total Consultants: ${responseData.total_consultants}\n`;
              message += `• Present: ${responseData.present_count}\n`;
              message += `• Absent: ${responseData.absent_count}\n`;
              message += `• Attendance Rate: ${responseData.attendance_rate}%\n\n`;
              
              if (responseData.present_users && responseData.present_users.length > 0) {
                message += `**Present Today:**\n`;
                responseData.present_users.forEach((user: AttendanceUser) => {
                  message += `• ${user.name} (${user.check_in || 'No check-in time'})\n`;
                });
              }
              
              if (responseData.late_users && responseData.late_users.length > 0) {
                message += `\n**Late Arrivals:**\n`;
                responseData.late_users.forEach((user: AttendanceUser) => {
                  message += `• ${user.name} (${user.check_in})\n`;
                });
              }
            } else if (data.response.type === 'personal_stats') {
              message += `**${responseData.user_name} Attendance:**\n`;
              message += `• Attendance Rate: ${responseData.attendance_rate}%\n`;
              message += `• Present Days: ${responseData.present_days}\n`;
              message += `• Absent Days: ${responseData.absent_days}\n`;
              message += `• Leave Days: ${responseData.leave_days}\n`;
              if (responseData.recent_records && responseData.recent_records.length > 0) {
                message += `\n**Recent Records:**\n`;
                responseData.recent_records.slice(0, 5).forEach((record: AttendanceRecord) => {
                  message += `• ${record.date}: ${record.status}`;
                  if (record.check_in) message += ` (${record.check_in} - ${record.check_out || 'N/A'})`;
                  message += `\n`;
                });
              }
            } else if (data.response.type === 'personal_attendance') {
              message += `**Your Attendance:**\n`;
              message += `• Attendance Rate: ${responseData.attendance_rate}%\n`;
              message += `• Present Days: ${responseData.present_days}\n`;
              message += `• Absent Days: ${responseData.absent_days}\n`;
              message += `• Leave Days: ${responseData.leave_days}\n`;
            } else if (data.response.type === 'help') {
              message = data.response.message + '\n\n';
              if (data.response.data && data.response.data.suggestions) {
                message += '**Try these examples:**\n';
                data.response.data.suggestions.forEach((suggestion: string) => {
                  message += `• ${suggestion}\n`;
                });
              }
            } else if (data.response.type === 'error') {
              message = `Error: ${data.response.message}`;
              if (data.response.data && data.response.data.person_searched) {
                message += `\n\nTip: Try using the exact name as it appears in the system.`;
              }
            } else {
              // Generic formatting for other response types
              message += JSON.stringify(responseData, null, 2);
            }
            
            formattedMessage = message;
          } else {
            formattedMessage = JSON.stringify(data.response, null, 2);
          }
        } else {
          formattedMessage = 'I received an unexpected response format.';
        }
        
        const botMessage = {
          id: Date.now() + 1,
          type: 'bot' as const,
          message: formattedMessage,
          timestamp: new Date()
        };
        setChatbotMessages(prev => [...prev, botMessage]);
      } else {
        const errorMessage = {
          id: Date.now() + 1,
          type: 'bot' as const,
          message: 'Sorry, I encountered an error processing your request.',
          timestamp: new Date()
        };
        setChatbotMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Chatbot error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot' as const,
        message: 'Sorry, I could not connect to the attendance system.',
        timestamp: new Date()
      };
      setChatbotMessages(prev => [...prev, errorMessage]);
    } finally {
      setChatbotLoading(false);
    }
  };

  // Handle quick question selection
  const handleQuickQuestion = async (question: string) => {
    setChatbotInput(question);
    
    const userMessage = {
      id: Date.now(),
      type: 'user' as const,
      message: question,
      timestamp: new Date()
    };

    setChatbotMessages(prev => [...prev, userMessage]);
    setChatbotLoading(true);
    setChatbotInput('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/attendance/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });

      if (response.ok) {
        const data = await response.json();
        
        // Format the response properly
        let formattedMessage = '';
        
        if (typeof data.response === 'string') {
          formattedMessage = data.response;
        } else if (data.response && typeof data.response === 'object') {
          // Handle structured response from chatbot
          if (data.response.error) {
            formattedMessage = data.response.error;
          } else if (data.response.message && data.response.data) {
            // Format structured data into readable message
            const responseData = data.response.data;
            let message = data.response.message + '\n\n';
            
            if (data.response.type === 'today_summary') {
              message += `**Today's Stats:**\n`;
              message += `• Total Consultants: ${responseData.total_consultants}\n`;
              message += `• Present: ${responseData.present_count}\n`;
              message += `• Absent: ${responseData.absent_count}\n`;
              message += `• Attendance Rate: ${responseData.attendance_rate}%\n\n`;
              
              if (responseData.present_users && responseData.present_users.length > 0) {
                message += `**Present Today:**\n`;
                responseData.present_users.forEach((user: AttendanceUser) => {
                  message += `• ${user.name} (${user.check_in || 'No check-in time'})\n`;
                });
              }
              
              if (responseData.late_users && responseData.late_users.length > 0) {
                message += `\n**Late Arrivals:**\n`;
                responseData.late_users.forEach((user: AttendanceUser) => {
                  message += `• ${user.name} (${user.check_in})\n`;
                });
              }
            } else if (data.response.type === 'personal_stats') {
              message += `**${responseData.user_name} Attendance:**\n`;
              message += `• Attendance Rate: ${responseData.attendance_rate}%\n`;
              message += `• Present Days: ${responseData.present_days}\n`;
              message += `• Absent Days: ${responseData.absent_days}\n`;
              message += `• Leave Days: ${responseData.leave_days}\n`;
              if (responseData.recent_records && responseData.recent_records.length > 0) {
                message += `\n**Recent Records:**\n`;
                responseData.recent_records.slice(0, 5).forEach((record: AttendanceRecord) => {
                  message += `• ${record.date}: ${record.status}`;
                  if (record.check_in) message += ` (${record.check_in} - ${record.check_out || 'N/A'})`;
                  message += `\n`;
                });
              }
            } else if (data.response.type === 'personal_attendance') {
              message += `**Your Attendance:**\n`;
              message += `• Attendance Rate: ${responseData.attendance_rate}%\n`;
              message += `• Present Days: ${responseData.present_days}\n`;
              message += `• Absent Days: ${responseData.absent_days}\n`;
              message += `• Leave Days: ${responseData.leave_days}\n`;
            } else if (data.response.type === 'help') {
              message = data.response.message + '\n\n';
              if (data.response.data && data.response.data.suggestions) {
                message += '**Try these examples:**\n';
                data.response.data.suggestions.forEach((suggestion: string) => {
                  message += `• ${suggestion}\n`;
                });
              }
            } else if (data.response.type === 'error') {
              message = `Error: ${data.response.message}`;
              if (data.response.data && data.response.data.person_searched) {
                message += `\n\nTip: Try using the exact name as it appears in the system.`;
              }
            } else {
              // Generic formatting for other response types
              message += JSON.stringify(responseData, null, 2);
            }
            
            formattedMessage = message;
          } else {
            formattedMessage = JSON.stringify(data.response, null, 2);
          }
        } else {
          formattedMessage = 'I received an unexpected response format.';
        }
        
        const botMessage = {
          id: Date.now() + 1,
          type: 'bot' as const,
          message: formattedMessage,
          timestamp: new Date()
        };
        setChatbotMessages(prev => [...prev, botMessage]);
      } else {
        const errorMessage = {
          id: Date.now() + 1,
          type: 'bot' as const,
          message: 'Sorry, I encountered an error processing your request.',
          timestamp: new Date()
        };
        setChatbotMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Chatbot error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot' as const,
        message: 'Sorry, I could not connect to the attendance system.',
        timestamp: new Date()
      };
      setChatbotMessages(prev => [...prev, errorMessage]);
    } finally {
      setChatbotLoading(false);
    }
  };

  // Add skill to list
  const addSkill = () => {
    if (newSkill.trim() && !newConsultant.skills.includes(newSkill.trim())) {
      setNewConsultant(prev => ({
        ...prev,
        skills: [...prev.skills, newSkill.trim()]
      }));
      setNewSkill('');
    }
  };

  // Add soft skill to list
  const addSoftSkill = () => {
    if (newSoftSkill.trim() && !newConsultant.soft_skills.includes(newSoftSkill.trim())) {
      setNewConsultant(prev => ({
        ...prev,
        soft_skills: [...prev.soft_skills, newSoftSkill.trim()]
      }));
      setNewSoftSkill('');
    }
  };

  // Remove skill from list
  const removeSkill = (skillToRemove: string) => {
    setNewConsultant(prev => ({
      ...prev,
      skills: prev.skills.filter(skill => skill !== skillToRemove)
    }));
  };

  // Remove soft skill from list
  const removeSoftSkill = (skillToRemove: string) => {
    setNewConsultant(prev => ({
      ...prev,
      soft_skills: prev.soft_skills.filter(skill => skill !== skillToRemove)
    }));
  };

  // Handle add consultant (simplified)
  const handleAddConsultant = async () => {
    alert('Add consultant functionality has been simplified. Please contact admin to add new consultants.');
  };

  // Generate dynamic metrics array from API data
  const metricsCards = dashboardMetrics ? [
    {
      title: "Total Consultants",
      description: "Across all departments",
      value: dashboardMetrics.totalConsultants,
      icon: Users,
    },
    {
      title: "Bench Consultants",
      description: "Available for allocation",
      value: dashboardMetrics.benchConsultants,
      icon: Briefcase,
    },
    {
      title: "Active Assignments",
      description: "Currently assigned",
      value: dashboardMetrics.activeAssignments,
      icon: TrendingUp,
    },
    {
      title: "Open Opportunities",
      description: "Available projects",
      value: dashboardMetrics.openOpportunities,
      icon: FileText,
    },
  ] : [];

  // Generate reports from real consultant data
  const generateReport = () => {
    return consultants
      .filter(c => c.active_assignments.length > 0)
      .map(consultant => ({
        id: consultant.id,
        name: consultant.name,
        project: consultant.active_assignments[0]?.opportunity_name || 'Unknown',
        client: consultant.active_assignments[0]?.client_name || 'Unknown',
        status: consultant.active_assignments[0]?.status || 'Unknown',
        experience: consultant.experience_years,
        skill: consultant.primary_skill
      }));
  };

  // Generate activity logs from consultant data
  const generateActivityLogs = () => {
    const now = new Date();
    const logs = [];
    
    consultants.forEach((consultant, index) => {
      const timeOffset = index * 30; // 30 minutes apart
      const logTime = new Date(now.getTime() - timeOffset * 60000);
      
      if (consultant.active_assignments.length > 0) {
        logs.push({
          id: `assign-${consultant.id}`,
          action: `${consultant.name} assigned to ${consultant.active_assignments[0].opportunity_name}`,
          time: logTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        });
      } else {
        logs.push({
          id: `available-${consultant.id}`,
          action: `${consultant.name} became available on bench`,
          time: logTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        });
      }
    });
    
    return logs.slice(0, 5); // Show last 5 activities
  };

  const reportData = generateReport();
  const activityLogs = generateActivityLogs();

  if (loading) {
    return (
      <div className="p-6 space-y-8">
        <div className="text-center py-8">
          <p className="text-muted-foreground">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-primary">Admin Dashboard</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Overview of system metrics and management options from live database.
        </p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {metricsCards.map((metric, index) => (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {metric.title}
              </CardTitle>
              <metric.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metric.value}</div>
              <p className="text-xs text-muted-foreground">
                {metric.description}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="space-y-4">
        <Separator />
        <h2 className="text-xl font-semibold">Quick Actions</h2>
        <div className="flex flex-wrap gap-4">
          <Button 
            variant="outline" 
            onClick={() => setShowConsultantTable(!showConsultantTable)}
            className="flex items-center gap-2"
          >
            <Users className="h-4 w-4" />
            Manage Consultants
          </Button>
          <Button 
            variant="default" 
            onClick={() => setShowAttendanceChatbot(!showAttendanceChatbot)}
            className="flex items-center gap-2"
          >
            <MessageSquare className="h-4 w-4" />
            Attendance Chatbot
          </Button>
        </div>

        {/* Attendance Chatbot */}
        {showAttendanceChatbot && (
          <Card className="mt-4">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Attendance Chatbot
              </CardTitle>
              <CardDescription>
                Ask questions about any consultant's attendance by name - get instant percentages and stats
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Chat Messages */}
                <div className="h-64 overflow-y-auto border rounded p-4 space-y-3 bg-muted/20">
                  {chatbotMessages.length === 0 ? (
                    <div className="text-center text-muted-foreground">
                      Ask me about any consultant's attendance! Try questions like:
                      <ul className="mt-2 text-sm space-y-1">
                        <li>• "What is John Doe's attendance percentage?"</li>
                        <li>• "Show Sarah Wilson attendance"</li>
                        <li>• "How is Mike Johnson's attendance?"</li>
                        <li>• "What is Kisshore Kumar attendance like?"</li>
                      </ul>
                    </div>
                  ) : (
                    chatbotMessages.map((msg) => (
                      <div key={msg.id} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] p-3 rounded-lg ${
                          msg.type === 'user' 
                            ? 'bg-primary text-primary-foreground ml-4' 
                            : 'bg-secondary mr-4'
                        }`}>
                          <div className="text-sm">{msg.message}</div>
                          <div className="text-xs opacity-70 mt-1">
                            {msg.timestamp.toLocaleTimeString()}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                  {chatbotLoading && (
                    <div className="flex justify-start">
                      <div className="bg-secondary p-3 rounded-lg mr-4">
                        <div className="text-sm">Typing...</div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Chat Input */}
                <div className="flex gap-2">
                  <Textarea
                    value={chatbotInput}
                    onChange={(e) => setChatbotInput(e.target.value)}
                    placeholder="Ask about any consultant's attendance... (e.g., 'John Doe attendance')"
                    className="flex-1 resize-none"
                    rows={2}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleChatbotQuery();
                      }
                    }}
                  />
                  <Button 
                    onClick={handleChatbotQuery}
                    disabled={!chatbotInput.trim() || chatbotLoading}
                    className="self-end"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>

                {/* Quick Question Options */}
                <div className="flex flex-wrap gap-2">
                  <span className="text-sm text-muted-foreground">Quick questions:</span>
                  {[
                    'What is John Doe\'s attendance percentage?',
                    'Show Sarah Wilson attendance',
                    'How is Mike Johnson\'s attendance?',
                    'What is Kisshore Kumar attendance like?',
                    'Who has the best attendance?'
                  ].map((question) => (
                    <Button
                      key={question}
                      variant="outline"
                      size="sm"
                      onClick={() => handleQuickQuestion(question)}
                      className="text-xs"
                      disabled={chatbotLoading}
                    >
                      {question}
                    </Button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Add New Consultant Form - REMOVED FOR SIMPLIFIED DASHBOARD */}
          

        {/* Consultant Management Table */}
        {showConsultantTable && (
          <Card className="mt-4">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Consultant Management
              </CardTitle>
              <CardDescription>
                Manage all consultants and their skills ({consultants.length} total consultants)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Department</TableHead>
                      <TableHead>Experience</TableHead>
                      <TableHead>Primary Skill</TableHead>
                      <TableHead>Skills</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {consultants.map((consultant) => (
                      <TableRow key={consultant.id}>
                        <TableCell className="font-medium">{consultant.name}</TableCell>
                        <TableCell>{consultant.email}</TableCell>
                        <TableCell>{consultant.department || 'N/A'}</TableCell>
                        <TableCell>{consultant.experience_years} years</TableCell>
                        <TableCell>
                          <Badge variant="default">{consultant.primary_skill}</Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex flex-wrap gap-1 max-w-xs">
                            {consultant.skills?.slice(0, 3).map((skill, index) => (
                              <Badge key={index} variant="secondary" className="text-xs">
                                {skill}
                              </Badge>
                            ))}
                            {(consultant.skills?.length || 0) > 3 && (
                              <Badge variant="outline" className="text-xs">
                                +{(consultant.skills?.length || 0) - 3}
                              </Badge>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge 
                            variant={consultant.availability_status === 'available' ? 'default' : 
                                   consultant.availability_status === 'busy' ? 'destructive' : 'secondary'}
                          >
                            {consultant.availability_status || consultant.status || 'Unknown'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button variant="outline" size="sm">
                              <Edit className="h-3 w-3" />
                            </Button>
                            <Button 
                              variant="destructive" 
                              size="sm"
                              onClick={() => handleDeleteConsultant(consultant.id)}
                            >
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                {consultants.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    No consultants found. Add some consultants to get started!
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Live Report Data */}
        {showReport && (
          <Card className="mt-4">
            <CardHeader>
              <CardTitle>Live Assignment Reports</CardTitle>
              <CardDescription>Current consultant assignments from database</CardDescription>
            </CardHeader>
            <CardContent>
              {reportData.length > 0 ? (
                <ul className="text-sm space-y-2">
                  {reportData.map((report) => (
                    <li key={report.id} className="flex justify-between items-center p-2 bg-muted/30 rounded">
                      <div>
                        <strong>{report.name}</strong> ({report.experience} years {report.skill})
                      </div>
                      <div className="text-right">
                        <div>Project: <strong>{report.project}</strong></div>
                        <div className="text-xs text-muted-foreground">Client: {report.client}</div>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-muted-foreground">No active assignments found.</p>
              )}
            </CardContent>
          </Card>
        )}

        {/* Live Activity Logs */}
        {showLogs && (
          <Card className="mt-4">
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Live system activity from database</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="text-sm space-y-1">
                {activityLogs.map((log) => (
                  <li key={log.id} className="flex justify-between">
                    <span>{log.action}</span>
                    <strong>{log.time}</strong>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Status Panels */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Consultant Status</CardTitle>
            <CardDescription>Current bench utilization</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Available on Bench:</span>
                <Badge variant="outline">{dashboardMetrics?.benchConsultants || 0}</Badge>
              </div>
              <div className="flex justify-between">
                <span>Currently Assigned:</span>
                <Badge className="bg-green-500">{dashboardMetrics?.activeAssignments || 0}</Badge>
              </div>
              <div className="flex justify-between">
                <span>Utilization Rate:</span>
                <Badge className="bg-blue-500">
                  {dashboardMetrics ? Math.round((dashboardMetrics.activeAssignments / dashboardMetrics.totalConsultants) * 100) : 0}%
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Skills Distribution</CardTitle>
            <CardDescription>Top consultant skills</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Array.from(new Set(consultants.map(c => c.primary_skill))).slice(0, 5).map((skill, index) => {
                const count = consultants.filter(c => c.primary_skill === skill).length;
                return (
                  <div key={skill} className="flex justify-between">
                    <span>{skill}:</span>
                    <Badge variant="outline">{count} consultant{count !== 1 ? 's' : ''}</Badge>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdminDashboard;
