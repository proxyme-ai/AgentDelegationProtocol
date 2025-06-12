import { vi } from 'vitest';

describe('fetchJSON', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('appends base url', async () => {
    vi.stubEnv('VITE_API_BASE_URL', 'https://api.test');
    const { fetchJSON } = await import('../services/api');
    (fetch as any).mockResolvedValue({ ok: true, json: () => Promise.resolve({}) });
    await fetchJSON('/foo');
    expect(fetch).toHaveBeenCalledWith('https://api.test/foo', undefined);
    vi.unstubAllEnvs();
  });

  it('throws on error response', async () => {
    const { fetchJSON } = await import('../services/api');
    (fetch as any).mockResolvedValue({ ok: false, text: () => Promise.resolve('err') });
    await expect(fetchJSON('/bad')).rejects.toThrow('err');
  });
});
