import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import DelegationsList from '../pages/DelegationsList';
import { delegationAPI } from '../services/api';
import type { Delegation, DelegationsResponse } from '../types';

// Mock the API
vi.mock('../services/api', () => ({
  delegationAPI: {
    list: vi.fn(),
    approve: vi.fn(),
    deny: vi.fn(),
    revoke: vi.fn(),
  },
}));

const mockDelegationAPI = vi.mocked(delegationAPI);

const createMockDelegation = (overrides: Partial<Delegation> = {}): Delegation => ({
  id: '1',
  agentId: 'agent-1',
  agentName: 'Test Agent',
  userId: 'user-1',
  scopes: ['read', 'write'],
  status: 'pending',
  createdAt: '2024-01-01T00:00:00Z',
  expiresAt: '2024-01-02T00:00:00Z',
  ...overrides,
});

const createMockResponse = (delegations: Delegation[]): DelegationsResponse => ({
  delegations,
  items: delegations,
  total: delegations.length,
  timestamp: '2024-01-01T00:00:00Z',
});

describe('DelegationsList', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders delegation management interface', async () => {
    const mockDelegations = [
      createMockDelegation({ id: '1', agentName: 'Agent 1', status: 'pending' }),
      createMockDelegation({ id: '2', agentName: 'Agent 2', status: 'approved' }),
    ];

    mockDelegationAPI.list.mockResolvedValue(createMockResponse(mockDelegations));

    render(<DelegationsList />);

    expect(screen.getByText('Delegation Management')).toBeInTheDocument();
    expect(screen.getByText('Manage agent delegation requests and monitor active delegations')).toBeInTheDocument();
    
    // Check tabs are present
    expect(screen.getByText('Pending Queue')).toBeInTheDocument();
    expect(screen.getByText('Active Delegations')).toBeInTheDocument();
    expect(screen.getByText('History')).toBeInTheDocument();
  });

  it('displays pending delegations by default', async () => {
    const mockDelegations = [
      createMockDelegation({ id: '1', agentName: 'Pending Agent', status: 'pending' }),
      createMockDelegation({ id: '2', agentName: 'Active Agent', status: 'approved' }),
    ];

    mockDelegationAPI.list.mockResolvedValue(createMockResponse(mockDelegations));

    render(<DelegationsList />);

    await waitFor(() => {
      expect(screen.getByText('Pending Agent')).toBeInTheDocument();
    });

    // Should not show active agent in pending tab
    expect(screen.queryByText('Active Agent')).not.toBeInTheDocument();
  });

  it('switches between tabs correctly', async () => {
    const mockDelegations = [
      createMockDelegation({ id: '1', agentName: 'Pending Agent', status: 'pending' }),
      createMockDelegation({ id: '2', agentName: 'Active Agent', status: 'approved' }),
      createMockDelegation({ id: '3', agentName: 'Denied Agent', status: 'denied' }),
    ];

    mockDelegationAPI.list.mockResolvedValue(createMockResponse(mockDelegations));

    render(<DelegationsList />);

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Pending Agent')).toBeInTheDocument();
    });

    // Switch to active tab
    fireEvent.click(screen.getByText('Active Delegations'));
    await waitFor(() => {
      expect(screen.getByText('Active Agent')).toBeInTheDocument();
    });
    expect(screen.queryByText('Pending Agent')).not.toBeInTheDocument();

    // Switch to history tab
    fireEvent.click(screen.getByText('History'));
    await waitFor(() => {
      expect(screen.getByText('Denied Agent')).toBeInTheDocument();
    });
    expect(screen.queryByText('Active Agent')).not.toBeInTheDocument();
  });

  it('displays tab counts correctly', async () => {
    const mockDelegations = [
      createMockDelegation({ id: '1', status: 'pending' }),
      createMockDelegation({ id: '2', status: 'pending' }),
      createMockDelegation({ id: '3', status: 'approved' }),
      createMockDelegation({ id: '4', status: 'denied' }),
    ];

    mockDelegationAPI.list.mockResolvedValue(createMockResponse(mockDelegations));

    render(<DelegationsList />);

    await waitFor(() => {
      // Check badge counts
      expect(screen.getByText('2')).toBeInTheDocument(); // Pending count
      expect(screen.getByText('1')).toBeInTheDocument(); // Active and History counts
    });
  });

  it('handles approve delegation', async () => {
    const mockDelegation = createMockDelegation({ id: '1', status: 'pending' });
    mockDelegationAPI.list.mockResolvedValue(createMockResponse([mockDelegation]));
    mockDelegationAPI.approve.mockResolvedValue({
      message: 'Approved',
      delegation: { ...mockDelegation, status: 'approved' },
      delegation_token: 'token123',
    });

    render(<DelegationsList />);

    await waitFor(() => {
      expect(screen.getByText('Test Agent')).toBeInTheDocument();
    });

    const approveButton = screen.getByText('Approve');
    fireEvent.click(approveButton);

    await waitFor(() => {
      expect(mockDelegationAPI.approve).toHaveBeenCalledWith('1');
    });
  });

  it('handles deny delegation', async () => {
    const mockDelegation = createMockDelegation({ id: '1', status: 'pending' });
    mockDelegationAPI.list.mockResolvedValue(createMockResponse([mockDelegation]));
    mockDelegationAPI.deny.mockResolvedValue({
      message: 'Denied',
      delegation: { ...mockDelegation, status: 'denied' },
    });

    render(<DelegationsList />);

    await waitFor(() => {
      expect(screen.getByText('Test Agent')).toBeInTheDocument();
    });

    const denyButton = screen.getByText('Deny');
    fireEvent.click(denyButton);

    await waitFor(() => {
      expect(mockDelegationAPI.deny).toHaveBeenCalledWith('1');
    });
  });

  it('handles revoke delegation', async () => {
    const mockDelegation = createMockDelegation({ id: '1', status: 'approved' });
    mockDelegationAPI.list.mockResolvedValue(createMockResponse([mockDelegation]));
    mockDelegationAPI.revoke.mockResolvedValue({ message: 'Revoked' });

    render(<DelegationsList />);

    // Switch to active tab to see revoke button
    fireEvent.click(screen.getByText('Active Delegations'));

    await waitFor(() => {
      expect(screen.getByText('Test Agent')).toBeInTheDocument();
    });

    const revokeButton = screen.getByText('Revoke');
    fireEvent.click(revokeButton);

    await waitFor(() => {
      expect(mockDelegationAPI.revoke).toHaveBeenCalledWith('1');
    });
  });

  it('displays empty state when no delegations', async () => {
    mockDelegationAPI.list.mockResolvedValue(createMockResponse([]));

    render(<DelegationsList />);

    await waitFor(() => {
      expect(screen.getByText('No Pending Delegations')).toBeInTheDocument();
      expect(screen.getByText('All delegation requests have been processed.')).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    mockDelegationAPI.list.mockRejectedValue(new Error('API Error'));

    render(<DelegationsList />);

    await waitFor(() => {
      expect(screen.getByText('Failed to load delegations. Please try again.')).toBeInTheDocument();
    });

    // Should show retry button
    expect(screen.getByText('Retry')).toBeInTheDocument();
  });

  it('refreshes data when refresh button is clicked', async () => {
    mockDelegationAPI.list.mockResolvedValue(createMockResponse([]));

    render(<DelegationsList />);

    await waitFor(() => {
      expect(mockDelegationAPI.list).toHaveBeenCalledTimes(1);
    });

    const refreshButton = screen.getByText('Refresh');
    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(mockDelegationAPI.list).toHaveBeenCalledTimes(2);
    });
  });

  it('opens delegation detail modal when view details is clicked', async () => {
    const mockDelegation = createMockDelegation({ id: '1', agentName: 'Test Agent' });
    mockDelegationAPI.list.mockResolvedValue(createMockResponse([mockDelegation]));

    render(<DelegationsList />);

    await waitFor(() => {
      expect(screen.getByText('Test Agent')).toBeInTheDocument();
    });

    const viewDetailsButton = screen.getByText('View Details');
    fireEvent.click(viewDetailsButton);

    await waitFor(() => {
      expect(screen.getByText('Delegation Details')).toBeInTheDocument();
    });
  });
});
