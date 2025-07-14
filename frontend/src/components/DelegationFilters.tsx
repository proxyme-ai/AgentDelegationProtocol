import { useState, useEffect } from 'react';
import type { DelegationFilters } from '../types';

interface DelegationFiltersProps {
  filters: DelegationFilters;
  onFiltersChange: (filters: DelegationFilters) => void;
  onClearFilters: () => void;
}

export default function DelegationFilters({ 
  filters, 
  onFiltersChange, 
  onClearFilters 
}: DelegationFiltersProps) {
  const [localFilters, setLocalFilters] = useState<DelegationFilters>(filters);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  const handleStatusChange = (status: string) => {
    const newFilters = {
      ...localFilters,
      status: status === 'all' ? undefined : status as any
    };
    setLocalFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleAgentIdChange = (agentId: string) => {
    const newFilters = {
      ...localFilters,
      agent_id: agentId || undefined
    };
    setLocalFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleUserIdChange = (userId: string) => {
    const newFilters = {
      ...localFilters,
      user_id: userId || undefined
    };
    setLocalFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleSearchChange = (term: string) => {
    setSearchTerm(term);
    // You can implement search logic here if needed
    // For now, we'll just store the search term
  };

  const handleClearAll = () => {
    setLocalFilters({});
    setSearchTerm('');
    onClearFilters();
  };

  const hasActiveFilters = () => {
    return localFilters.status || localFilters.agent_id || localFilters.user_id || searchTerm;
  };

  return (
    <div className="bg-base-100 p-4 rounded-lg shadow-sm border">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-semibold text-lg">Filters</h3>
        {hasActiveFilters() && (
          <button 
            className="btn btn-sm btn-outline"
            onClick={handleClearAll}
          >
            Clear All
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Search */}
        <div className="form-control">
          <label className="label">
            <span className="label-text font-medium">Search</span>
          </label>
          <input
            type="text"
            placeholder="Search delegations..."
            className="input input-bordered input-sm"
            value={searchTerm}
            onChange={(e) => handleSearchChange(e.target.value)}
          />
        </div>

        {/* Status Filter */}
        <div className="form-control">
          <label className="label">
            <span className="label-text font-medium">Status</span>
          </label>
          <select
            className="select select-bordered select-sm"
            value={localFilters.status || 'all'}
            onChange={(e) => handleStatusChange(e.target.value)}
          >
            <option value="all">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="denied">Denied</option>
            <option value="expired">Expired</option>
            <option value="revoked">Revoked</option>
          </select>
        </div>

        {/* Agent ID Filter */}
        <div className="form-control">
          <label className="label">
            <span className="label-text font-medium">Agent ID</span>
          </label>
          <input
            type="text"
            placeholder="Filter by agent ID..."
            className="input input-bordered input-sm"
            value={localFilters.agent_id || ''}
            onChange={(e) => handleAgentIdChange(e.target.value)}
          />
        </div>

        {/* User ID Filter */}
        <div className="form-control">
          <label className="label">
            <span className="label-text font-medium">User ID</span>
          </label>
          <input
            type="text"
            placeholder="Filter by user ID..."
            className="input input-bordered input-sm"
            value={localFilters.user_id || ''}
            onChange={(e) => handleUserIdChange(e.target.value)}
          />
        </div>
      </div>

      {/* Active Filters Display */}
      {hasActiveFilters() && (
        <div className="mt-4 pt-4 border-t">
          <div className="flex flex-wrap gap-2">
            <span className="text-sm font-medium">Active filters:</span>
            {localFilters.status && (
              <div className="badge badge-primary gap-2">
                Status: {localFilters.status}
                <button 
                  className="btn btn-xs btn-circle btn-ghost"
                  onClick={() => handleStatusChange('all')}
                >
                  ✕
                </button>
              </div>
            )}
            {localFilters.agent_id && (
              <div className="badge badge-primary gap-2">
                Agent: {localFilters.agent_id}
                <button 
                  className="btn btn-xs btn-circle btn-ghost"
                  onClick={() => handleAgentIdChange('')}
                >
                  ✕
                </button>
              </div>
            )}
            {localFilters.user_id && (
              <div className="badge badge-primary gap-2">
                User: {localFilters.user_id}
                <button 
                  className="btn btn-xs btn-circle btn-ghost"
                  onClick={() => handleUserIdChange('')}
                >
                  ✕
                </button>
              </div>
            )}
            {searchTerm && (
              <div className="badge badge-primary gap-2">
                Search: {searchTerm}
                <button 
                  className="btn btn-xs btn-circle btn-ghost"
                  onClick={() => handleSearchChange('')}
                >
                  ✕
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}