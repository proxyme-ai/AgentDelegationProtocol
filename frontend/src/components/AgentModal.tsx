import { useState, useEffect } from 'react';
import { agentAPI, delegationAPI } from '../services/api';
import { Agent, Delegation, UpdateAgentRequest } from '../types';

interface AgentModalProps {
  agent: Agent;
  onClose: () => void;
  onUpdate: (agent: Agent) => void;
  onDelete: (agentId: string) => void;
}

export default function AgentModal({ agent, onClose, onUpdate, onDelete }: AgentModalProps) {
  const [activeTab, setActiveTab] = useState<'details' | 'delegations' | 'edit'>('details');
  const [delegations, setDelegations] = useState<Delegation[]>([]);
  const [loadingDelegations, setLoadingDelegations] = useState(false);
  const [editForm, setEditForm] = useState<UpdateAgentRequest>({
    name: agent.name,
    description: agent.description || '',
    scopes: [...agent.scopes],
    status: agent.status
  });
  const [scopeInput, setScopeInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Load delegations when modal opens or tab changes
  useEffect(() => {
    if (activeTab === 'delegations') {
      loadDelegations();
    }
  }, [activeTab, agent.id]);

  const loadDelegations = async () => {
    try {
      setLoadingDelegations(true);
      const response = await delegationAPI.list({ agent_id: agent.id });
      setDelegations(response.delegations);
    } catch (err) {
      console.error('Failed to load delegations:', err);
    } finally {
      setLoadingDelegations(false);
    }
  };

  const handleUpdate = async () => {
    if (!validateEditForm()) return;

    try {
      setLoading(true);
      const response = await agentAPI.update(agent.id, {
        ...editForm,
        description: editForm.description || undefined
      });
      onUpdate(response.agent);
      setActiveTab('details');
    } catch (err) {
      setErrors({ 
        submit: err instanceof Error ? err.message : 'Failed to update agent' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm(`Are you sure you want to delete "${agent.name}"? This action cannot be undone.`)) {
      return;
    }

    try {
      setLoading(true);
      await agentAPI.delete(agent.id);
      onDelete(agent.id);
    } catch (err) {
      setErrors({ 
        submit: err instanceof Error ? err.message : 'Failed to delete agent' 
      });
      setLoading(false);
    }
  };

  const validateEditForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!editForm.name?.trim()) {
      newErrors.name = 'Agent name is required';
    } else if (editForm.name.length < 2) {
      newErrors.name = 'Agent name must be at least 2 characters';
    }

    if (editForm.scopes.length === 0) {
      newErrors.scopes = 'At least one scope is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const addScope = () => {
    const scope = scopeInput.trim();
    if (scope && !editForm.scopes.includes(scope)) {
      setEditForm(prev => ({
        ...prev,
        scopes: [...prev.scopes, scope]
      }));
      setScopeInput('');
    }
  };

  const removeScope = (scopeToRemove: string) => {
    setEditForm(prev => ({
      ...prev,
      scopes: prev.scopes.filter(scope => scope !== scopeToRemove)
    }));
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'badge-success';
      case 'inactive': return 'badge-warning';
      case 'suspended': return 'badge-error';
      default: return 'badge-ghost';
    }
  };

  const getDelegationStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'badge-success';
      case 'pending': return 'badge-warning';
      case 'denied': return 'badge-error';
      case 'expired': return 'badge-ghost';
      case 'revoked': return 'badge-error';
      default: return 'badge-ghost';
    }
  };

  return (
    <div className="modal modal-open">
      <div className="modal-box w-11/12 max-w-4xl max-h-[90vh]">
        {/* Header */}
        <div className="flex justify-between items-start mb-6">
          <div>
            <h3 className="font-bold text-xl flex items-center">
              <span className="text-2xl mr-2">🤖</span>
              {agent.name}
            </h3>
            <div className={`badge ${getStatusColor(agent.status)} mt-2`}>
              {agent.status}
            </div>
          </div>
          <button
            className="btn btn-sm btn-circle btn-ghost"
            onClick={onClose}
          >
            ✕
          </button>
        </div>

        {/* Tabs */}
        <div className="tabs tabs-bordered mb-6">
          <button
            className={`tab ${activeTab === 'details' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('details')}
          >
            Details
          </button>
          <button
            className={`tab ${activeTab === 'delegations' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('delegations')}
          >
            Delegations ({agent.delegationCount})
          </button>
          <button
            className={`tab ${activeTab === 'edit' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('edit')}
          >
            Edit
          </button>
        </div>

        {/* Tab Content */}
        <div className="min-h-[400px]">
          {/* Details Tab */}
          {activeTab === 'details' && (
            <div className="space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="stat bg-base-200 rounded-lg">
                  <div className="stat-title">Agent ID</div>
                  <div className="stat-value text-sm font-mono">{agent.id}</div>
                </div>
                <div className="stat bg-base-200 rounded-lg">
                  <div className="stat-title">Status</div>
                  <div className="stat-value text-sm">
                    <span className={`badge ${getStatusColor(agent.status)}`}>
                      {agent.status}
                    </span>
                  </div>
                </div>
                <div className="stat bg-base-200 rounded-lg">
                  <div className="stat-title">Delegations</div>
                  <div className="stat-value text-2xl">{agent.delegationCount}</div>
                </div>
                <div className="stat bg-base-200 rounded-lg">
                  <div className="stat-title">Permissions</div>
                  <div className="stat-value text-2xl">{agent.scopes.length}</div>
                </div>
              </div>

              {/* Description */}
              {agent.description && (
                <div>
                  <h4 className="font-semibold mb-2">Description</h4>
                  <p className="text-base-content/80">{agent.description}</p>
                </div>
              )}

              {/* Scopes */}
              <div>
                <h4 className="font-semibold mb-2">Permissions</h4>
                <div className="flex flex-wrap gap-2">
                  {agent.scopes.map(scope => (
                    <span key={scope} className="badge badge-outline">
                      {scope}
                    </span>
                  ))}
                </div>
              </div>

              {/* Timestamps */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold mb-1">Created</h4>
                  <p className="text-sm text-base-content/70">{formatDate(agent.createdAt)}</p>
                </div>
                {agent.lastUsed && (
                  <div>
                    <h4 className="font-semibold mb-1">Last Used</h4>
                    <p className="text-sm text-base-content/70">{formatDate(agent.lastUsed)}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Delegations Tab */}
          {activeTab === 'delegations' && (
            <div>
              {loadingDelegations ? (
                <div className="flex justify-center py-8">
                  <span className="loading loading-spinner loading-lg"></span>
                </div>
              ) : delegations.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-4xl mb-4">📋</div>
                  <h4 className="text-lg font-semibold mb-2">No delegations</h4>
                  <p className="text-base-content/70">This agent has no delegation history.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {delegations.map(delegation => (
                    <div key={delegation.id} className="card bg-base-200">
                      <div className="card-body p-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <h5 className="font-semibold">User: {delegation.userId}</h5>
                            <p className="text-sm text-base-content/70 mb-2">
                              ID: {delegation.id}
                            </p>
                            <div className="flex flex-wrap gap-1 mb-2">
                              {delegation.scopes.map(scope => (
                                <span key={scope} className="badge badge-outline badge-xs">
                                  {scope}
                                </span>
                              ))}
                            </div>
                            <div className="text-xs text-base-content/60">
                              <div>Created: {formatDate(delegation.createdAt)}</div>
                              {delegation.approvedAt && (
                                <div>Approved: {formatDate(delegation.approvedAt)}</div>
                              )}
                              <div>Expires: {formatDate(delegation.expiresAt)}</div>
                            </div>
                          </div>
                          <span className={`badge ${getDelegationStatusColor(delegation.status)}`}>
                            {delegation.status}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Edit Tab */}
          {activeTab === 'edit' && (
            <div className="space-y-4">
              {/* Name */}
              <div className="form-control">
                <label className="label">
                  <span className="label-text font-medium">Agent Name</span>
                </label>
                <input
                  type="text"
                  className={`input input-bordered ${errors.name ? 'input-error' : ''}`}
                  value={editForm.name}
                  onChange={(e) => {
                    setEditForm(prev => ({ ...prev, name: e.target.value }));
                    if (errors.name) setErrors(prev => ({ ...prev, name: '' }));
                  }}
                  disabled={loading}
                />
                {errors.name && (
                  <label className="label">
                    <span className="label-text-alt text-error">{errors.name}</span>
                  </label>
                )}
              </div>

              {/* Description */}
              <div className="form-control">
                <label className="label">
                  <span className="label-text font-medium">Description</span>
                </label>
                <textarea
                  className="textarea textarea-bordered h-20"
                  value={editForm.description}
                  onChange={(e) => setEditForm(prev => ({ ...prev, description: e.target.value }))}
                  disabled={loading}
                />
              </div>

              {/* Status */}
              <div className="form-control">
                <label className="label">
                  <span className="label-text font-medium">Status</span>
                </label>
                <select
                  className="select select-bordered"
                  value={editForm.status}
                  onChange={(e) => setEditForm(prev => ({ ...prev, status: e.target.value as any }))}
                  disabled={loading}
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="suspended">Suspended</option>
                </select>
              </div>

              {/* Scopes */}
              <div className="form-control">
                <label className="label">
                  <span className="label-text font-medium">Permissions</span>
                </label>
                
                <div className="join mb-2">
                  <input
                    type="text"
                    className="input input-bordered join-item flex-1"
                    placeholder="Add new scope"
                    value={scopeInput}
                    onChange={(e) => setScopeInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addScope())}
                    disabled={loading}
                  />
                  <button
                    type="button"
                    className="btn btn-primary join-item"
                    onClick={addScope}
                    disabled={!scopeInput.trim() || loading}
                  >
                    Add
                  </button>
                </div>

                <div className="flex flex-wrap gap-1">
                  {editForm.scopes.map(scope => (
                    <span key={scope} className="badge badge-primary">
                      {scope}
                      <button
                        type="button"
                        className="ml-1 text-xs hover:text-error"
                        onClick={() => removeScope(scope)}
                        disabled={loading}
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>

                {errors.scopes && (
                  <label className="label">
                    <span className="label-text-alt text-error">{errors.scopes}</span>
                  </label>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Error Display */}
        {errors.submit && (
          <div className="alert alert-error mt-4">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{errors.submit}</span>
          </div>
        )}

        {/* Actions */}
        <div className="modal-action">
          {activeTab === 'edit' ? (
            <>
              <button
                className="btn btn-error"
                onClick={handleDelete}
                disabled={loading}
              >
                {loading ? (
                  <span className="loading loading-spinner loading-sm"></span>
                ) : (
                  <>
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    Delete
                  </>
                )}
              </button>
              <button
                className="btn btn-ghost"
                onClick={() => setActiveTab('details')}
                disabled={loading}
              >
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={handleUpdate}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="loading loading-spinner loading-sm mr-2"></span>
                    Saving...
                  </>
                ) : (
                  'Save Changes'
                )}
              </button>
            </>
          ) : (
            <button className="btn btn-ghost" onClick={onClose}>
              Close
            </button>
          )}
        </div>
      </div>
    </div>
  );
}