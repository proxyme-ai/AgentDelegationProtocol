import { useEffect, useState, useCallback } from 'react';
import { delegationAPI } from '../services/api';
import type { Delegation, DelegationFilters } from '../types';
import DelegationCard from '../components/DelegationCard';
import DelegationDetailModal from '../components/DelegationDetailModal';
import DelegationFilters from '../components/DelegationFilters';
import Loading from '../components/Loading';
import DelegationFilters from '../components/DelegationFilters';

export default function DelegationsList() {
  const [delegations, setDelegations] = useState<Delegation[]>([]);
  const [filteredDelegations, setFilteredDelegations] = useState<Delegation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<DelegationFilters>({});
  const [selectedDelegation, setSelectedDelegation] = useState<Delegation | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'pending' | 'active' | 'history'>('pending');
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);

  const loadDelegations = useCallback(async () => {
    try {
      setError(null);
      const response = await delegationAPI.list(filters);
      setDelegations(response.delegations);
    } catch (err) {
      console.error('Failed to load delegations:', err);
      setError('Failed to load delegations. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  // Filter delegations based on active tab
  useEffect(() => {
    let filtered = delegations;
    
    switch (activeTab) {
      case 'pending':
        filtered = delegations.filter(d => d.status === 'pending');
        break;
      case 'active':
        filtered = delegations.filter(d => d.status === 'approved');
        break;
      case 'history':
        filtered = delegations.filter(d => 
          ['denied', 'expired', 'revoked'].includes(d.status)
        );
        break;
    }
    
    setFilteredDelegations(filtered);
  }, [delegations, activeTab]);

  // Initial load
  useEffect(() => {
    loadDelegations();
  }, [loadDelegations]);

  // Set up real-time updates for active delegations
  useEffect(() => {
    if (activeTab === 'active') {
      const interval = setInterval(() => {
        loadDelegations();
      }, 30000); // Refresh every 30 seconds
      
      setRefreshInterval(interval);
      
      return () => {
        if (interval) clearInterval(interval);
      };
    } else {
      if (refreshInterval) {
        clearInterval(refreshInterval);
        setRefreshInterval(null);
      }
    }
  }, [activeTab, loadDelegations]);

  // Cleanup interval on unmount
  useEffect(() => {
    return () => {
      if (refreshInterval) clearInterval(refreshInterval);
    };
  }, [refreshInterval]);

  const handleFiltersChange = (newFilters: DelegationFilters) => {
    setFilters(newFilters);
  };

  const handleClearFilters = () => {
    setFilters({});
  };

  const handleViewDetails = (delegation: Delegation) => {
    setSelectedDelegation(delegation);
    setIsDetailModalOpen(true);
  };

  const handleCloseDetailModal = () => {
    setIsDetailModalOpen(false);
    setSelectedDelegation(null);
  };

  const getTabCounts = () => {
    const pending = delegations.filter(d => d.status === 'pending').length;
    const active = delegations.filter(d => d.status === 'approved').length;
    const history = delegations.filter(d => 
      ['denied', 'expired', 'revoked'].includes(d.status)
    ).length;
    
    return { pending, active, history };
  };

  const tabCounts = getTabCounts();

  if (isLoading) {
    return <Loading />;
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Delegation Management</h1>
          <p className="text-base-content/70 mt-1">
            Manage agent delegation requests and monitor active delegations
          </p>
        </div>
        <div className="flex items-center gap-2">
          {activeTab === 'active' && (
            <div className="flex items-center gap-2 text-sm text-base-content/70">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              Auto-refreshing
            </div>
          )}
          <button 
            className="btn btn-outline btn-sm"
            onClick={loadDelegations}
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="alert alert-error">
          <span>{error}</span>
          <button 
            className="btn btn-sm btn-ghost"
            onClick={loadDelegations}
          >
            Retry
          </button>
        </div>
      )}

      {/* Tabs */}
      <div className="tabs tabs-boxed">
        <button 
          className={`tab ${activeTab === 'pending' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('pending')}
        >
          Pending Queue
          {tabCounts.pending > 0 && (
            <div className="badge badge-warning badge-sm ml-2">
              {tabCounts.pending}
            </div>
          )}
        </button>
        <button 
          className={`tab ${activeTab === 'active' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('active')}
        >
          Active Delegations
          {tabCounts.active > 0 && (
            <div className="badge badge-success badge-sm ml-2">
              {tabCounts.active}
            </div>
          )}
        </button>
        <button 
          className={`tab ${activeTab === 'history' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          History
          {tabCounts.history > 0 && (
            <div className="badge badge-neutral badge-sm ml-2">
              {tabCounts.history}
            </div>
          )}
        </button>
      </div>

      {/* Filters */}
      <DelegationFilters
        filters={filters}
        onFiltersChange={handleFiltersChange}
        onClearFilters={handleClearFilters}
      />

      {/* Content */}
      <div className="space-y-4">
        {/* Tab-specific headers */}
        {activeTab === 'pending' && (
          <div className="bg-warning/10 border border-warning/20 rounded-lg p-4">
            <h2 className="font-semibold text-lg mb-2">Pending Delegation Requests</h2>
            <p className="text-sm text-base-content/70">
              Review and approve or deny delegation requests from agents. 
              Approved delegations will generate delegation tokens for the agents.
            </p>
          </div>
        )}

        {activeTab === 'active' && (
          <div className="bg-success/10 border border-success/20 rounded-lg p-4">
            <h2 className="font-semibold text-lg mb-2">Active Delegations</h2>
            <p className="text-sm text-base-content/70">
              Monitor currently active delegations. These delegations have valid tokens 
              and can be revoked if needed. Status updates automatically every 30 seconds.
            </p>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="bg-neutral/10 border border-neutral/20 rounded-lg p-4">
            <h2 className="font-semibold text-lg mb-2">Delegation History</h2>
            <p className="text-sm text-base-content/70">
              View completed, denied, expired, and revoked delegations. 
              Use filters to search through historical records.
            </p>
          </div>
        )}

        {/* Delegations Grid */}
        {filteredDelegations.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📋</div>
            <h3 className="text-xl font-semibold mb-2">
              {activeTab === 'pending' && 'No Pending Delegations'}
              {activeTab === 'active' && 'No Active Delegations'}
              {activeTab === 'history' && 'No Historical Delegations'}
            </h3>
            <p className="text-base-content/70">
              {activeTab === 'pending' && 'All delegation requests have been processed.'}
              {activeTab === 'active' && 'No delegations are currently active.'}
              {activeTab === 'history' && 'No completed delegations found.'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {filteredDelegations.map((delegation) => (
              <DelegationCard
                key={delegation.id}
                delegation={delegation}
                onUpdate={loadDelegations}
                onViewDetails={handleViewDetails}
                showActions={activeTab !== 'history'}
              />
            ))}
          </div>
        )}
      </div>

      {/* Detail Modal */}
      <DelegationDetailModal
        delegation={selectedDelegation}
        isOpen={isDetailModalOpen}
        onClose={handleCloseDetailModal}
      />
    </div>
  );
}
