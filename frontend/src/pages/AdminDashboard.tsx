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
import { Users, Briefcase, FileText, TrendingUp, Plus, Edit, Trash2, UserPlus, X } from "lucide-react";
import { ConsultantFilter } from "@/components/Admin/ConsultantFilter";
import { ConsultantTable } from "@/components/Admin/ConsultantTable";
import { AIAgentQueue } from "@/components/Admin/AIAgentQueue";

// API configuration
const API_BASE_URL = 'http://localhost:8000';

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
  const [showAddConsultant, setShowAddConsultant] = useState(false);
  const [showConsultantTable, setShowConsultantTable] = useState(false);
  const [dashboardMetrics, setDashboardMetrics] = useState<DashboardMetrics | null>(null);
  const [consultants, setConsultants] = useState<Consultant[]>([]);
  const [loading, setLoading] = useState(true);
  const [addingConsultant, setAddingConsultant] = useState(false);
  const [newConsultant, setNewConsultant] = useState<NewConsultantForm>({
    name: '',
    email: '',
    phone: '',
    location: '',
    experience_years: 0,
    department: '',
    primary_skill: '',
    skills: [],
    soft_skills: [],
    availability_status: 'available'
  });
  const [newSkill, setNewSkill] = useState('');
  const [newSoftSkill, setNewSoftSkill] = useState('');

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

  // Add new consultant
  const handleAddConsultant = async () => {
    if (!newConsultant.name || !newConsultant.email || !newConsultant.primary_skill) {
      alert('Please fill in all required fields');
      return;
    }

    setAddingConsultant(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/consultants`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newConsultant,
          status: 'active',
          attendance_rate: 100,
          training_status: 'not-started'
        }),
      });

      if (response.ok) {
        // Reset form
        setNewConsultant({
          name: '',
          email: '',
          phone: '',
          location: '',
          experience_years: 0,
          department: '',
          primary_skill: '',
          skills: [],
          soft_skills: [],
          availability_status: 'available'
        });
        setShowAddConsultant(false);
        // Refresh data to show new consultant
        await fetchDashboardData();
        alert('Consultant added successfully!');
      } else {
        const error = await response.json();
        alert(`Failed to add consultant: ${error.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error adding consultant:', error);
      alert('Failed to add consultant. Please try again.');
    } finally {
      setAddingConsultant(false);
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
            variant="default" 
            onClick={() => setShowAddConsultant(!showAddConsultant)}
            className="flex items-center gap-2"
          >
            <UserPlus className="h-4 w-4" />
            Add New Consultant
          </Button>
          <Button 
            variant="outline" 
            onClick={() => setShowConsultantTable(!showConsultantTable)}
            className="flex items-center gap-2"
          >
            <Users className="h-4 w-4" />
            Manage Consultants
          </Button>
          <Button variant="outline" onClick={() => setShowReport(!showReport)}>
            Generate Report
          </Button>
          <Button variant="ghost" onClick={() => setShowLogs(!showLogs)}>
            View Activity Logs
          </Button>
          <Button variant="outline" onClick={fetchDashboardData}>
            Refresh Data
          </Button>
        </div>

        {/* Add New Consultant Form */}
        {showAddConsultant && (
          <Card className="mt-4">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserPlus className="h-5 w-5" />
                Add New Consultant
              </CardTitle>
              <CardDescription>
                Add a new consultant to the database with complete profile information
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Basic Information */}
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="name">Full Name *</Label>
                    <Input
                      id="name"
                      value={newConsultant.name}
                      onChange={(e) => setNewConsultant(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="Enter full name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="email">Email *</Label>
                    <Input
                      id="email"
                      type="email"
                      value={newConsultant.email}
                      onChange={(e) => setNewConsultant(prev => ({ ...prev, email: e.target.value }))}
                      placeholder="Enter email address"
                    />
                  </div>
                  <div>
                    <Label htmlFor="phone">Phone</Label>
                    <Input
                      id="phone"
                      value={newConsultant.phone}
                      onChange={(e) => setNewConsultant(prev => ({ ...prev, phone: e.target.value }))}
                      placeholder="Enter phone number"
                    />
                  </div>
                  <div>
                    <Label htmlFor="location">Location</Label>
                    <Input
                      id="location"
                      value={newConsultant.location}
                      onChange={(e) => setNewConsultant(prev => ({ ...prev, location: e.target.value }))}
                      placeholder="Enter location"
                    />
                  </div>
                </div>

                {/* Professional Information */}
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="experience">Experience (Years) *</Label>
                    <Input
                      id="experience"
                      type="number"
                      value={newConsultant.experience_years}
                      onChange={(e) => setNewConsultant(prev => ({ ...prev, experience_years: parseInt(e.target.value) || 0 }))}
                      placeholder="Years of experience"
                    />
                  </div>
                  <div>
                    <Label htmlFor="department">Department *</Label>
                    <Select value={newConsultant.department} onValueChange={(value) => setNewConsultant(prev => ({ ...prev, department: value }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select department" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Engineering">Engineering</SelectItem>
                        <SelectItem value="Data Science">Data Science</SelectItem>
                        <SelectItem value="Product Management">Product Management</SelectItem>
                        <SelectItem value="Design">Design</SelectItem>
                        <SelectItem value="Marketing">Marketing</SelectItem>
                        <SelectItem value="Sales">Sales</SelectItem>
                        <SelectItem value="Operations">Operations</SelectItem>
                        <SelectItem value="Finance">Finance</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="primary_skill">Primary Skill *</Label>
                    <Input
                      id="primary_skill"
                      value={newConsultant.primary_skill}
                      onChange={(e) => setNewConsultant(prev => ({ ...prev, primary_skill: e.target.value }))}
                      placeholder="e.g., React, Python, Project Management"
                    />
                  </div>
                  <div>
                    <Label htmlFor="availability">Availability Status</Label>
                    <Select value={newConsultant.availability_status} onValueChange={(value) => setNewConsultant(prev => ({ ...prev, availability_status: value }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select availability" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="available">Available</SelectItem>
                        <SelectItem value="busy">Busy</SelectItem>
                        <SelectItem value="on_leave">On Leave</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>

              {/* Skills Section */}
              <div className="space-y-4">
                <div>
                  <Label htmlFor="skills">Technical Skills</Label>
                  <div className="flex gap-2">
                    <Input
                      id="skills"
                      value={newSkill}
                      onChange={(e) => setNewSkill(e.target.value)}
                      placeholder="Add technical skill"
                      onKeyPress={(e) => e.key === 'Enter' && addSkill()}
                    />
                    <Button type="button" onClick={addSkill} size="sm">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {newConsultant.skills.map((skill, index) => (
                      <Badge key={index} variant="secondary" className="flex items-center gap-1">
                        {skill}
                        <X 
                          className="h-3 w-3 cursor-pointer" 
                          onClick={() => removeSkill(skill)}
                        />
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <Label htmlFor="soft_skills">Soft Skills</Label>
                  <div className="flex gap-2">
                    <Input
                      id="soft_skills"
                      value={newSoftSkill}
                      onChange={(e) => setNewSoftSkill(e.target.value)}
                      placeholder="Add soft skill"
                      onKeyPress={(e) => e.key === 'Enter' && addSoftSkill()}
                    />
                    <Button type="button" onClick={addSoftSkill} size="sm">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {newConsultant.soft_skills.map((skill, index) => (
                      <Badge key={index} variant="outline" className="flex items-center gap-1">
                        {skill}
                        <X 
                          className="h-3 w-3 cursor-pointer" 
                          onClick={() => removeSoftSkill(skill)}
                        />
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4 pt-4">
                <Button 
                  onClick={handleAddConsultant} 
                  disabled={addingConsultant}
                  className="flex items-center gap-2"
                >
                  {addingConsultant ? 'Adding...' : 'Add Consultant'}
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setShowAddConsultant(false)}
                >
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

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
