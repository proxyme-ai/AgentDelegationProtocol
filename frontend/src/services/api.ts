const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(BASE_URL + url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<T>;
}

export function getAgents() {
  return fetchJSON('/agents');
}

export function createAgent(data: Record<string, unknown>) {
  return fetchJSON('/agents', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
}

export function getDelegations() {
  return fetchJSON('/delegations');
}

export function approveDelegation(id: string) {
  return fetchJSON(`/delegations/${id}/approve`, { method: 'POST' });
}

export function denyDelegation(id: string) {
  return fetchJSON(`/delegations/${id}/deny`, { method: 'POST' });
}
