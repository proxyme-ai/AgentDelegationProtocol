import { Agent } from '../types';

interface AgentCardProps {
  agent: Agent;
  selected: boolean;
  onSelect: (selected: boolean) => void;
  onClick: () => void;
}

export default function AgentCard({ agent, selected, onSelect, onClick }: AgentCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'badge-success';
      case 'inactive': return 'badge-warning';
      case 'suspended': return 'badge-error';
      default: return 'badge-ghost';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return '✅';
      case 'inactive': return '⏸️';
      case 'suspended': return '🚫';
      default: return '❓';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatLastUsed = (lastUsed?: string) => {
    if (!lastUsed) return 'Never';
    const date = new Date(lastUsed);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return formatDate(lastUsed);
  };

  return (
    <div className={`card bg-base-100 shadow hover:shadow-lg transition-shadow cursor-pointer ${
      selected ? 'ring-2 ring-primary' : ''
    }`}>
      <div className="card-body p-4">
        {/* Header with checkbox and status */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center">
            <input
              type="checkbox"
              className="checkbox checkbox-sm mr-3"
              checked={selected}
              onChange={(e) => {
                e.stopPropagation();
                onSelect(e.target.checked);
              }}
            />
            <div className="text-2xl mr-2">🤖</div>
          </div>
          <div className={`badge ${getStatusColor(agent.status)} badge-sm`}>
            <span className="mr-1">{getStatusIcon(agent.status)}</span>
            {agent.status}
          </div>
        </div>

        {/* Agent Info */}
        <div onClick={onClick} className="flex-1">
          <h3 className="card-title text-lg mb-2">{agent.name}</h3>
          
          {agent.description && (
            <p className="text-sm text-base-content/70 mb-3 line-clamp-2">
              {agent.description}
            </p>
          )}

          {/* Stats */}
          <div className="grid grid-cols-2 gap-2 mb-3">
            <div className="stat-item">
              <div className="text-xs text-base-content/50">Delegations</div>
              <div className="text-sm font-semibold">{agent.delegationCount}</div>
            </div>
            <div className="stat-item">
              <div className="text-xs text-base-content/50">Scopes</div>
              <div className="text-sm font-semibold">{agent.scopes.length}</div>
            </div>
          </div>

          {/* Scopes */}
          {agent.scopes.length > 0 && (
            <div className="mb-3">
              <div className="text-xs text-base-content/50 mb-1">Permissions</div>
              <div className="flex flex-wrap gap-1">
                {agent.scopes.slice(0, 3).map((scope) => (
                  <span key={scope} className="badge badge-outline badge-xs">
                    {scope}
                  </span>
                ))}
                {agent.scopes.length > 3 && (
                  <span className="badge badge-outline badge-xs">
                    +{agent.scopes.length - 3} more
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Timestamps */}
          <div className="text-xs text-base-content/50 space-y-1">
            <div>Created: {formatDate(agent.createdAt)}</div>
            <div>Last used: {formatLastUsed(agent.lastUsed)}</div>
          </div>
        </div>

        {/* Actions */}
        <div className="card-actions justify-end mt-3 pt-3 border-t border-base-300">
          <button 
            className="btn btn-ghost btn-xs"
            onClick={(e) => {
              e.stopPropagation();
              onClick();
            }}
          >
            View Details
          </button>
        </div>
      </div>
    </div>
  );
}