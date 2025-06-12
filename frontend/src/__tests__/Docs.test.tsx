import { vi } from "vitest";
import { render, screen } from '@testing-library/react';
import Docs from '../pages/Docs';

describe('Docs', () => {
  it('displays markdown from docs.md', async () => {
    vi.stubGlobal('fetch', vi.fn(() => Promise.resolve({
      text: () => Promise.resolve('# Hello')
    })) as any);
    render(<Docs />);
    await screen.findByText('Hello');
    vi.restoreAllMocks();
  });
});
