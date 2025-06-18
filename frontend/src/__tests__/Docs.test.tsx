import { vi } from "vitest";
import { render, screen } from '@testing-library/react';
import Docs from '../pages/Docs';

describe('Docs', () => {
  it('displays markdown from docs.md', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.resolve({ text: () => Promise.resolve('# Hello') })) as unknown as typeof fetch
    );
    render(<Docs />);
    await screen.findByText('Hello');
    vi.restoreAllMocks();
  });
});
