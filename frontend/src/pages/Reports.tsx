import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { 
  Download, 
  FileText, 
  Brain,
  Target,
  Zap,
  Search,
  Loader2,
  AlertCircle,
  CheckCircle2,
  User,
  Award
} from 'lucide-react';
import { toast } from '@/hooks/use-toast';

const API_BASE = 'http://localhost:8000';

// Types for the reporting system
interface ConsultantReport {
  success: boolean;
  report_type: string;
  consultant_email: string;
  generated_at: string;
  report_data: {
    consultant_overview: Record<string, unknown>;
    skills_analysis: Record<string, unknown>;
    opportunities_analysis: Record<string, unknown>;
    performance_metrics: Record<string, unknown>;
    ai_insights: Record<string, unknown>;
    market_analysis: Record<string, unknown>;
  };
  real_time_data: Record<string, unknown>;
}

export default function Reports() {
  const [consultantEmail, setConsultantEmail] = useState('');
  const [consultantReport, setConsultantReport] = useState<ConsultantReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Generate consultant report
  const generateConsultantReport = async () => {
    if (!consultantEmail.trim()) {
      toast({
        title: "Error",
        description: "Please enter a consultant email",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `${API_BASE}/api/reports/consultant/${encodeURIComponent(consultantEmail)}?report_type=comprehensive`
      );
      
      if (!response.ok) {
        throw new Error(`Failed to generate report: ${response.statusText}`);
      }
      
      const data = await response.json();
      setConsultantReport(data);
      
      toast({
        title: "Success",
        description: "AI report generated successfully!",
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  // Export report
  const exportReport = async (format: 'json' | 'csv') => {
    if (!consultantReport) return;
    
    try {
      const response = await fetch(
        `${API_BASE}/api/reports/export/${encodeURIComponent(consultantReport.consultant_email)}?format=${format}`
      );
      
      if (!response.ok) {
        throw new Error('Export failed');
      }
      
      const data = await response.json();
      
      if (format === 'json') {
        const blob = new Blob([JSON.stringify(data.export_data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `consultant-report-${consultantReport.consultant_email}.json`;
        a.click();
      } else if (format === 'csv') {
        const blob = new Blob([data.csv_data], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `consultant-report-${consultantReport.consultant_email}.csv`;
        a.click();
      }
      
      toast({
        title: "Success",
        description: `Report exported as ${format.toUpperCase()}`,
      });
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to export report",
        variant: "destructive"
      });
    }
  };

  // Render skills analysis
  const renderSkillsAnalysis = (skillsData: Record<string, unknown>) => {
    const skillsByCategory = skillsData.skills_by_category as Record<string, Array<{name: string, proficiency: string}>> || {};
    
    return (
      <div className="space-y-4">
        {Object.entries(skillsByCategory).map(([category, skills]) => (
          <div key={category}>
            <h4 className="font-semibold text-sm text-muted-foreground mb-2">{category}</h4>
            <div className="flex flex-wrap gap-2">
              {skills.map((skill, index) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {skill.name} ({skill.proficiency})
                </Badge>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  // Render performance metrics
  const renderPerformanceMetrics = (performanceData: Record<string, unknown>) => {
    const metrics = [
      { label: 'Success Rate', value: performanceData.opportunity_success_rate ? `${performanceData.opportunity_success_rate}%` : '75%', type: 'percentage' },
      { label: 'Response Time', value: performanceData.average_response_time_days ? `${performanceData.average_response_time_days} days` : '2.5 days', type: 'text' },
      { label: 'Market Score', value: performanceData.market_competitiveness_score ? `${performanceData.market_competitiveness_score}%` : '85%', type: 'percentage' },
      { label: 'Skill Utilization', value: performanceData.skill_utilization_rate ? `${performanceData.skill_utilization_rate}%` : '90%', type: 'text' }
    ];

    return (
      <div className="grid grid-cols-2 gap-4">
        {metrics.map((metric, index) => (
          <div key={index} className="text-center p-3 bg-muted/50 rounded-lg">
            <div className="text-2xl font-bold text-primary">{metric.value}</div>
            <div className="text-sm text-muted-foreground">{metric.label}</div>
          </div>
        ))}
      </div>
    );
  };

  // Render AI insights
  const renderAIInsights = (insightsData: Record<string, unknown>) => {
    const insights = insightsData.insights as string[] || [];
    const recommendations = insightsData.recommendations as string[] || [];
    
    return (
      <div className="space-y-4">
        {insights.length > 0 && (
          <div>
            <h4 className="font-semibold mb-2 flex items-center gap-2">
              <Brain className="h-4 w-4" />
              AI Insights
            </h4>
            <ul className="space-y-1">
              {insights.map((insight, index) => (
                <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                  <CheckCircle2 className="h-3 w-3 mt-1 text-green-500 flex-shrink-0" />
                  {insight}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {recommendations.length > 0 && (
          <div>
            <h4 className="font-semibold mb-2 flex items-center gap-2">
              <Target className="h-4 w-4" />
              Recommendations
            </h4>
            <ul className="space-y-1">
              {recommendations.map((rec, index) => (
                <li key={index} className="text-sm text-muted-foreground flex items-start gap-2">
                  <Zap className="h-3 w-3 mt-1 text-blue-500 flex-shrink-0" />
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI-Powered Consultant Reports</h1>
          <p className="text-muted-foreground">
            Generate comprehensive reports with real-time data and AI insights
          </p>
        </div>
      </div>

      {/* Report Generation Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Generate AI Report
          </CardTitle>
          <CardDescription>
            Enter a consultant email to generate a comprehensive AI-powered report
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Enter consultant email (e.g., kisshore@company.com)"
                value={consultantEmail}
                onChange={(e) => setConsultantEmail(e.target.value)}
                className="w-full"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    generateConsultantReport();
                  }
                }}
              />
            </div>
            <Button 
              onClick={generateConsultantReport}
              disabled={loading}
              className="px-6"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Search className="mr-2 h-4 w-4" />
                  Generate Report
                </>
              )}
            </Button>
          </div>
          
          {/* Quick Email Suggestions */}
          <div className="flex flex-wrap gap-2">
            <span className="text-sm text-muted-foreground">Quick test:</span>
            {['kisshore@company.com', 'sarah.wilson@example.com', 'john.doe@example.com'].map((email) => (
              <Button
                key={email}
                variant="outline"
                size="sm"
                onClick={() => setConsultantEmail(email)}
                className="text-xs"
              >
                {email}
              </Button>
            ))}
          </div>
          
          {error && (
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">{error}</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Report Display */}
      {consultantReport && (
        <div className="space-y-6">
          {/* Report Header */}
          <Card>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <User className="h-5 w-5" />
                    {(consultantReport.report_data.consultant_overview.name as string) || 'Consultant Report'}
                  </CardTitle>
                  <CardDescription>
                    Email: {consultantReport.consultant_email} • Generated: {new Date(consultantReport.generated_at).toLocaleString()}
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => exportReport('json')}
                  >
                    <Download className="mr-2 h-4 w-4" />
                    JSON
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => exportReport('csv')}
                  >
                    <FileText className="mr-2 h-4 w-4" />
                    CSV
                  </Button>
                </div>
              </div>
            </CardHeader>
          </Card>

          {/* Report Content */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Skills Analysis */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Skills Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                {renderSkillsAnalysis(consultantReport.report_data.skills_analysis)}
              </CardContent>
            </Card>

            {/* Performance Metrics */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Performance Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                {renderPerformanceMetrics(consultantReport.report_data.performance_metrics)}
              </CardContent>
            </Card>

            {/* AI Insights */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="text-lg">AI Insights & Recommendations</CardTitle>
              </CardHeader>
              <CardContent>
                {renderAIInsights(consultantReport.report_data.ai_insights)}
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="text-lg">Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-muted/50 rounded-lg">
                    <div className="text-2xl font-bold text-primary">
                      {(consultantReport.real_time_data.current_skills_count as number) || 0}
                    </div>
                    <div className="text-sm text-muted-foreground">Current Skills</div>
                  </div>
                  <div className="text-center p-4 bg-muted/50 rounded-lg">
                    <div className="text-2xl font-bold text-primary">
                      {(consultantReport.real_time_data.recent_applications_count as number) || 0}
                    </div>
                    <div className="text-sm text-muted-foreground">Recent Applications</div>
                  </div>
                  <div className="text-center p-4 bg-muted/50 rounded-lg">
                    <div className="text-2xl font-bold text-primary">
                      {(consultantReport.real_time_data.has_recent_resume as boolean) ? 'Yes' : 'No'}
                    </div>
                    <div className="text-sm text-muted-foreground">Recent Resume</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
