import type { Site, SitePayload } from './types';

const API_BASE = '/api/v1';
const TOKEN_KEY = 'auth_token';

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

function getAuthHeaders(): HeadersInit {
  const token = getToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE}/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });
  if (!response.ok) {
    throw new Error('Login failed');
  }
  const data = await response.json();
  setToken(data.access_token);
  return data;
}

export async function listSites(): Promise<Site[]> {
  const response = await fetch(`${API_BASE}/sites`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    if (response.status === 401) {
      clearToken();
      throw new Error('Unauthorized');
    }
    throw new Error('Failed to fetch sites');
  }
  return response.json();
}

export async function getSite(id: string): Promise<Site> {
  const response = await fetch(`${API_BASE}/sites/${id}`, {
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    if (response.status === 401) {
      clearToken();
      throw new Error('Unauthorized');
    }
    throw new Error('Failed to fetch site');
  }
  return response.json();
}

export async function createSite(payload: SitePayload): Promise<Site> {
  const response = await fetch(`${API_BASE}/sites`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    if (response.status === 401) {
      clearToken();
      throw new Error('Unauthorized');
    }
    throw new Error('Failed to create site');
  }
  return response.json();
}

export async function updateSite(id: string, payload: SitePayload): Promise<Site> {
  const response = await fetch(`${API_BASE}/sites/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    if (response.status === 401) {
      clearToken();
      throw new Error('Unauthorized');
    }
    throw new Error('Failed to update site');
  }
  return response.json();
}

export async function deleteSite(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/sites/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    if (response.status === 401) {
      clearToken();
      throw new Error('Unauthorized');
    }
    throw new Error('Failed to delete site');
  }
}

export async function retryCert(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/sites/${id}/cert`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  if (!response.ok) {
    if (response.status === 401) {
      clearToken();
      throw new Error('Unauthorized');
    }
    throw new Error('Failed to retry certificate');
  }
}