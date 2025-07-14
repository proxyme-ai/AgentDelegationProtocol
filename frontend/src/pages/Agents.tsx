import { useState, useEffect } from 'react';
import { agentAPI } from '../services/api';
import { Agent, AgentFilters } from '../types';
import AgentCard from '../components/AgentCard';
import AgentModal from '../components/AgentModal';
import CreateAgentModal from '../components/CreateAgentModal';
import BulkActionsBar from '../components/BulkActionsBar';
import SearchAndFilter from '../components/SearchAndFilter';
import Loading from '../components/Loading';
import { useToast, ToastContainer } from '../components/Toast';

export default function Agents() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAgents, setSelectedAgents] = useState<Set<string>>(new Set());
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filters, setFilters] = useState<AgentFilters>({});
  const toast = useToast();

  // Load agents
  const loadAgents = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await agentAPI.list(filters);
      setAgents(response.agents);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load agents');
    } finally {
      setLoading(false);
    }
  };

  // Load agents on mount and when filters change
  useEffect(() => {
    loadAgents();
  }, [filters]);

  // Handle agent selection
  const handleAgentSelect = (agentId: string, selected: boolean) => {
    const newSelected = new Set(selectedAgents);
    if (selected) {
      newSelected.add(agentId);
    } else {
      newSelected.delete(agentId);
    }
    setSelectedAgents(newSelected);
  };

  // Handle select all
  const handleSelectAll = (selected: boolean) => {
    if (selected) {
      setSelectedAgents(new Set(agents.map(agent => agent.id)));
    } else {
      setSelectedAgents(new Set());
    }
  };

  // Handle agent creation
  const handleAgentCreated = (agent: Agent) => {
    setAgents(prev => [agent, ...prev]);
    setShowCreateModal(false);
    toast.success('Agent created successfully');
  };

  // Handle agent update
  const handleAgentUpdated = (updatedAgent: Agent) => {
    setAgents(prev => prev.map(agent => 
      agent.id === updatedAgent.id ? updatedAgent : agent
    ));
    setSelectedAgent(updatedAgent);
    toast.success('Agent updated successfully');
  };

  // Handle agent deletion
  const handleAgentDeleted = (agentId: string) => {
    setAgents(prev => prev.filter(agent => agent.id !== agentId));
    setSelectedAgent(null);
    setSelectedAgents(prev => {
      const newSelected = new Set(prev);
      newSelected.delete(agentId);
      return newSelected;
    });
    toast.success('Agent deleted successfully');
  };

  // Handle bulk operations
  const handleBulkAction = async (action: string) => {
    try {
      const selectedIds = Array.from(selectedAgents);
      
      switch (action) {
        case 'activate':
          await Promise.all(selectedIds.map(id => 
            agentAPI.update(id, { status: 'active' })
          ));
          toast.success(`${selectedIds.length} agents activated`);
          break;
        case 'deactivate':
          await Promise.all(selectedIds.map(id => 
            agentAPI.update(id, { status: 'inactive' })
          ));
          toast.success(`${selectedIds.length} agents deactivated`);
          break;
        case 'suspend':
          await Promise.all(selectedIds.map(id => 
            agentAPI.update(id, { status: 'suspended' })
          ));
          toast.success(`${selectedIds.length} agents suspended`);
          break;
        case 'delete':
          if (confirm(`Are you sure you want to delete ${selectedIds.length} agents?`)) {
            await Promise.all(selectedIds.map(id => agentAPI.delete(id)));
            toast.success(`${selectedIds.length} agents deleted`);
          }
          break;
      }
      
      setSelectedAgents(new Set());
      loadAgents();
    } catch (err) {
      toast.error(
        'Bulk operation failed',
        err instanceof Error ? err.message : 'An unexpected error occurred'
      );
    }
  };

  if (loading) {
    return <Loading message="Loading agents..." />;
  }

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Agent Management</h1>
          <p className="text-base-content/70 mt-1">
            Manage AI agents and their permissions
          </p>
        </div>
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateModal(true)}
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Create Agent
        </button>
      </div>

      {/* Search and Filter */}
      <SearchAndFilter 
        filters={filters}
        onFiltersChange={setFilters}
        onRefresh={loadAgents}
      />

      {/* Bulk Actions */}
      {selectedAgents.size > 0 && (
        <BulkActionsBar
          selectedCount={selectedAgents.size}
          onAction={handleBulkAction}
          onClear={() => setSelectedAgents(new Set())}
        />
      )}

      {/* Error Display */}
      {error && (
        <div className="alert alert-error mb-4">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{error}</span>
          <button 
            className="btn btn-sm btn-ghost"
            onClick={loadAgents}
          >
            Retry
          </button>
        </div>
      )}

      {/* Agents Grid */}
      {agents.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🤖</div>
          <h3 className="text-xl font-semibold mb-2">No agents found</h3>
          <p className="text-base-content/70 mb-4">
            {Object.keys(filters).length > 0 
              ? "Try adjusting your search filters"
              : "Create your first agent to get started"
            }
          </p>
          <button 
            className="btn btn-primary"
            onClick={() => setShowCreateModal(true)}
          >
            Create Agent
          </button>
        </div>
      ) : (
        <>
          {/* Select All Checkbox */}
          <div className="flex items-center mb-4">
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                className="checkbox checkbox-sm mr-2"
                checked={selectedAgents.size === agents.length && agents.length > 0}
                onChange={(e) => handleSelectAll(e.target.checked)}
              />
              <span className="text-sm">
                Select all ({agents.length} agents)
              </span>
            </label>
          </div>

          {/* Agents Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {agents.map((agent) => (
              <AgentCard
                key={agent.id}
                agent={agent}
                selected={selectedAgents.has(agent.id)}
                onSelect={(selected) => handleAgentSelect(agent.id, selected)}
                onClick={() => setSelectedAgent(agent)}
              />
            ))}
          </div>
        </>
      )}

      {/* Modals */}
      {selectedAgent && (
        <AgentModal
          agent={selectedAgent}
          onClose={() => setSelectedAgent(null)}
          onUpdate={handleAgentUpdated}
          onDelete={handleAgentDeleted}
        />
      )}

      {showCreateModal && (
        <CreateAgentModal
          onClose={() => setShowCreateModal(false)}
          onCreate={handleAgentCreated}
        />
      )}

      {/* Toast Notifications */}
      <ToastContainer messages={toast.messages} onClose={toast.removeToast} />
    </div>
  );
}