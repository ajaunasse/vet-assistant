/**
 * Authentication Service
 */
import apiClient from './apiClient';
import { TokenManager } from '../utils/TokenManager';
import {
  User,
  RegisterData,
  LoginData,
  TokenResponse,
  UpdateProfileData,
  VerifyEmailResponse,
} from '../types/auth';

export const authService = {
  /**
   * Register a new user
   */
  async register(data: RegisterData): Promise<User> {
    const response = await apiClient.post<User>('/auth/register', data);
    return response.data;
  },

  /**
   * Login with email and password
   */
  async login(data: LoginData): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/auth/login', data);

    // Store tokens
    TokenManager.setTokens(response.data.access_token, response.data.refresh_token);

    return response.data;
  },

  /**
   * Logout (clear tokens)
   */
  async logout(): Promise<void> {
    TokenManager.clearTokens();
  },

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<string> {
    const refreshToken = TokenManager.getRefreshToken();

    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await apiClient.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });

    // Update tokens
    TokenManager.setTokens(response.data.access_token, response.data.refresh_token);

    return response.data.access_token;
  },

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  /**
   * Verify email with token
   */
  async verifyEmail(token: string): Promise<VerifyEmailResponse> {
    const response = await apiClient.get<VerifyEmailResponse>('/auth/verify-email', {
      params: { token },
    });
    return response.data;
  },

  /**
   * Update user profile
   */
  async updateProfile(data: UpdateProfileData): Promise<User> {
    const response = await apiClient.put<User>('/auth/profile', data);
    return response.data;
  },

  /**
   * Resend verification email
   */
  async resendVerification(email: string): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post<{ success: boolean; message: string }>(
      '/auth/resend-verification',
      { email }
    );
    return response.data;
  },

  /**
   * Check if user is authenticated (has tokens)
   */
  isAuthenticated(): boolean {
    return TokenManager.hasTokens();
  },
};
