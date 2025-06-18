import { vi } from "vitest";
import { render, screen } from '@testing-library/react';
import Dashboard from '../pages/Dashboard';
import * as api from '../services/api';

vi.mock('../services/api');

const delegations = [{ id: '1', agent: 'agent1', status: 'pending' }];

vi.mocked(api.getDelegations).mockResolvedValue(delegations);

describe('Dashboard', () => {
  it('renders pending delegations', async () => {
    render(<Dashboard />);
    await screen.findByText('agent1 - pending');
  });
});
