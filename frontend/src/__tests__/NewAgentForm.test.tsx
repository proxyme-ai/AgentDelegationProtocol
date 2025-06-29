import { vi } from "vitest";
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import NewAgentForm from '../pages/NewAgentForm';
import * as api from '../services/api';
import type { Agent } from '../types.ts';

vi.mock('../services/api');

describe('NewAgentForm', () => {
  it('validates name', async () => {
    const user = userEvent.setup();
    vi.mocked(api.createAgent).mockResolvedValue({} as unknown as Agent);
    render(<NewAgentForm />);
    await user.click(screen.getByText('Create'));
    expect(screen.getByText('Name required')).toBeInTheDocument();
  });
});
