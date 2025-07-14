import { useState, useEffect } from 'react';
import type { Delegation, TokenInfo } from '../types';
import { tokenAPI } from '../services/api';

interface DelegationDetailModalProps {
  delegation: Delegation | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function DelegationDetailModal({ 
  delegation, 
  isOpen, 
  onClose 
}: DelegationDetailModalProps) {
  const [delegationTokenInfo, setDelegationTokenInfo] = useState<TokenInfo | null>(null);
  const [accessTokenInfo, setAccessTokenInfo] = useState<TokenInfo | null>(null);
  const [isLoadingTokens, setIsLoadingTokens] = useState(false);

  useEffect(() => {
    if (delegation && isOpen) {
      loadTokenInfo();
    }
  }, [delegation, isOpen]);

  const loadTokenInfo = async () => {
    if (!delegation) return;
    
    setIsLoadingTokens(true);
    try {
      // Load delegation token info if available
      if (delegation.delegationToken) {
        try {
          const response = await tokenAPI.introspect({ token: delegation.delegationToken });
          setDelegationTokenInfo(response.token_info);
        } catch (error) {
          console.error('Failed to introspect delegation token:', error);
        }
      }

      // Load access token info if available
      if (delegation.accessToken) {
        try {
          const response = await tokenAPI.introspect({ token: delegation.accessToken });
          setAccessTokenInfo(response.token_info);
        } catch (error) {
          console.error('Failed to introspect access token:', error);
        }
      }
    } finally {
      setIsLoadingTokens(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatTimeRemaining = (expiresAt: string) => {
    const now = Date.now();
    const expiry = new Date(expiresAt).getTime();
    const diff = expiry - now;
    
    if (diff <= 0) return 'Expired';
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) {
      return `${hours}h ${minutes}m remaining`;
    } else {
      return `${minutes}m remaining`;
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const TokenInfoSection = ({ 
    title, 
    tokenInfo, 
    token 
  }: { 
    title: string; 
    tokenInfo: TokenInfo | null; 
    token?: string; 
  }) => (
    <div className="space-y-3">
      <h4 className="font-semibold text-lg">{title}</h4>
      {tokenInfo ? (
        <div className="bg-base-200 p-4 rounded-lg space-y-3">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-semibold">Type:</span>
              <p className="capitalize">{tokenInfo.type}</p>
            </div>
            <div>
              <span className="font-semibold">Subject:</span>
              <p>{tokenInfo.subject}</p>
            </div>
            <div>
              <span className="font-semibold">Issued At:</span>
              <p>{formatDate(tokenInfo.issued_at)}</p>
            </div>
            <div>
              <span className="font-semibold">Expires At:</span>
              <p>{formatDate(tokenInfo.expires_at)}</p>
            </div>
            <div>
              <span className="font-semibold">Status:</span>
              <div className={`badge ${tokenInfo.isValid ? 'badge-success' : 'badge-error'}`}>
                {tokenInfo.isValid ? 'Valid' : 'Invalid'}
              </div>
            </div>
            <div>
              <span className="font-semibold">Time Remaining:</span>
              <p>{formatTimeRemaining(tokenInfo.expires_at)}</p>
            </div>
          </div>
          
          <div>
            <span className="font-semibold">Scopes:</span>
            <div className="flex flex-wrap gap-1 mt-1">
              {tokenInfo.scopes.map((scope, index) => (
                <span key={index} className="badge badge-outline badge-sm">
                  {scope}
                </span>
              ))}
            </div>
          </div>

          {tokenInfo.claims && Object.keys(tokenInfo.claims).length > 0 && (
            <div>
              <span className="font-semibold">Claims:</span>
              <div className="bg-base-300 p-3 rounded mt-1 text-xs font-mono">
                <pre>{JSON.stringify(tokenInfo.claims, null, 2)}</pre>
              </div>
            </div>
          )}

          {token && (
            <div>
              <span className="font-semibold">Token:</span>
              <div className="flex items-center gap-2 mt-1">
                <input 
                  type="text" 
                  value={token} 
                  readOnly 
                  className="input input-sm input-bordered flex-1 font-mono text-xs"
                />
                <button 
                  className="btn btn-sm btn-outline"
                  onClick={() => copyToClipboard(token)}
                >
                  Copy
                </button>
              </div>
            </div>
          )}
        </div>
      ) : token ? (
        <div className="bg-base-200 p-4 rounded-lg">
          <div className="flex items-center gap-2">
            <input 
              type="text" 
              value={token} 
              readOnly 
              className="input input-sm input-bordered flex-1 font-mono text-xs"
            />
            <button 
              className="btn btn-sm btn-outline"
              onClick={() => copyToClipboard(token)}
            >
              Copy
            </button>
          </div>
          <p className="text-sm text-base-content/70 mt-2">
            Token introspection not available
          </p>
        </div>
      ) : (
        <p className="text-base-content/70">No token available</p>
      )}
    </div>
  );

  if (!delegation) return null;

  return (
    <div className={`modal ${isOpen ? 'modal-open' : ''}`}>
      <div className="modal-box max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h3 className="font-bold text-xl">Delegation Details</h3>
            <p className="text-base-content/70">ID: {delegation.id}</p>
          </div>
          <button 
            className="btn btn-sm btn-circle btn-ghost"
            onClick={onClose}
          >
            ✕
          </button>
        </div>

        <div className="space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="font-semibold text-lg">Basic Information</h4>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="font-semibold">Agent Name:</span>
                  <p>{delegation.agentName}</p>
                </div>
                <div>
                  <span className="font-semibold">Agent ID:</span>
                  <p className="font-mono">{delegation.agentId}</p>
                </div>
                <div>
                  <span className="font-semibold">User ID:</span>
                  <p className="font-mono">{delegation.userId}</p>
                </div>
                <div>
                  <span className="font-semibold">Status:</span>
                  <div className={`badge ${
                    delegation.status === 'approved' ? 'badge-success' :
                    delegation.status === 'pending' ? 'badge-warning' :
                    delegation.status === 'denied' ? 'badge-error' :
                    delegation.status === 'expired' ? 'badge-neutral' :
                    'badge-error'
                  }`}>
                    {delegation.status.toUpperCase()}
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <h4 className="font-semibold text-lg">Timeline</h4>
              <div className="space-y-2 text-sm">
                <div>
                  <span className="font-semibold">Created:</span>
                  <p>{formatDate(delegation.createdAt)}</p>
                </div>
                {delegation.approvedAt && (
                  <div>
                    <span className="font-semibold">Approved:</span>
                    <p>{formatDate(delegation.approvedAt)}</p>
                  </div>
                )}
                <div>
                  <span className="font-semibold">Expires:</span>
                  <p>{formatDate(delegation.expiresAt)}</p>
                </div>
                <div>
                  <span className="font-semibold">Time Remaining:</span>
                  <p>{formatTimeRemaining(delegation.expiresAt)}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Scopes */}
          <div className="space-y-3">
            <h4 className="font-semibold text-lg">Scopes</h4>
            <div className="flex flex-wrap gap-2">
              {delegation.scopes.map((scope, index) => (
                <span key={index} className="badge badge-outline">
                  {scope}
                </span>
              ))}
            </div>
          </div>

          {/* Token Information */}
          {isLoadingTokens ? (
            <div className="flex justify-center py-8">
              <span className="loading loading-spinner loading-lg"></span>
            </div>
          ) : (
            <div className="space-y-6">
              <TokenInfoSection 
                title="Delegation Token" 
                tokenInfo={delegationTokenInfo}
                token={delegation.delegationToken}
              />
              
              <TokenInfoSection 
                title="Access Token" 
                tokenInfo={accessTokenInfo}
                token={delegation.accessToken}
              />
            </div>
          )}
        </div>

        <div className="modal-action">
          <button className="btn" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}