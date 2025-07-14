import type {
  Agent,
  Delegation,
  TokenInfo,
  SimulationScenario,
  SimulationResult,
  SystemStatusResponse,
  LogsResponse,
  DemoResult,
  TokenIntrospectionResponse,
  AgentsResponse,
  DelegationsResponse,
  ActiveTokensResponse,
  CreateAgentRequest,
  UpdateAgentRequest,
  CreateDelegationRequest,
  TokenIntrospectionRequest,
  TokenRevocationRequest,
  AgentFilters,
  DelegationFilters,
  LogFilters,
  APIError
} from '../types';
import { APIException } from '../types';

// ============================================================================
// CONFIGURATION
// ============================================================================

export const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const DEFAULT_TIMEOUT = 10000; // 10 seconds
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Sleep utility for retry delays
 */
const sleep = (ms: number): Promise<void> => 
  new Promise(resolve => setTimeout(resolve, ms));

/**
 * Check if an error is retryable
 */
const isRetryableError = (error: any): boolean => {
  if (error instanceof APIException) {
    // Retry on server errors (5xx) but not client errors (4xx)
    return error.code >= 500;
  }
  
  // Retry on network errors
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return true;
  }
  
  return false;
};

/**
 * Build query string from filters
 */
const buildQueryString = (params: Record<string, any>): string => {
  const searchParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, String(value));
    }
  });
  
  const queryString = searchParams.toString();
  return queryString ? `?${queryString}` : '';
};

// ============================================================================
// CORE API CLIENT
// ============================================================================

class APIClient {
  private baseURL: string;
  private timeout: number;
  private authToken?: string;

  constructor(baseURL: string = BASE_URL, timeout: number = DEFAULT_TIMEOUT) {
    this.baseURL = baseURL;
    this.timeout = timeout;
  }

  /**
   * Set authentication token for requests
   */
  setAuthToken(token: string): void {
    this.authToken = token;
  }

  /**
   * Clear authentication token
   */
  clearAuthToken(): void {
    this.authToken = undefined;
  }

  /**
   * Create request headers with authentication and content type
   */
  private createHeaders(additionalHeaders: Record<string, string> = {}): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...additionalHeaders
    };

    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }

    return headers;
  }

  /**
   * Enhanced fetch with timeout, error handling, and retry logic
   */
  async fetchWithRetry<T>(
    url: string, 
    options: RequestInit = {}, 
    retries: number = MAX_RETRIES
  ): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(`${this.baseURL}${url}`, {
        ...options,
        headers: this.createHeaders(options.headers as Record<string, string>),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        let errorData: APIError;
        
        try {
          errorData = await response.json();
        } catch {
          // If JSON parsing fails, create a generic error
          errorData = {
            error: `HTTP ${response.status}`,
            message: response.statusText || 'Request failed',
            timestamp: new Date().toISOString()
          };
        }

        const apiError = new APIException(errorData, response.status);
        
        // Retry logic for retryable errors
        if (retries > 0 && isRetryableError(apiError)) {
          console.warn(`Request failed, retrying in ${RETRY_DELAY}ms... (${retries} retries left)`);
          await sleep(RETRY_DELAY);
          return this.fetchWithRetry<T>(url, options, retries - 1);
        }
        
        throw apiError;
      }

      return await response.json();
    } catch (error) {
      clearTimeout(timeoutId);
      
      // Handle timeout and network errors
      if (error instanceof DOMException && error.name === 'AbortError') {
        const timeoutError = new APIException({
          error: 'Request timeout',
          message: `Request timed out after ${this.timeout}ms`,
          timestamp: new Date().toISOString()
        }, 408);
        
        if (retries > 0) {
          console.warn(`Request timed out, retrying... (${retries} retries left)`);
          await sleep(RETRY_DELAY);
          return this.fetchWithRetry<T>(url, options, retries - 1);
        }
        
        throw timeoutError;
      }

      // Retry network errors
      if (retries > 0 && isRetryableError(error)) {
        console.warn(`Network error, retrying... (${retries} retries left)`);
        await sleep(RETRY_DELAY);
        return this.fetchWithRetry<T>(url, options, retries - 1);
      }

      throw error;
    }
  }

  /**
   * GET request
   */
  async get<T>(url: string): Promise<T> {
    return this.fetchWithRetry<T>(url, { method: 'GET' });
  }

  /**
   * POST request
   */
  async post<T>(url: string, data?: any): Promise<T> {
    return this.fetchWithRetry<T>(url, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined
    });
  }

  /**
   * PUT request
   */
  async put<T>(url: string, data?: any): Promise<T> {
    return this.fetchWithRetry<T>(url, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined
    });
  }

  /**
   * DELETE request
   */
  async delete<T>(url: string): Promise<T> {
    return this.fetchWithRetry<T>(url, { method: 'DELETE' });
  }
}

// Create singleton instance
const apiClient = new APIClient();

// ============================================================================
// AGENT MANAGEMENT API
// ============================================================================

export const agentAPI = {
  /**
   * List all agents with optional filtering
   */
  async list(filters: AgentFilters = {}): Promise<AgentsResponse> {
    const queryString = buildQueryString(filters);
    return apiClient.get<AgentsResponse>(`/api/agents${queryString}`);
  },

  /**
   * Create a new agent
   */
  async create(data: CreateAgentRequest): Promise<{ message: string; agent: Agent }> {
    return apiClient.post<{ message: string; agent: Agent }>('/api/agents', data);
  },

  /**
   * Get agent details by ID
   */
  async get(agentId: string): Promise<Agent> {
    return apiClient.get<Agent>(`/api/agents/${agentId}`);
  },

  /**
   * Update agent
   */
  async update(agentId: string, data: UpdateAgentRequest): Promise<{ message: string; agent: Agent }> {
    return apiClient.put<{ message: string; agent: Agent }>(`/api/agents/${agentId}`, data);
  },

  /**
   * Delete agent
   */
  async delete(agentId: string): Promise<{ message: string }> {
    return apiClient.delete<{ message: string }>(`/api/agents/${agentId}`);
  }
};

// ============================================================================
// DELEGATION MANAGEMENT API
// ============================================================================

export const delegationAPI = {
  /**
   * List delegations with optional filtering
   */
  async list(filters: DelegationFilters = {}): Promise<DelegationsResponse> {
    const queryString = buildQueryString(filters);
    return apiClient.get<DelegationsResponse>(`/api/delegations${queryString}`);
  },

  /**
   * Create a new delegation
   */
  async create(data: CreateDelegationRequest): Promise<{ message: string; delegation: Delegation }> {
    return apiClient.post<{ message: string; delegation: Delegation }>('/api/delegations', data);
  },

  /**
   * Get delegation details by ID
   */
  async get(delegationId: string): Promise<Delegation> {
    return apiClient.get<Delegation>(`/api/delegations/${delegationId}`);
  },

  /**
   * Approve a delegation
   */
  async approve(delegationId: string): Promise<{ message: string; delegation: Delegation; delegation_token: string }> {
    return apiClient.put<{ message: string; delegation: Delegation; delegation_token: string }>(`/api/delegations/${delegationId}/approve`);
  },

  /**
   * Deny a delegation
   */
  async deny(delegationId: string): Promise<{ message: string; delegation: Delegation }> {
    return apiClient.put<{ message: string; delegation: Delegation }>(`/api/delegations/${delegationId}/deny`);
  },

  /**
   * Revoke a delegation
   */
  async revoke(delegationId: string): Promise<{ message: string }> {
    return apiClient.delete<{ message: string }>(`/api/delegations/${delegationId}`);
  }
};

// ============================================================================
// TOKEN MANAGEMENT API
// ============================================================================

export const tokenAPI = {
  /**
   * List active tokens
   */
  async listActive(): Promise<ActiveTokensResponse> {
    return apiClient.get<ActiveTokensResponse>('/api/tokens/active');
  },

  /**
   * Introspect a token
   */
  async introspect(data: TokenIntrospectionRequest): Promise<TokenIntrospectionResponse> {
    return apiClient.post<TokenIntrospectionResponse>('/api/tokens/introspect', data);
  },

  /**
   * Revoke a token
   */
  async revoke(data: TokenRevocationRequest): Promise<{ message: string }> {
    return apiClient.post<{ message: string }>('/api/tokens/revoke', data);
  }
};

// ============================================================================
// DEMO & SIMULATION API
// ============================================================================

export const demoAPI = {
  /**
   * Run complete demo flow
   */
  async run(): Promise<{ demo_result: DemoResult }> {
    return apiClient.post<{ demo_result: DemoResult }>('/api/demo/run');
  }
};

export const simulationAPI = {
  /**
   * List available simulation scenarios
   */
  async listScenarios(): Promise<{ scenarios: SimulationScenario[] }> {
    return apiClient.get<{ scenarios: SimulationScenario[] }>('/api/simulate/scenarios');
  },

  /**
   * Run a specific simulation scenario
   */
  async runScenario(scenarioId: string): Promise<{ simulation_result: SimulationResult }> {
    return apiClient.post<{ simulation_result: SimulationResult }>(`/api/simulate/${scenarioId}`);
  }
};

// ============================================================================
// SYSTEM STATUS API
// ============================================================================

export const systemAPI = {
  /**
   * Get system status and statistics
   */
  async getStatus(): Promise<SystemStatusResponse> {
    return apiClient.get<SystemStatusResponse>('/api/status');
  },

  /**
   * Get system activity logs
   */
  async getLogs(filters: LogFilters = {}): Promise<LogsResponse> {
    const queryString = buildQueryString(filters);
    return apiClient.get<LogsResponse>(`/api/logs${queryString}`);
  }
};

// ============================================================================
// LEGACY COMPATIBILITY (for existing code)
// ============================================================================

/**
 * @deprecated Use agentAPI.list() instead
 */
export function getAgents(): Promise<AgentsResponse> {
  return agentAPI.list();
}

/**
 * @deprecated Use agentAPI.create() instead
 */
export function createAgent(data: CreateAgentRequest): Promise<{ message: string; agent: Agent }> {
  return agentAPI.create(data);
}

/**
 * @deprecated Use delegationAPI.list() instead
 */
export function getDelegations(): Promise<DelegationsResponse> {
  return delegationAPI.list();
}

/**
 * @deprecated Use delegationAPI.approve() instead
 */
export function approveDelegation(id: string): Promise<{ message: string; delegation: Delegation; delegation_token: string }> {
  return delegationAPI.approve(id);
}

/**
 * @deprecated Use delegationAPI.deny() instead
 */
export function denyDelegation(id: string): Promise<{ message: string; delegation: Delegation }> {
  return delegationAPI.deny(id);
}

// ============================================================================
// EXPORTS
// ============================================================================

export { apiClient, APIException };
export default apiClient;
