// ============================================================================
// API SERVICE LAYER EXPORTS
// ============================================================================

// Core API client and services
export {
  apiClient,
  agentAPI,
  delegationAPI,
  tokenAPI,
  demoAPI,
  simulationAPI,
  systemAPI
} from './api';

// Legacy compatibility exports
export {
  getAgents,
  createAgent,
  getDelegations,
  approveDelegation,
  denyDelegation
} from './api';

// React hooks for data fetching and mutations
export {
  // Agent hooks
  useAgents,
  useAgent,
  useCreateAgent,
  useUpdateAgent,
  useDeleteAgent,
  
  // Delegation hooks
  useDelegations,
  useDelegation,
  useCreateDelegation,
  useApproveDelegation,
  useDenyDelegation,
  useRevokeDelegation,
  
  // Token hooks
  useActiveTokens,
  useTokenIntrospection,
  useRevokeToken,
  
  // Demo & simulation hooks
  useRunDemo,
  useSimulationScenarios,
  useRunSimulation,
  
  // System hooks
  useSystemStatus,
  useSystemLogs,
  
  // Composite hooks
  useDashboardData,
  useAgentWithDelegations,
  usePolling
} from './hooks';

// Utility functions
export {
  // Error handling
  formatAPIError,
  isNetworkError,
  isTimeoutError,
  isRetryableError,
  
  // Token utilities
  parseJWTPayload,
  isTokenExpired,
  getTokenExpiryTime,
  getTimeToExpiry,
  formatTokenForDisplay,
  getTokenType,
  getTokenScopes,
  createTokenInfo,
  
  // Validation utilities
  validateAgentName,
  validateScopes,
  validateUserId,
  
  // Formatting utilities
  formatTimestamp,
  formatRelativeTime,
  formatDuration,
  getStatusColor,
  debounce,
  deepClone
} from './utils';

// Re-export types for convenience
export type {
  Agent,
  Delegation,
  TokenInfo,
  SimulationScenario,
  SimulationResult,
  SystemStats,
  SystemActivity,
  APIResponse,
  ListResponse,
  AgentsResponse,
  DelegationsResponse,
  ActiveTokensResponse,
  SystemStatusResponse,
  LogsResponse,
  DemoResult,
  TokenIntrospectionResponse,
  APIError,
  APIException,
  CreateAgentRequest,
  UpdateAgentRequest,
  CreateDelegationRequest,
  TokenIntrospectionRequest,
  TokenRevocationRequest,
  AgentFilters,
  DelegationFilters,
  LogFilters
} from '../types';