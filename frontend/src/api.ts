import type { Site, SitePayload } from './types';

const API_BASE = '/api/v1';

export async function listSites(): Promise<Site[]> {
  const response = await fetch(`${API_BASE}/sites`);
  if (!response.ok) {
    throw new Error('Failed to fetch sites');
  }
  return response.json();
}

export async function getSite(id: string): Promise<Site> {
  const response = await fetch(`${API_BASE}/sites/${id}`);
  if (!response.ok) {
    throw new Error('Failed to fetch site');
  }
  return response.json();
}

export async function createSite(payload: SitePayload): Promise<Site> {
  const response = await fetch(`${API_BASE}/sites`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error('Failed to create site');
  }
  return response.json();
}

export async function updateSite(id: string, payload: SitePayload): Promise<Site> {
  const response = await fetch(`${API_BASE}/sites/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error('Failed to update site');
  }
  return response.json();
}

export async function deleteSite(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/sites/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error('Failed to delete site');
  }
}

export async function retryCert(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/sites/${id}/cert`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error('Failed to retry certificate');
  }
}