import { useState } from 'react';
import { AgentFilters } from '../types';

interface SearchAndFilterProps {
  filters: AgentFilters;
  onFiltersChange: (filters: AgentFilters) => void;
  onRefresh: () => void;
}

export default function SearchAndFilter({ filters, onFiltersChange, onRefresh }: SearchAndFilterProps) {
  const [searchInput, setSearchInput] = useState(filters.search || '');

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onFiltersChange({ ...filters, search: searchInput.trim() || undefined });
  };

  const handleStatusFilter = (status: string) => {
    const newStatus = filters.status === status ? undefined : status as any;
    onFiltersChange({ ...filters, status: newStatus });
  };

  const clearFilters = () => {
    setSearchInput('');
    onFiltersChange({});
  };

  const hasActiveFilters = filters.search || filters.status;

  return (
    <div className="card bg-base-100 shadow mb-6">
      <div className="card-body p-4">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search */}
          <form onSubmit={handleSearchSubmit} className="flex-1">
            <div className="join w-full">
              <input
                type="text"
                placeholder="Search agents by name or description..."
                className="input input-bordered join-item flex-1"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
              />
              <button type="submit" className="btn btn-primary join-item">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </div>
          </form>

          {/* Status Filters */}
          <div className="flex flex-wrap gap-2">
            <div className="text-sm font-medium text-base-content/70 flex items-center mr-2">
              Status:
            </div>
            <button
              className={`btn btn-sm ${filters.status === 'active' ? 'btn-success' : 'btn-outline'}`}
              onClick={() => handleStatusFilter('active')}
            >
              ✅ Active
            </button>
            <button
              className={`btn btn-sm ${filters.status === 'inactive' ? 'btn-warning' : 'btn-outline'}`}
              onClick={() => handleStatusFilter('inactive')}
            >
              ⏸️ Inactive
            </button>
            <button
              className={`btn btn-sm ${filters.status === 'suspended' ? 'btn-error' : 'btn-outline'}`}
              onClick={() => handleStatusFilter('suspended')}
            >
              🚫 Suspended
            </button>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            <button
              className="btn btn-ghost btn-sm"
              onClick={onRefresh}
              title="Refresh"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
            {hasActiveFilters && (
              <button
                className="btn btn-ghost btn-sm"
                onClick={clearFilters}
                title="Clear filters"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                Clear
              </button>
            )}
          </div>
        </div>

        {/* Active Filters Display */}
        {hasActiveFilters && (
          <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-base-300">
            <span className="text-sm text-base-content/70">Active filters:</span>
            {filters.search && (
              <span className="badge badge-primary badge-sm">
                Search: "{filters.search}"
                <button
                  className="ml-1 text-xs"
                  onClick={() => {
                    setSearchInput('');
                    onFiltersChange({ ...filters, search: undefined });
                  }}
                >
                  ×
                </button>
              </span>
            )}
            {filters.status && (
              <span className="badge badge-secondary badge-sm">
                Status: {filters.status}
                <button
                  className="ml-1 text-xs"
                  onClick={() => onFiltersChange({ ...filters, status: undefined })}
                >
                  ×
                </button>
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}