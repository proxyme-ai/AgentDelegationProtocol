// ============================================================================
// CORE DATA MODELS
// ============================================================================

export interface Agent {
  id: string;
  name: string;
  description?: string;
  scopes: string[];
  status: 'active' | 'inactive' | 'suspended';
  createdAt: string;
  lastUsed?: string;
  delegationCount: number;
  delegations?: Delegation[];
}

export interface Delegation {
  id: string;
  agentId: string;
  agentName: string;
  userId: string;
  scopes: string[];
  status: 'pending' | 'approved' | 'denied' | 'expired' | 'revoked';
  createdAt: string;
  approvedAt?: string;
  expiresAt: string;
  delegationToken?: string;
  accessToken?: string;
}

export interface TokenInfo {
  token: string;
  type: 'delegation' | 'access';
  subject: string;
  expires_at: string;
  issued_at: string;
  scopes: string[];
  time_to_expiry_seconds: number;
  claims?: Record<string, any>;
  isValid: boolean;
}

export interface SimulationScenario {
  id: string;
  name: string;
  description: string;
}

export interface SimulationStep {
  step: number;
  action: string;
  result: string;
}

export interface SimulationResult {
  scenario: string;
  status: 'success' | 'expected_failure' | 'error';
  steps: SimulationStep[];
  message: string;
}

export interface SystemStats {
  total_agents: number;
  active_agents: number;
  total_delegations: number;
  active_delegations: number;
  pending_delegations: number;
  active_tokens: number;
}

export interface SystemActivity {
  id: string;
  timestamp: string;
  action: string;
  details: string;
  user_id?: string;
  agent_id?: string;
}

// ============================================================================
// API RESPONSE TYPES
// ============================================================================

export interface APIResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

export interface ListResponse<T> {
  items: T[];
  total: number;
  timestamp: string;
}

export interface AgentsResponse extends ListResponse<Agent> {
  agents: Agent[];
}

export interface DelegationsResponse extends ListResponse<Delegation> {
  delegations: Delegation[];
}

export interface ActiveTokensResponse extends ListResponse<TokenInfo> {
  active_tokens: TokenInfo[];
}

export interface SystemStatusResponse {
  status: string;
  service: string;
  version: string;
  timestamp: string;
  statistics: SystemStats;
}

export interface LogsResponse extends ListResponse<SystemActivity> {
  logs: SystemActivity[];
}

export interface DemoResult {
  step: string;
  delegation_token: string;
  access_token: string;
  delegation_id: string;
  agent_id: string;
  user_id: string;
  scopes: string[];
  message: string;
}

export interface TokenIntrospectionResponse {
  token_info: TokenInfo;
}

// ============================================================================
// API ERROR TYPES
// ============================================================================

export interface APIError {
  error: string;
  message: string;
  code?: number;
  details?: Record<string, any>;
  timestamp: string;
  missing_fields?: string[];
}

export class APIException extends Error {
  public readonly code: number;
  public readonly details?: Record<string, any>;
  public readonly timestamp: string;

  constructor(error: APIError, status: number = 500) {
    super(error.message || error.error);
    this.name = 'APIException';
    this.code = status;
    this.details = error.details;
    this.timestamp = error.timestamp;
  }
}

// ============================================================================
// REQUEST TYPES
// ============================================================================

export interface CreateAgentRequest {
  name: string;
  description?: string;
  scopes?: string[];
}

export interface UpdateAgentRequest {
  name?: string;
  description?: string;
  scopes?: string[];
  status?: 'active' | 'inactive' | 'suspended';
}

export interface CreateDelegationRequest {
  agent_id: string;
  user_id: string;
  scopes: string[];
}

export interface TokenIntrospectionRequest {
  token: string;
}

export interface TokenRevocationRequest {
  token: string;
}

// ============================================================================
// FILTER AND QUERY TYPES
// ============================================================================

export interface AgentFilters {
  status?: 'active' | 'inactive' | 'suspended';
  search?: string;
}

export interface DelegationFilters {
  status?: 'pending' | 'approved' | 'denied' | 'expired' | 'revoked';
  agent_id?: string;
  user_id?: string;
}

export interface LogFilters {
  limit?: number;
}
