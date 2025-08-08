import { ReactNode } from "react";

// Mock opportunity data
export interface Opportunity {
  startDate: ReactNode;
  endDate: any;
  id: string;
  title: string;
  description: string;
  consultantEmail: string;
  status: 'pending' | 'accepted' | 'declined';
}

export let opportunities: Opportunity[] = [];

// Add opportunity
export const addOpportunity = (opportunity: Opportunity) => {
  opportunities.push(opportunity);
  // Save to localStorage for persistence
  localStorage.setItem('opportunities', JSON.stringify(opportunities));
};

// Update status (accept/decline)
export const updateOpportunityStatus = (id: string, status: 'accepted' | 'declined') => {
  const opp = opportunities.find(o => o.id === id);
  if (opp) {
    opp.status = status;
    localStorage.setItem('opportunities', JSON.stringify(opportunities));
  }
};

// Get opportunities by consultant
export const getOpportunitiesForConsultant = (email: string) => {
  return opportunities.filter(o => o.consultantEmail === email);
};

// Load opportunities from localStorage
export const loadOpportunities = () => {
  const stored = localStorage.getItem('opportunities');
  if (stored) {
    opportunities.length = 0; // Clear current array
    opportunities.push(...JSON.parse(stored));
  }
};
