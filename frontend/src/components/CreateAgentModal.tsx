import { useState } from 'react';
import { agentAPI } from '../services/api';
import { Agent, CreateAgentRequest } from '../types';

interface CreateAgentModalProps {
  onClose: () => void;
  onCreate: (agent: Agent) => void;
}

export default function CreateAgentModal({ onClose, onCreate }: CreateAgentModalProps) {
  const [formData, setFormData] = useState<CreateAgentRequest>({
    name: '',
    description: '',
    scopes: []
  });
  const [scopeInput, setScopeInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Agent name is required';
    } else if (formData.name.length < 2) {
      newErrors.name = 'Agent name must be at least 2 characters';
    } else if (formData.name.length > 50) {
      newErrors.name = 'Agent name must be less than 50 characters';
    }

    if (formData.description && formData.description.length > 200) {
      newErrors.description = 'Description must be less than 200 characters';
    }

    if (formData.scopes.length === 0) {
      newErrors.scopes = 'At least one scope is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    try {
      setLoading(true);
      const response = await agentAPI.create({
        ...formData,
        description: formData.description || undefined
      });
      onCreate(response.agent);
    } catch (err) {
      setErrors({ 
        submit: err instanceof Error ? err.message : 'Failed to create agent' 
      });
    } finally {
      setLoading(false);
    }
  };

  const addScope = () => {
    const scope = scopeInput.trim();
    if (scope && !formData.scopes.includes(scope)) {
      setFormData(prev => ({
        ...prev,
        scopes: [...prev.scopes, scope]
      }));
      setScopeInput('');
      // Clear scope error if it exists
      if (errors.scopes) {
        setErrors(prev => ({ ...prev, scopes: '' }));
      }
    }
  };

  const removeScope = (scopeToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      scopes: prev.scopes.filter(scope => scope !== scopeToRemove)
    }));
  };

  const handleScopeKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addScope();
    }
  };

  // Common scopes for quick selection
  const commonScopes = [
    'read:data',
    'write:data',
    'read:files',
    'write:files',
    'admin:users',
    'admin:system'
  ];

  return (
    <div className="modal modal-open">
      <div className="modal-box w-11/12 max-w-2xl">
        <form onSubmit={handleSubmit}>
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <h3 className="font-bold text-lg">Create New Agent</h3>
            <button
              type="button"
              className="btn btn-sm btn-circle btn-ghost"
              onClick={onClose}
            >
              ✕
            </button>
          </div>

          {/* Form Fields */}
          <div className="space-y-4">
            {/* Name */}
            <div className="form-control">
              <label className="label">
                <span className="label-text font-medium">
                  Agent Name <span className="text-error">*</span>
                </span>
              </label>
              <input
                type="text"
                className={`input input-bordered ${errors.name ? 'input-error' : ''}`}
                placeholder="Enter agent name"
                value={formData.name}
                onChange={(e) => {
                  setFormData(prev => ({ ...prev, name: e.target.value }));
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
                className={`textarea textarea-bordered h-20 ${errors.description ? 'textarea-error' : ''}`}
                placeholder="Enter agent description (optional)"
                value={formData.description}
                onChange={(e) => {
                  setFormData(prev => ({ ...prev, description: e.target.value }));
                  if (errors.description) setErrors(prev => ({ ...prev, description: '' }));
                }}
                disabled={loading}
              />
              {errors.description && (
                <label className="label">
                  <span className="label-text-alt text-error">{errors.description}</span>
                </label>
              )}
            </div>

            {/* Scopes */}
            <div className="form-control">
              <label className="label">
                <span className="label-text font-medium">
                  Permissions (Scopes) <span className="text-error">*</span>
                </span>
              </label>
              
              {/* Scope Input */}
              <div className="join mb-2">
                <input
                  type="text"
                  className="input input-bordered join-item flex-1"
                  placeholder="Enter scope (e.g., read:data)"
                  value={scopeInput}
                  onChange={(e) => setScopeInput(e.target.value)}
                  onKeyPress={handleScopeKeyPress}
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

              {/* Common Scopes */}
              <div className="mb-2">
                <div className="text-sm text-base-content/70 mb-1">Quick add:</div>
                <div className="flex flex-wrap gap-1">
                  {commonScopes.map(scope => (
                    <button
                      key={scope}
                      type="button"
                      className={`badge badge-outline badge-sm cursor-pointer hover:badge-primary ${
                        formData.scopes.includes(scope) ? 'badge-primary' : ''
                      }`}
                      onClick={() => {
                        if (!formData.scopes.includes(scope)) {
                          setFormData(prev => ({
                            ...prev,
                            scopes: [...prev.scopes, scope]
                          }));
                          if (errors.scopes) {
                            setErrors(prev => ({ ...prev, scopes: '' }));
                          }
                        }
                      }}
                      disabled={loading}
                    >
                      {scope}
                    </button>
                  ))}
                </div>
              </div>

              {/* Selected Scopes */}
              {formData.scopes.length > 0 && (
                <div className="space-y-1">
                  <div className="text-sm text-base-content/70">Selected permissions:</div>
                  <div className="flex flex-wrap gap-1">
                    {formData.scopes.map(scope => (
                      <span key={scope} className="badge badge-primary badge-sm">
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
                </div>
              )}

              {errors.scopes && (
                <label className="label">
                  <span className="label-text-alt text-error">{errors.scopes}</span>
                </label>
              )}
            </div>
          </div>

          {/* Submit Error */}
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
            <button
              type="button"
              className="btn btn-ghost"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="loading loading-spinner loading-sm mr-2"></span>
                  Creating...
                </>
              ) : (
                'Create Agent'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}