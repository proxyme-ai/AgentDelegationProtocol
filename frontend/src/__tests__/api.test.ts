import { vi } from 'vitest';
import { fetchJSON, BASE_URL } from '../services/api';

describe('fetchJSON', () => {
  it('prefixes requests with BASE_URL', async () => {
    const mockResponse = { ok: true, json: () => Promise.resolve({}) } as Response;
    const fetchSpy = vi.fn().mockResolvedValue(mockResponse);
    // @ts-expect-error - assign mock to global
    global.fetch = fetchSpy;
    await fetchJSON('/demo');
    expect(fetchSpy).toHaveBeenCalledWith(BASE_URL + '/demo', undefined);
  });
});
