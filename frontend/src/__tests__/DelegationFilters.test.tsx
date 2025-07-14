import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import DelegationFilters from '../components/DelegationFilters';
import type { DelegationFilters as DelegationFiltersType } from '../types';

describe('DelegationFilters', () => {
  const mockOnFiltersChange = vi.fn();
  const mockOnClearFilters = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders filter controls', () => {
    const filters: DelegationFiltersType = {};

    render(
      <DelegationFilters
        filters={filters}
        onFiltersChange={mockOnFiltersChange}
        onClearFilters={mockOnClearFilters}
      />
    );

    expect(screen.getByText('Filters')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Search delegations...')).toBeInTheDocument();
    expect(screen.getByDisplayValue('All Statuses')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Filter by agent ID...')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Filter by user ID...')).toBeInTheDocument();
  });

  it('handles status filter changes', () => {
    const filters: DelegationFiltersType = {};

    render(
      <DelegationFilters
        filters={filters}
        onFiltersChange={mockOnFiltersChange}
        onClearFilters={mockOnClearFilters}
      />
    );

    const statusSelect = screen.getByDisplayValue('All Statuses');
    fireEvent.change(statusSelect, { target: { value: 'pending' } });

    expect(mockOnFiltersChange).toHaveBeenCalledWith({ status: 'pending' });
  });

  it('handles agent ID filter changes', () => {
    const filters: DelegationFiltersType = {};

    render(
      <DelegationFilters
        filters={filters}
        onFiltersChange={mockOnFiltersChange}
        onClearFilters={mockOnClearFilters}
      />
    );

    const agentIdInput = screen.getByPlaceholderText('Filter by agent ID...');
    fireEvent.change(agentIdInput, { target: { value: 'agent-123' } });

    expect(mockOnFiltersChange).toHaveBeenCalledWith({ agent_id: 'agent-123' });
  });

  it('handles user ID filter changes', () => {
    const filters: DelegationFiltersType = {};

    render(
      <DelegationFilters
        filters={filters}
        onFiltersChange={mockOnFiltersChange}
        onClearFilters={mockOnClearFilters}
      />
    );

    const userIdInput = screen.getByPlaceholderText('Filter by user ID...');
    fireEvent.change(userIdInput, { target: { value: 'user-456' } });

    expect(mockOnFiltersChange).toHaveBeenCalledWith({ user_id: 'user-456' });
  });

  it('handles search input changes', () => {
    const filters: DelegationFiltersType = {};

    render(
      <DelegationFilters
        filters={filters}
        onFiltersChange={mockOnFiltersChange}
        onClearFilters={mockOnClearFilters}
      />
    );

    const searchInput = screen.getByPlaceholderText('Search delegations...');
    fireEvent.change(searchInput, { target: { value: 'test search' } });

    // Search doesn't trigger onFiltersChange immediately, it's stored locally
    expect(mockOnFiltersChange).not.toHaveBeenCalled();
  });

  it('displays active filters', () => {
    const filters: DelegationFiltersType = {
      status: 'pending',
      agent_id: 'agent-123',
      user_id: 'user-456',
    };

    render(
      <DelegationFilters
        filters={filters}
        onFiltersChange={mockOnFiltersChange}
        onClearFilters={mockOnClearFilters}
      />
    );

    expect(screen.getByText('Active filters:')).toBeInTheDocument();
    expect(screen.getByText('Status: pending')).toBeInTheDocument();
    expect(screen.getByText('Agent: agent-123')).toBeInTheDocument();
    expect(screen.getByText('User: user-456')).toBeInTheDocument();
  });

  it('shows clear all button when filters are active', () => {
    const filters: DelegationFiltersType = {
      status: 'pending',
    };

    render(
      <DelegationFilters
        filters={filters}
        onFiltersChange={mockOnFiltersChange}
        onClearFilters={mockOnClearFilters}
      />
    );

    expect(screen.getByText('Clear All')).toBeInTheDocument();
  });

  it('hides clear all button when no filters are active', () => {
    const filters: DelegationFiltersType = {};

    render(
      <DelegationFilters
        filters={filters}
        onFiltersChange={mockOnFiltersChange}
        onClearFilters={mockOnClearFilters}
      />
    );

    expect(screen.queryByText('Clear All')).not.toBeInTheDocument();
  });

  it('handles clear all filters', () => {
    const filters: DelegationFiltersType = {
      status: 'pending',
      agent_id: 'agent-123',
    };

    render(
      <DelegationFilters
        filters={filters}
        onFiltersChange={mockOnFiltersChange}
        onClearFilters={mockOnClearFilters}
      />
    );

    const clearAllButton = screen.getByText('Clear All');
    fireEvent.click(clearAllButton);

    expect(mockOnClearFilters).toHaveBeenCalled();
  });

  it('handles individual filter removal', () => {
    const filters: DelegationFiltersType = {
      status: 'pending',
      agent_id: 'agent-123',
    };

    render(
      <DelegationFilters
        filters={filters}
        onFiltersChange={mockOnFiltersChange}
        onClearFilters={mockOnClearFilters}
      />
    );

    // Find and click the X button for status filter
    const statusBadge = screen.getByText('Status: pending').closest('.badge');
    const removeButton = statusBadge?.querySelector('button');
    
    if (removeButton) {
      fireEvent.click(removeButton);
      expect(mockOnFiltersChange).toHaveBeenCalledWith({ agent_id: 'agent-123' });
    }
  });

  it('updates local state when filters prop changes', () => {
    const initialFilters: DelegationFiltersType = {};
    const { rerender } = render(
      <DelegationFilters
        filters={initialFilters}
        onFiltersChange={mockOnFiltersChange}
        onClearFilters={mockOnClearFilters}
      />
    );

    expect(screen.getByDisplayValue('All Statuses')).toBeInTheDocument();

    const updatedFilters: DelegationFiltersType = { status: 'approved' };
    rerender(
      <DelegationFilters
        filters={updatedFilters}
        onFiltersChange={mockOnFiltersChange}
        onClearFilters={mockOnClearFilters}
      />
    );

    expect(screen.getByDisplayValue('Approved')).toBeInTheDocument();
  });

  it('clears empty filter values', () => {
    const filters: DelegationFiltersType = {};

    render(
      <DelegationFilters
        filters={filters}
        onFiltersChange={mockOnFiltersChange}
        onClearFilters={mockOnClearFilters}
      />
    );

    const agentIdInput = screen.getByPlaceholderText('Filter by agent ID...');
    
    // Set a value then clear it
    fireEvent.change(agentIdInput, { target: { value: 'agent-123' } });
    expect(mockOnFiltersChange).toHaveBeenCalledWith({ agent_id: 'agent-123' });

    fireEvent.change(agentIdInput, { target: { value: '' } });
    expect(mockOnFiltersChange).toHaveBeenCalledWith({ agent_id: undefined });
  });
});