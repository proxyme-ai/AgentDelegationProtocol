import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import DelegationCard from '../components/DelegationCard';
import { delegationAPI } from '../services/api';
import type { Delegation } from '../types';

// Mock the API
vi.mock('../services/api', () => ({
  delegationAPI: {
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

describe('DelegationCard', () => {
  const mockOnUpdate = vi.fn();
  const mockOnViewDetails = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders delegation information correctly', () => {
    const delegation = createMockDelegation({
      agentName: 'Test Agent',
      agentId: 'agent-123',
      userId: 'user-456',
      scopes: ['read', 'write', 'admin'],
      status: 'pending',
    });

    render(
      <DelegationCard
        delegation={delegation}
        onUpdate={mockOnUpdate}
        onViewDetails={mockOnViewDetails}
      />
    );

    expect(screen.getByText('Test Agent')).toBeInTheDocument();
    expect(screen.getByText('Agent ID: agent-123')).toBeInTheDocument();
    expect(screen.getByText('User ID: user-456')).toBeInTheDocument();
    expect(screen.getByText('PENDING')).toBeInTheDocument();
    expect(screen.getByText('read')).toBeInTheDocument();
    expect(screen.getByText('write')).toBeInTheDocument();
    expect(screen.getByText('admin')).toBeInTheDocument();
  });

  it('shows approve and deny buttons for pending delegations', () => {
    const delegation = createMockDelegation({ status: 'pending' });

    render(
      <DelegationCard
        delegation={delegation}
        onUpdate={mockOnUpdate}
        onViewDetails={mockOnViewDetails}
      />
    );

    expect(screen.getByText('Approve')).toBeInTheDocument();
    expect(screen.getByText('Deny')).toBeInTheDocument();
    expect(screen.queryByText('Revoke')).not.toBeInTheDocument();
  });

  it('shows revoke button for approved delegations', () => {
    const delegation = createMockDelegation({ status: 'approved' });

    render(
      <DelegationCard
        delegation={delegation}
        onUpdate={mockOnUpdate}
        onViewDetails={mockOnViewDetails}
      />
    );

    expect(screen.getByText('Revoke')).toBeInTheDocument();
    expect(screen.queryByText('Approve')).not.toBeInTheDocument();
    expect(screen.queryByText('Deny')).not.toBeInTheDocument();
  });

  it('hides action buttons when showActions is false', () => {
    const delegation = createMockDelegation({ status: 'pending' });

    render(
      <DelegationCard
        delegation={delegation}
        onUpdate={mockOnUpdate}
        onViewDetails={mockOnViewDetails}
        showActions={false}
      />
    );

    expect(screen.queryByText('Approve')).not.toBeInTheDocument();
    expect(screen.queryByText('Deny')).not.toBeInTheDocument();
    expect(screen.queryByText('Revoke')).not.toBeInTheDocument();
  });

  it('handles approve delegation', async () => {
    const delegation = createMockDelegation({ status: 'pending' });
    mockDelegationAPI.approve.mockResolvedValue({
      message: 'Approved',
      delegation: { ...delegation, status: 'approved' },
      delegation_token: 'token123',
    });

    render(
      <DelegationCard
        delegation={delegation}
        onUpdate={mockOnUpdate}
        onViewDetails={mockOnViewDetails}
      />
    );

    const approveButton = screen.getByText('Approve');
    fireEvent.click(approveButton);

    await waitFor(() => {
      expect(mockDelegationAPI.approve).toHaveBeenCalledWith('1');
      expect(mockOnUpdate).toHaveBeenCalled();
    });
  });

  it('handles deny delegation', async () => {
    const delegation = createMockDelegation({ status: 'pending' });
    mockDelegationAPI.deny.mockResolvedValue({
      message: 'Denied',
      delegation: { ...delegation, status: 'denied' },
    });

    render(
      <DelegationCard
        delegation={delegation}
        onUpdate={mockOnUpdate}
        onViewDetails={mockOnViewDetails}
      />
    );

    const denyButton = screen.getByText('Deny');
    fireEvent.click(denyButton);

    await waitFor(() => {
      expect(mockDelegationAPI.deny).toHaveBeenCalledWith('1');
      expect(mockOnUpdate).toHaveBeenCalled();
    });
  });

  it('handles revoke delegation', async () => {
    const delegation = createMockDelegation({ status: 'approved' });
    mockDelegationAPI.revoke.mockResolvedValue({ message: 'Revoked' });

    render(
      <DelegationCard
        delegation={delegation}
        onUpdate={mockOnUpdate}
        onViewDetails={mockOnViewDetails}
      />
    );

    const revokeButton = screen.getByText('Revoke');
    fireEvent.click(revokeButton);

    await waitFor(() => {
      expect(mockDelegationAPI.revoke).toHaveBeenCalledWith('1');
      expect(mockOnUpdate).toHaveBeenCalled();
    });
  });

  it('calls onViewDetails when view details button is clicked', () => {
    const delegation = createMockDelegation();

    render(
      <DelegationCard
        delegation={delegation}
        onUpdate={mockOnUpdate}
        onViewDetails={mockOnViewDetails}
      />
    );

    const viewDetailsButton = screen.getByText('View Details');
    fireEvent.click(viewDetailsButton);

    expect(mockOnViewDetails).toHaveBeenCalledWith(delegation);
  });

  it('shows expiring soon badge for delegations expiring within an hour', () => {
    const soonExpiry = new Date(Date.now() + 30 * 60 * 1000).toISOString(); // 30 minutes from now
    const delegation = createMockDelegation({ expiresAt: soonExpiry });

    render(
      <DelegationCard
        delegation={delegation}
        onUpdate={mockOnUpdate}
        onViewDetails={mockOnViewDetails}
      />
    );

    expect(screen.getByText('Expiring Soon')).toBeInTheDocument();
  });

  it('shows approved date when delegation is approved', () => {
    const delegation = createMockDelegation({
      status: 'approved',
      approvedAt: '2024-01-01T12:00:00Z',
    });

    render(
      <DelegationCard
        delegation={delegation}
        onUpdate={mockOnUpdate}
        onViewDetails={mockOnViewDetails}
      />
    );

    expect(screen.getByText('Approved:')).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    const delegation = createMockDelegation({ status: 'pending' });
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    mockDelegationAPI.approve.mockRejectedValue(new Error('API Error'));

    render(
      <DelegationCard
        delegation={delegation}
        onUpdate={mockOnUpdate}
        onViewDetails={mockOnViewDetails}
      />
    );

    const approveButton = screen.getByText('Approve');
    fireEvent.click(approveButton);

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Failed to approve delegation:', expect.any(Error));
    });

    consoleSpy.mockRestore();
  });

  it('disables buttons while loading', async () => {
    const delegation = createMockDelegation({ status: 'pending' });
    mockDelegationAPI.approve.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    render(
      <DelegationCard
        delegation={delegation}
        onUpdate={mockOnUpdate}
        onViewDetails={mockOnViewDetails}
      />
    );

    const approveButton = screen.getByText('Approve');
    fireEvent.click(approveButton);

    // Button should be disabled while loading
    expect(approveButton).toBeDisabled();
    expect(screen.getByText('Deny')).toBeDisabled();
  });
});