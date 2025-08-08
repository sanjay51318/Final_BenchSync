#!/usr/bin/env python3
"""
Professional Opportunity Agent MCP Server
Handles AI-powered opportunity matching and recommendations with advanced ML capabilities
"""
import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional
import traceback

# Set environment variables before importing AI libraries
os.environ["TRANSFORMERS_BACKEND"] = "pt"
os.environ["USE_TF"] = "0"
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# MCP imports
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    CallToolRequest,
    ListToolsRequest,
    Tool,
    TextContent,
    CallToolResult,
    ListToolsResult,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("opportunity-agent-server")

# AI/ML dependencies with fallback
HAS_AI_CAPABILITIES = False
try:
    import numpy as np
    from transformers import pipeline, AutoTokenizer, AutoModel
    from sentence_transformers import SentenceTransformer
    import sklearn
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_AI_CAPABILITIES = True
    logger.info("✅ AI capabilities loaded successfully")
except Exception as e:
    logger.warning(f"⚠️ AI capabilities not available: {str(e)}")
    HAS_AI_CAPABILITIES = False

class OpportunityAgentMCP:
    """Professional Opportunity Agent with AI-powered matching"""
    
    def __init__(self):
        self.has_ai = HAS_AI_CAPABILITIES
        self.similarity_model = None
        self.skill_matcher = None
        self.text_classifier = None
        
        # Skill categories and mappings
        self.skill_categories = {
            'frontend': ['react', 'angular', 'vue', 'html', 'css', 'javascript', 'typescript', 'bootstrap', 'tailwind'],
            'backend': ['python', 'java', 'node.js', 'django', 'flask', 'spring', 'express', 'fastapi', 'php'],
            'database': ['sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'cassandra'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible'],
            'data_science': ['pandas', 'numpy', 'tensorflow', 'pytorch', 'sklearn', 'tableau', 'powerbi'],
            'mobile': ['react native', 'flutter', 'ios', 'android', 'swift', 'kotlin', 'xamarin'],
            'devops': ['ci/cd', 'jenkins', 'gitlab', 'github actions', 'docker', 'kubernetes', 'monitoring']
        }
        
        if self.has_ai:
            try:
                self._initialize_ai_models()
            except Exception as e:
                logger.warning(f"AI model initialization failed: {str(e)}")
                self.has_ai = False
    
    def _initialize_ai_models(self):
        """Initialize AI models with error handling"""
        try:
            # Initialize similarity model for semantic matching
            self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize text classifier for opportunity categorization
            self.text_classifier = pipeline(
                "text-classification",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            
            logger.info("✅ Opportunity Agent AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ AI model initialization failed: {str(e)}")
            raise e
    
    def match_consultant_to_opportunities(self, consultant_skills: List[str], opportunities: List[Dict]) -> List[Dict]:
        """Match consultant skills to available opportunities"""
        if not opportunities:
            return []
        
        matched_opportunities = []
        
        for opportunity in opportunities:
            match_result = self._calculate_opportunity_match(consultant_skills, opportunity)
            if match_result['match_score'] > 0.2:  # Minimum threshold
                matched_opportunities.append(match_result)
        
        # Sort by match score descending
        matched_opportunities.sort(key=lambda x: x['match_score'], reverse=True)
        return matched_opportunities[:10]  # Return top 10 matches
    
    def _calculate_opportunity_match(self, consultant_skills: List[str], opportunity: Dict) -> Dict:
        """Calculate match score between consultant skills and opportunity requirements"""
        required_skills = opportunity.get('required_skills', [])
        opportunity_description = opportunity.get('description', '')
        
        if self.has_ai and self.similarity_model:
            return self._calculate_ai_match(consultant_skills, opportunity, required_skills, opportunity_description)
        else:
            return self._calculate_basic_match(consultant_skills, opportunity, required_skills)
    
    def _calculate_ai_match(self, consultant_skills: List[str], opportunity: Dict, required_skills: List[str], description: str) -> Dict:
        """AI-powered matching using semantic similarity"""
        try:
            # Encode consultant skills and required skills
            consultant_text = " ".join(consultant_skills).lower()
            required_text = " ".join(required_skills).lower()
            full_opportunity_text = f"{required_text} {description}".lower()
            
            # Calculate semantic similarity
            consultant_embedding = self.similarity_model.encode([consultant_text])
            opportunity_embedding = self.similarity_model.encode([full_opportunity_text])
            
            similarity_score = cosine_similarity(consultant_embedding, opportunity_embedding)[0][0]
            
            # Calculate skill overlap
            consultant_skills_lower = [skill.lower() for skill in consultant_skills]
            required_skills_lower = [skill.lower() for skill in required_skills]
            
            matched_skills = list(set(consultant_skills_lower) & set(required_skills_lower))
            skill_coverage = len(matched_skills) / max(len(required_skills_lower), 1)
            
            # Combine semantic similarity and skill coverage
            match_score = (similarity_score * 0.6) + (skill_coverage * 0.4)
            
            # Analyze strengths and gaps
            strengths = matched_skills
            gaps = [skill for skill in required_skills_lower if skill not in consultant_skills_lower]
            
            # Generate AI reasoning
            reasoning = self._generate_match_reasoning(match_score, len(matched_skills), len(required_skills), similarity_score)
            
            return {
                'opportunity': opportunity,
                'match_score': min(1.0, match_score),
                'match_reasoning': reasoning,
                'strengths': strengths,
                'potential_gaps': gaps,
                'skill_coverage': skill_coverage,
                'semantic_similarity': similarity_score,
                'analysis_method': 'AI-Enhanced'
            }
            
        except Exception as e:
            logger.warning(f"AI matching failed, falling back to basic: {str(e)}")
            return self._calculate_basic_match(consultant_skills, opportunity, required_skills)
    
    def _calculate_basic_match(self, consultant_skills: List[str], opportunity: Dict, required_skills: List[str]) -> Dict:
        """Basic pattern-based matching"""
        consultant_skills_lower = [skill.lower() for skill in consultant_skills]
        required_skills_lower = [skill.lower() for skill in required_skills]
        
        # Direct skill matching
        matched_skills = list(set(consultant_skills_lower) & set(required_skills_lower))
        
        # Category-based matching
        category_matches = 0
        for category, category_skills in self.skill_categories.items():
            consultant_in_category = any(skill in consultant_skills_lower for skill in category_skills)
            required_in_category = any(skill in required_skills_lower for skill in category_skills)
            if consultant_in_category and required_in_category:
                category_matches += 1
        
        # Calculate match score
        direct_match_score = len(matched_skills) / max(len(required_skills_lower), 1)
        category_match_score = category_matches / max(len(self.skill_categories), 1)
        
        match_score = (direct_match_score * 0.7) + (category_match_score * 0.3)
        
        gaps = [skill for skill in required_skills_lower if skill not in consultant_skills_lower]
        reasoning = f"Found {len(matched_skills)} direct skill matches out of {len(required_skills_lower)} required skills."
        
        return {
            'opportunity': opportunity,
            'match_score': min(1.0, match_score),
            'match_reasoning': reasoning,
            'strengths': matched_skills,
            'potential_gaps': gaps,
            'skill_coverage': direct_match_score,
            'analysis_method': 'Pattern-Based'
        }
    
    def _generate_match_reasoning(self, match_score: float, matched_count: int, required_count: int, semantic_score: float) -> str:
        """Generate human-readable reasoning for the match"""
        if match_score >= 0.8:
            return f"Excellent match! {matched_count}/{required_count} required skills matched with high semantic similarity ({semantic_score:.2f})."
        elif match_score >= 0.6:
            return f"Good match with {matched_count}/{required_count} skills aligned and moderate semantic fit ({semantic_score:.2f})."
        elif match_score >= 0.4:
            return f"Partial match with {matched_count}/{required_count} direct skills but some potential through related experience."
        else:
            return f"Limited match with {matched_count}/{required_count} skills. May require additional training or skills development."
    
    def recommend_skill_development(self, consultant_skills: List[str], target_opportunities: List[Dict]) -> Dict:
        """Recommend skills to develop based on opportunity gaps"""
        all_required_skills = []
        consultant_skills_lower = [skill.lower() for skill in consultant_skills]
        
        # Collect all required skills from target opportunities
        for opp in target_opportunities:
            required_skills = opp.get('required_skills', [])
            all_required_skills.extend([skill.lower() for skill in required_skills])
        
        # Find skill gaps
        skill_frequency = {}
        for skill in all_required_skills:
            if skill not in consultant_skills_lower:
                skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
        
        # Sort by frequency (most in-demand first)
        recommended_skills = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Categorize recommendations
        recommendations = {
            'high_priority': [skill for skill, freq in recommended_skills[:3]],
            'medium_priority': [skill for skill, freq in recommended_skills[3:6]],
            'low_priority': [skill for skill, freq in recommended_skills[6:]],
            'skill_frequency': dict(recommended_skills),
            'total_opportunities': len(target_opportunities)
        }
        
        return recommendations
    
    def analyze_market_trends(self, opportunities: List[Dict]) -> Dict:
        """Analyze market trends from available opportunities"""
        if not opportunities:
            return {'error': 'No opportunities to analyze'}
        
        skill_demand = {}
        experience_levels = []
        project_types = []
        
        for opp in opportunities:
            # Analyze skill demand
            for skill in opp.get('required_skills', []):
                skill_lower = skill.lower()
                skill_demand[skill_lower] = skill_demand.get(skill_lower, 0) + 1
            
            # Analyze experience requirements
            exp_level = opp.get('experience_level', 'unknown')
            experience_levels.append(exp_level)
            
            # Analyze project types (from title/description)
            title = opp.get('title', '').lower()
            if 'frontend' in title or 'ui' in title or 'react' in title:
                project_types.append('Frontend Development')
            elif 'backend' in title or 'api' in title or 'server' in title:
                project_types.append('Backend Development')
            elif 'fullstack' in title or 'full stack' in title:
                project_types.append('Full Stack Development')
            elif 'devops' in title or 'cloud' in title:
                project_types.append('DevOps/Cloud')
            elif 'data' in title or 'analytics' in title:
                project_types.append('Data Science')
            else:
                project_types.append('Other')
        
        # Get top skills
        top_skills = sorted(skill_demand.items(), key=lambda x: x[1], reverse=True)[:15]
        
        return {
            'total_opportunities': len(opportunities),
            'top_skills_in_demand': dict(top_skills),
            'experience_distribution': {level: experience_levels.count(level) for level in set(experience_levels)},
            'project_type_distribution': {ptype: project_types.count(ptype) for ptype in set(project_types)},
            'market_insights': self._generate_market_insights(top_skills, project_types)
        }
    
    def _generate_market_insights(self, top_skills: List, project_types: List) -> List[str]:
        """Generate actionable market insights"""
        insights = []
        
        if top_skills:
            top_skill = top_skills[0][0]
            insights.append(f"'{top_skill}' is the most in-demand skill in current opportunities.")
        
        if 'Frontend Development' in project_types and project_types.count('Frontend Development') > len(project_types) * 0.3:
            insights.append("Frontend development roles are particularly abundant in the current market.")
        
        if 'DevOps/Cloud' in project_types:
            insights.append("Cloud and DevOps expertise continues to be highly valued.")
        
        if any('react' in skill[0] for skill in top_skills[:5]):
            insights.append("React skills are consistently in high demand across multiple opportunities.")
        
        if not insights:
            insights.append("Market analysis shows diverse opportunities across multiple technology stacks.")
        
        return insights

# Initialize the opportunity agent
opportunity_agent = OpportunityAgentMCP()

# MCP Server setup
server = Server("opportunity-agent-server")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools"""
    return ListToolsResult(
        tools=[
            Tool(
                name="match_opportunities",
                description="Match consultant skills to available opportunities using AI-powered analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "consultant_skills": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of consultant skills"
                        },
                        "opportunities": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "List of available opportunities"
                        }
                    },
                    "required": ["consultant_skills", "opportunities"]
                }
            ),
            Tool(
                name="recommend_skills",
                description="Recommend skills for development based on market opportunities",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "consultant_skills": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Current consultant skills"
                        },
                        "target_opportunities": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Target opportunities for analysis"
                        }
                    },
                    "required": ["consultant_skills", "target_opportunities"]
                }
            ),
            Tool(
                name="analyze_market",
                description="Analyze market trends from available opportunities",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "opportunities": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "List of opportunities to analyze"
                        }
                    },
                    "required": ["opportunities"]
                }
            ),
            Tool(
                name="get_capabilities",
                description="Get current AI capabilities and status",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        ]
    )

@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls"""
    
    try:
        if request.name == "match_opportunities":
            consultant_skills = request.arguments.get("consultant_skills", [])
            opportunities = request.arguments.get("opportunities", [])
            
            if not consultant_skills:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps({
                                "error": "Consultant skills are required",
                                "success": False
                            })
                        )
                    ]
                )
            
            matches = opportunity_agent.match_consultant_to_opportunities(consultant_skills, opportunities)
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "matches": matches,
                            "total_matches": len(matches),
                            "analysis_method": opportunity_agent.has_ai and "AI-Enhanced" or "Pattern-Based",
                            "success": True
                        }, indent=2)
                    )
                ]
            )
        
        elif request.name == "recommend_skills":
            consultant_skills = request.arguments.get("consultant_skills", [])
            target_opportunities = request.arguments.get("target_opportunities", [])
            
            recommendations = opportunity_agent.recommend_skill_development(consultant_skills, target_opportunities)
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "recommendations": recommendations,
                            "success": True
                        }, indent=2)
                    )
                ]
            )
        
        elif request.name == "analyze_market":
            opportunities = request.arguments.get("opportunities", [])
            
            analysis = opportunity_agent.analyze_market_trends(opportunities)
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "market_analysis": analysis,
                            "success": True
                        }, indent=2)
                    )
                ]
            )
        
        elif request.name == "get_capabilities":
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "has_ai_capabilities": opportunity_agent.has_ai,
                            "available_models": {
                                "similarity_model": opportunity_agent.similarity_model is not None,
                                "text_classifier": opportunity_agent.text_classifier is not None
                            },
                            "supported_features": [
                                "AI-powered semantic matching",
                                "Skill gap analysis",
                                "Market trend analysis",
                                "Skill development recommendations"
                            ],
                            "skill_categories": len(opportunity_agent.skill_categories),
                            "status": "ready"
                        })
                    )
                ]
            )
        
        else:
            raise ValueError(f"Unknown tool: {request.name}")
            
    except Exception as e:
        logger.error(f"Tool execution failed: {str(e)}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps({
                        "error": f"Tool execution failed: {str(e)}",
                        "success": False,
                        "traceback": traceback.format_exc()
                    })
                )
            ]
        )

async def main():
    """Main server function"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as streams:
        await server.run(
            streams[0],
            streams[1],
            InitializationOptions(
                server_name="opportunity-agent",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
