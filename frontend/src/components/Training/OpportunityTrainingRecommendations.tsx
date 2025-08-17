import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, GraduationCap, ExternalLink, DollarSign, Clock } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

interface TrainingRecommendation {
  id: string;
  title: string;
  skill: string;
  skills_covered: string[];
  provider: string;
  duration_hours: number;
  difficulty: string;
  cost: number;
  certification: boolean;
  certification_name: string;
  market_demand: number;
  career_impact: string;
  rating: number;
  url: string;
  recommendation_score: number;
  estimated_roi: string;
  reason: string;
  related_opportunities: Array<{id: number, title: string, company: string}>;
  opportunities_count: number;
  priority: string;
  ai_generated: boolean;
  recommendation_reason: string;
}

interface OpportunityTrainingResponse {
  success: boolean;
  consultant_id: number;
  consultant_name: string;
  missing_skills: string[];
  training_recommendations: TrainingRecommendation[];
  opportunities_analyzed: number;
  ai_powered: boolean;
  total_recommendations: number;
  high_priority_count: number;
}

interface OpportunityTrainingRecommendationsProps {
  consultantId: number;
}

export function OpportunityTrainingRecommendations({ consultantId }: OpportunityTrainingRecommendationsProps) {
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<OpportunityTrainingResponse | null>(null);
  const [missingSkills, setMissingSkills] = useState<string>('');
  const [experienceLevel, setExperienceLevel] = useState<string>('intermediate');

  const handleGetRecommendations = async () => {
    if (!missingSkills.trim()) return;

    try {
      setLoading(true);
      const skillsArray = missingSkills.split(',').map(s => s.trim()).filter(s => s);
      
      const response = await fetch(`${API_BASE_URL}/api/consultant/${consultantId}/opportunity-training-recommendations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          missing_skills: skillsArray,
          experience_level: experienceLevel,
          include_ai_recommendations: true
        })
      });

      if (response.ok) {
        const data: OpportunityTrainingResponse = await response.json();
        setRecommendations(data);
      } else {
        console.error('Failed to get training recommendations');
      }
    } catch (error) {
      console.error('Error getting training recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <GraduationCap className="h-5 w-5 text-primary" />
          AI-Powered Training Recommendations
        </CardTitle>
        <CardDescription>
          Get personalized training recommendations based on missing skills and market opportunities
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="missing-skills">Missing Skills (comma-separated)</Label>
            <Input
              id="missing-skills"
              placeholder="e.g., React, Node.js, TypeScript"
              value={missingSkills}
              onChange={(e) => setMissingSkills(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="experience-level">Experience Level</Label>
            <Select value={experienceLevel} onValueChange={setExperienceLevel}>
              <SelectTrigger id="experience-level">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="beginner">Beginner</SelectItem>
                <SelectItem value="intermediate">Intermediate</SelectItem>
                <SelectItem value="advanced">Advanced</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <Button 
          onClick={handleGetRecommendations} 
          disabled={loading || !missingSkills.trim()}
          className="w-full"
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Getting AI Recommendations...
            </>
          ) : (
            'Get Training Recommendations'
          )}
        </Button>

        {recommendations && (
          <div className="space-y-4 mt-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">
                {recommendations.total_recommendations} Recommendations Found
              </h3>
              {recommendations.ai_powered && (
                <Badge variant="outline" className="text-primary">
                  AI-Powered
                </Badge>
              )}
            </div>

            <div className="grid gap-4">
              {recommendations.training_recommendations.map((rec, index) => (
                <Card key={rec.id || index} className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h4 className="font-semibold text-lg">{rec.title}</h4>
                      <p className="text-sm text-muted-foreground">{rec.provider}</p>
                    </div>
                    <Badge 
                      variant={rec.priority === 'High' ? 'destructive' : 'default'}
                    >
                      {rec.priority} Priority
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3 text-sm">
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span>{rec.duration_hours}h</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <DollarSign className="h-4 w-4 text-muted-foreground" />
                      <span>{rec.cost === 0 ? 'Free' : `$${rec.cost}`}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Rating: </span>
                      <span className="font-medium">{rec.rating}/5</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">ROI: </span>
                      <span className="font-medium">{rec.estimated_roi}</span>
                    </div>
                  </div>

                  <div className="mb-3">
                    <p className="text-sm text-muted-foreground mb-2">Skills Covered:</p>
                    <div className="flex flex-wrap gap-1">
                      {rec.skills_covered.map((skill, idx) => (
                        <Badge key={idx} variant="secondary" className="text-xs">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <p className="text-sm text-muted-foreground mb-3">{rec.reason}</p>

                  {rec.related_opportunities.length > 0 && (
                    <div className="mb-3">
                      <p className="text-xs text-muted-foreground mb-1">Related Opportunities:</p>
                      <div className="text-xs">
                        {rec.related_opportunities.map((opp, idx) => (
                          <span key={idx} className="mr-2">
                            {opp.title} ({opp.company})
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex gap-2">
                    {rec.url && (
                      <Button variant="outline" size="sm" asChild>
                        <a href={rec.url} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="h-4 w-4 mr-1" />
                          View Course
                        </a>
                      </Button>
                    )}
                    <Button size="sm">
                      Start Learning
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
