import { vi } from "vitest";
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DelegationsList from '../pages/DelegationsList';
import * as api from '../services/api';

vi.mock('../services/api');

const delegations = [{ id: '1', agent: 'agent1' }];

(api.getDelegations as any).mockResolvedValue(delegations);

(api.approveDelegation as any).mockResolvedValue({});
(api.denyDelegation as any).mockResolvedValue({});

describe('DelegationsList', () => {
  it('calls approve', async () => {
    const user = userEvent.setup();
    render(<DelegationsList />);
    await screen.findByText('agent1');
    await user.click(screen.getByText('Approve'));
    expect(api.approveDelegation).toHaveBeenCalledWith('1');
  });
});
