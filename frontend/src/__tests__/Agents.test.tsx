import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi } from 'vitest';
import Agents from '../pages/Agents';

// Mock the API
vi.mock('../services/api', () => ({
  agentAPI: {
    list: vi.fn().mockResolvedValue({
      agents: [
        {
          id: '1',
          name: 'Test Agent',
          description: 'A test agent',
          scopes: ['read:data', 'write:data'],
          status: 'active',
          createdAt: '2024-01-01T00:00:00Z',
          lastUsed: '2024-01-02T00:00:00Z',
          delegationCount: 2
        }
      ],
      total: 1,
      timestamp: '2024-01-01T00:00:00Z'
    }),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn()
  }
}));

// Mock components that might not exist yet
vi.mock('../components/AgentCard', () => ({
  default: ({ agent, onClick }: any) => (
    <div data-testid="agent-card" onClick={onClick}>
      {agent.name}
    </div>
  )
}));

vi.mock('../components/SearchAndFilter', () => ({
  default: ({ onFiltersChange }: any) => (
    <div data-testid="search-filter">
      <input 
        placeholder="Search agents..."
        onChange={(e) => onFiltersChange({ search: e.target.value })}
      />
    </div>
  )
}));

vi.mock('../components/BulkActionsBar', () => ({
  default: ({ selectedCount }: any) => (
    <div data-testid="bulk-actions">
      {selectedCount} selected
    </div>
  )
}));

vi.mock('../components/CreateAgentModal', () => ({
  default: ({ onClose }: any) => (
    <div data-testid="create-modal">
      <button onClick={onClose}>Close</button>
    </div>
  )
}));

vi.mock('../components/AgentModal', () => ({
  default: ({ agent, onClose }: any) => (
    <div data-testid="agent-modal">
      {agent.name}
      <button onClick={onClose}>Close</button>
    </div>
  )
}));

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Agents', () => {
  it('renders agents page with header', async () => {
    renderWithRouter(<Agents />);
    
    expect(screen.getByText('Agent Management')).toBeInTheDocument();
    expect(screen.getByText('Manage AI agents and their permissions')).toBeInTheDocument();
    expect(screen.getByText('Create Agent')).toBeInTheDocument();
  });

  it('displays agent cards when agents are loaded', async () => {
    renderWithRouter(<Agents />);
    
    // Wait for the agent to be loaded and displayed
    expect(await screen.findByText('Test Agent')).toBeInTheDocument();
    expect(screen.getByTestId('agent-card')).toBeInTheDocument();
  });

  it('shows search and filter components', () => {
    renderWithRouter(<Agents />);
    
    expect(screen.getByTestId('search-filter')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Search agents...')).toBeInTheDocument();
  });
});