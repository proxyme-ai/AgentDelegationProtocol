import { vi } from "vitest";
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Dashboard from '../pages/Dashboard';
import * as hooks from '../services/hooks';
import * as api from '../services/api';

// Mock the hooks
vi.mock('../services/hooks');
vi.mock('../services/api');

const mockDashboardData = {
  agents: {
    agents: [
      { id: '1', name: 'Test Agent', status: 'active', delegationCount: 2, scopes: ['read'], createdAt: '2024-01-01', lastUsed: '2024-01-02' }
    ],
    total: 1,
    timestamp: '2024-01-01'
  },
  delegations: {
    delegations: [
      { id: '1', agentId: '1', agentName: 'Test Agent', userId: 'user1', status: 'pending', scopes: ['read'], createdAt: '2024-01-01', expiresAt: '2024-01-02' }
    ],
    total: 1,
    timestamp: '2024-01-01'
  },
  systemStatus: {
    status: 'healthy',
    service: 'Agent Delegation Protocol',
    version: '1.0.0',
    timestamp: '2024-01-01',
    statistics: {
      total_agents: 1,
      active_agents: 1,
      total_delegations: 1,
      active_delegations: 0,
      pending_delegations: 1,
      active_tokens: 0
    }
  },
  activeTokens: {
    active_tokens: [],
    total: 0,
    timestamp: '2024-01-01'
  },
  loading: false,
  error: null,
  refetch: vi.fn()
};

const mockLogsData = {
  data: {
    logs: [
      {
        id: '1',
        timestamp: '2024-01-01T10:00:00Z',
        action: 'Agent registered',
        details: 'New agent Test Agent was registered',
        user_id: 'user1',
        agent_id: 'agent1'
      }
    ],
    total: 1,
    timestamp: '2024-01-01'
  },
  loading: false
};

const mockRunDemo = {
  mutate: vi.fn(),
  loading: false,
  error: null
};

describe('Dashboard', () => {
  beforeEach(() => {
    vi.mocked(hooks.useDashboardData).mockReturnValue(mockDashboardData);
    vi.mocked(hooks.usePolling).mockReturnValue(mockLogsData);
    vi.mocked(hooks.useRunDemo).mockReturnValue(mockRunDemo);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders dashboard title and description', () => {
    render(<Dashboard />);
    
    expect(screen.getByText('Agent Delegation Protocol')).toBeInTheDocument();
    expect(screen.getByText(/Comprehensive dashboard for managing AI agent delegations/)).toBeInTheDocument();
  });

  it('displays system statistics', () => {
    render(<Dashboard />);
    
    expect(screen.getByText('Total Agents')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument(); // total_agents value
    expect(screen.getByText('Delegations')).toBeInTheDocument();
    expect(screen.getByText('Active Tokens')).toBeInTheDocument();
    expect(screen.getByText('System Health')).toBeInTheDocument();
  });

  it('shows live demo section', () => {
    render(<Dashboard />);
    
    expect(screen.getByText('🚀 Live Protocol Demo')).toBeInTheDocument();
    expect(screen.getByText('Run Demo')).toBeInTheDocument();
    expect(screen.getByText(/Experience the complete delegation flow/)).toBeInTheDocument();
  });

  it('displays recent activity feed', () => {
    render(<Dashboard />);
    
    expect(screen.getByText('📊 Recent Activity')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Filter activities...')).toBeInTheDocument();
    expect(screen.getByText('Agent registered')).toBeInTheDocument();
  });

  it('shows pending delegations section', () => {
    render(<Dashboard />);
    
    expect(screen.getByText('⏳ Pending Delegations')).toBeInTheDocument();
    expect(screen.getByText('Test Agent')).toBeInTheDocument();
    expect(screen.getByText('Pending')).toBeInTheDocument();
  });

  it('shows active agents section', () => {
    render(<Dashboard />);
    
    expect(screen.getByText('🤖 Active Agents')).toBeInTheDocument();
    expect(screen.getByText('Test Agent')).toBeInTheDocument();
    expect(screen.getByText('2 delegations')).toBeInTheDocument();
  });

  it('handles demo execution', async () => {
    const user = userEvent.setup();
    render(<Dashboard />);
    
    const runDemoButton = screen.getByText('Run Demo');
    await user.click(runDemoButton);
    
    expect(mockRunDemo.mutate).toHaveBeenCalled();
  });

  it('filters activities based on search input', async () => {
    const user = userEvent.setup();
    render(<Dashboard />);
    
    const filterInput = screen.getByPlaceholderText('Filter activities...');
    await user.type(filterInput, 'registered');
    
    expect(screen.getByText('Agent registered')).toBeInTheDocument();
  });

  it('displays loading state', () => {
    vi.mocked(hooks.useDashboardData).mockReturnValue({
      ...mockDashboardData,
      loading: true
    });
    
    render(<Dashboard />);
    
    expect(screen.getByRole('status')).toBeInTheDocument(); // loading spinner
  });

  it('displays error state', () => {
    const mockError = {
      message: 'Failed to load data',
      code: 500,
      timestamp: '2024-01-01'
    };
    
    vi.mocked(hooks.useDashboardData).mockReturnValue({
      ...mockDashboardData,
      loading: false,
      error: mockError
    });
    
    render(<Dashboard />);
    
    expect(screen.getByText(/Failed to load dashboard data/)).toBeInTheDocument();
  });
});
