import { vi } from "vitest";
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DelegationsList from '../pages/DelegationsList';
import * as api from '../services/api';
import type { Delegation } from '../types.ts';

vi.mock('../services/api');

const delegations = [{ id: '1', agent: 'agent1' }];

vi.mocked(api.getDelegations).mockResolvedValue(delegations);

vi.mocked(api.approveDelegation).mockResolvedValue({} as unknown as Delegation);
vi.mocked(api.denyDelegation).mockResolvedValue({} as unknown as Delegation);

describe('DelegationsList', () => {
  it('calls approve', async () => {
    const user = userEvent.setup();
    render(<DelegationsList />);
    await screen.findByText('agent1');
    await user.click(screen.getByText('Approve'));
    expect(api.approveDelegation).toHaveBeenCalledWith('1');
  });
});
