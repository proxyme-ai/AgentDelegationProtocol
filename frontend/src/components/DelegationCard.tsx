import { useState } from 'react';
import type { Delegation } from '../types';
import { delegationAPI } from '../services/api';

interface DelegationCardProps {
  delegation: Delegation;
  onUpdate: () => void;
  onViewDetails: (delegation: Delegation) => void;
  showActions?: boolean;
}

export default function DelegationCard({ 
  delegation, 
  onUpdate, 
  onViewDetails, 
  showActions = true 
}: DelegationCardProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleApprove = async () => {
    setIsLoading(true);
    try {
      await delegationAPI.approve(delegation.id);
      onUpdate();
    } catch (error) {
      console.error('Failed to approve delegation:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeny = async () => {
    setIsLoading(true);
    try {
      await delegationAPI.deny(delegation.id);
      onUpdate();
    } catch (error) {
      console.error('Failed to deny delegation:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRevoke = async () => {
    setIsLoading(true);
    try {
      await delegationAPI.revoke(delegation.id);
      onUpdate();
    } catch (error) {
      console.error('Failed to revoke delegation:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusClasses = {
      pending: 'badge-warning',
      approved: 'badge-success',
      denied: 'badge-error',
      expired: 'badge-neutral',
      revoked: 'badge-error'
    };
    
    return (
      <div className={`badge ${statusClasses[status as keyof typeof statusClasses] || 'badge-neutral'}`}>
        {status.toUpperCase()}
      </div>
    );
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const isExpiringSoon = () => {
    if (!delegation.expiresAt) return false;
    const expiryTime = new Date(delegation.expiresAt).getTime();
    const now = Date.now();
    const oneHour = 60 * 60 * 1000;
    return expiryTime - now < oneHour && expiryTime > now;
  };

  return (
    <div className="card bg-base-100 shadow-md hover:shadow-lg transition-shadow">
      <div className="card-body">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="card-title text-lg">{delegation.agentName}</h3>
            <p className="text-sm text-base-content/70">Agent ID: {delegation.agentId}</p>
            <p className="text-sm text-base-content/70">User ID: {delegation.userId}</p>
          </div>
          <div className="flex flex-col items-end gap-2">
            {getStatusBadge(delegation.status)}
            {isExpiringSoon() && (
              <div className="badge badge-warning badge-sm">
                Expiring Soon
              </div>
            )}
          </div>
        </div>

        <div className="space-y-2 mb-4">
          <div>
            <span className="font-semibold text-sm">Scopes:</span>
            <div className="flex flex-wrap gap-1 mt-1">
              {delegation.scopes.map((scope, index) => (
                <span key={index} className="badge badge-outline badge-sm">
                  {scope}
                </span>
              ))}
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-semibold">Created:</span>
              <p className="text-base-content/70">{formatDate(delegation.createdAt)}</p>
            </div>
            <div>
              <span className="font-semibold">Expires:</span>
              <p className="text-base-content/70">{formatDate(delegation.expiresAt)}</p>
            </div>
          </div>

          {delegation.approvedAt && (
            <div className="text-sm">
              <span className="font-semibold">Approved:</span>
              <p className="text-base-content/70">{formatDate(delegation.approvedAt)}</p>
            </div>
          )}
        </div>

        <div className="card-actions justify-between">
          <button 
            className="btn btn-outline btn-sm"
            onClick={() => onViewDetails(delegation)}
          >
            View Details
          </button>
          
          {showActions && (
            <div className="flex gap-2">
              {delegation.status === 'pending' && (
                <>
                  <button 
                    className={`btn btn-success btn-sm ${isLoading ? 'loading' : ''}`}
                    onClick={handleApprove}
                    disabled={isLoading}
                  >
                    Approve
                  </button>
                  <button 
                    className={`btn btn-error btn-sm ${isLoading ? 'loading' : ''}`}
                    onClick={handleDeny}
                    disabled={isLoading}
                  >
                    Deny
                  </button>
                </>
              )}
              
              {delegation.status === 'approved' && (
                <button 
                  className={`btn btn-warning btn-sm ${isLoading ? 'loading' : ''}`}
                  onClick={handleRevoke}
                  disabled={isLoading}
                >
                  Revoke
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}