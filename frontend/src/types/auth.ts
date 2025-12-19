/**
 * Authentication types for NeuroVet
 */

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  clinic_name?: string;
  order_number?: string;
  specialty?: string;
  is_student: boolean;
  school_name?: string;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  clinic_name?: string;
  order_number?: string;
  specialty?: string;
  is_student?: boolean;
  school_name?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface UpdateProfileData {
  first_name?: string;
  last_name?: string;
  clinic_name?: string;
  order_number?: string;
  specialty?: string;
  is_student?: boolean;
  school_name?: string;
}

export interface VerifyEmailResponse {
  verified: boolean;
  message: string;
}
