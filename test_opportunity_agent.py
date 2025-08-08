#!/usr/bin/env python3
"""
Test script for Opportunity Agent MCP Server
"""
import asyncio
import sys
import os
sys.path.append('.')

from utils.opportunity_agent_interface import OpportunityAgentMCPClient

async def test_opportunity_agent():
    client = OpportunityAgentMCPClient()
    
    # Test capabilities
    print('Testing opportunity agent capabilities...')
    capabilities = await client.get_server_capabilities()
    print(f'Capabilities: {capabilities}')
    
    # Test consultant matching
    print('\nTesting consultant opportunity matching...')
    consultant_skills = ['python', 'react', 'postgresql', 'aws']
    opportunities = [
        {
            'id': 1,
            'title': 'Full Stack Developer',
            'description': 'Build web applications using React and Python',
            'required_skills': ['python', 'react', 'javascript', 'sql'],
            'experience_level': 'mid'
        },
        {
            'id': 2,
            'title': 'DevOps Engineer',
            'description': 'AWS cloud infrastructure and automation',
            'required_skills': ['aws', 'docker', 'kubernetes', 'terraform'],
            'experience_level': 'senior'
        }
    ]
    
    matches = await client.match_consultant_to_opportunities(consultant_skills, opportunities)
    print(f'Matches: {matches}')
    
    if matches.get('success'):
        print(f'✅ Found {matches.get("total_matches", 0)} matches')
        print(f'Analysis method: {matches.get("analysis_method", "Unknown")}')
        
        # Print match details
        for i, match in enumerate(matches.get('matches', [])[:2]):
            print(f"\nMatch {i+1}:")
            print(f"  Opportunity: {match.get('opportunity', {}).get('title', 'Unknown')}")
            print(f"  Match Score: {match.get('match_score', 0):.2f}")
            print(f"  Reasoning: {match.get('match_reasoning', 'No reasoning')}")
            print(f"  Strengths: {match.get('strengths', [])}")
            print(f"  Gaps: {match.get('potential_gaps', [])}")
    else:
        print(f'❌ Matching failed: {matches.get("error", "Unknown")}')

if __name__ == "__main__":
    asyncio.run(test_opportunity_agent())
