import axios from 'axios';
import { ChatRequest, ChatResponse, SessionResponse } from '../types/api';

// Use relative URLs to leverage the proxy configuration in package.json
const API_BASE_URL = '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Deduplication mechanism for session creation
let pendingSessionRequest: Promise<string> | null = null;
let currentSessionId: string | null = null;

export const apiService = {
  async createSession(): Promise<string> {
    // If we already have a session, return it
    if (currentSessionId) {
      console.log('Returning existing session:', currentSessionId);
      return currentSessionId;
    }
    
    // If there's already a pending request, return the same promise
    if (pendingSessionRequest) {
      console.log('Returning existing session request promise');
      return pendingSessionRequest;
    }
    
    console.log('Creating new session request');
    pendingSessionRequest = api.post<SessionResponse>('/sessions')
      .then(response => {
        const sessionId = response.data.id;
        console.log('Session created successfully:', sessionId);
        currentSessionId = sessionId;
        pendingSessionRequest = null; // Clear the pending request
        return sessionId;
      })
      .catch(error => {
        console.error('Session creation failed:', error);
        pendingSessionRequest = null; // Clear the pending request on error
        throw error;
      });
    
    return pendingSessionRequest;
  },

  async sendMessage(sessionId: string, message: string): Promise<ChatResponse> {
    const request: ChatRequest = { message };
    const response = await api.post<ChatResponse>(`/sessions/${sessionId}/messages`, request);
    return response.data;
  },

  async getSession(sessionId: string) {
    const response = await api.get(`/sessions/${sessionId}`);
    return response.data;
  },

  async getSessionBySlug(slug: string) {
    const response = await api.get(`/sessions/slug/${slug}`);
    return response.data;
  },

  async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  },

  // Reset session state (useful for testing or manual session reset)
  resetSession() {
    console.log('Resetting session state');
    currentSessionId = null;
    pendingSessionRequest = null;
  },
};