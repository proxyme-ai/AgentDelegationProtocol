import { useState, useEffect, useCallback, useRef } from 'react';
import type {
  Agent,
  Delegation,
  TokenInfo,
  SimulationScenario,
  SimulationResult,
  SystemStatusResponse,
  SystemActivity,
  DemoResult,
  AgentFilters,
  DelegationFilters,
  LogFilters,
  CreateAgentRequest,
  UpdateAgentRequest,
  CreateDelegationRequest,
  TokenIntrospectionRequest,
  TokenRevocationRequest
} from '../types';
import { APIException } from '../types';
import {
  agentAPI,
  delegationAPI,
  tokenAPI,
  demoAPI,
  simulationAPI,
  systemAPI
} from './api';

// ============================================================================
// HOOK TYPES
// ============================================================================

interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: APIException | null;
}

interface MutationState {
  loading: boolean;
  error: APIException | null;
}

// ============================================================================
// UTILITY HOOKS
// ============================================================================

/**
 * Generic hook for async data fetching with loading and error states
 */
function useAsyncData<T>(
  fetchFn: () => Promise<T>,
  dependencies: any[] = [],
  immediate: boolean = true
): AsyncState<T> & { refetch: () => Promise<void> } {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: immediate,
    error: null
  });

  const mountedRef = useRef(true);

  const fetchData = useCallback(async () => {
    if (!mountedRef.current) return;

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const data = await fetchFn();
      if (mountedRef.current) {
        setState({ data, loading: false, error: null });
      }
    } catch (error) {
      if (mountedRef.current) {
        const apiError = error instanceof APIException ? error : new APIException({
          error: 'Unknown error',
          message: error instanceof Error ? error.message : 'An unexpected error occurred',
          timestamp: new Date().toISOString()
        });
        setState(prev => ({ ...prev, loading: false, error: apiError }));
      }
    }
  }, dependencies);

  useEffect(() => {
    if (immediate) {
      fetchData();
    }
  }, [fetchData, immediate]);

  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

  return {
    ...state,
    refetch: fetchData
  };
}

/**
 * Generic hook for mutations (create, update, delete operations)
 */
function useMutation<TData, TVariables = void>(
  mutationFn: (variables: TVariables) => Promise<TData>
): MutationState & {
  mutate: (variables: TVariables) => Promise<TData>;
  reset: () => void;
} {
  const [state, setState] = useState<MutationState>({
    loading: false,
    error: null
  });

  const mutate = useCallback(async (variables: TVariables): Promise<TData> => {
    setState({ loading: true, error: null });

    try {
      const result = await mutationFn(variables);
      setState({ loading: false, error: null });
      return result;
    } catch (error) {
      const apiError = error instanceof APIException ? error : new APIException({
        error: 'Unknown error',
        message: error instanceof Error ? error.message : 'An unexpected error occurred',
        timestamp: new Date().toISOString()
      });
      setState({ loading: false, error: apiError });
      throw apiError;
    }
  }, [mutationFn]);

  const reset = useCallback(() => {
    setState({ loading: false, error: null });
  }, []);

  return {
    ...state,
    mutate,
    reset
  };
}

// ============================================================================
// AGENT HOOKS
// ============================================================================

/**
 * Hook to fetch agents list with filtering
 */
export function useAgents(filters: AgentFilters = {}, immediate: boolean = true) {
  return useAsyncData(
    () => agentAPI.list(filters),
    [filters.status, filters.search],
    immediate
  );
}

/**
 * Hook to fetch a single agent by ID
 */
export function useAgent(agentId: string | null, immediate: boolean = true) {
  return useAsyncData(
    () => agentId ? agentAPI.get(agentId) : Promise.resolve(null),
    [agentId],
    immediate && !!agentId
  );
}

/**
 * Hook to create a new agent
 */
export function useCreateAgent() {
  return useMutation<{ message: string; agent: Agent }, CreateAgentRequest>(
    (data) => agentAPI.create(data)
  );
}

/**
 * Hook to update an agent
 */
export function useUpdateAgent() {
  return useMutation<{ message: string; agent: Agent }, { agentId: string; data: UpdateAgentRequest }>(
    ({ agentId, data }) => agentAPI.update(agentId, data)
  );
}

/**
 * Hook to delete an agent
 */
export function useDeleteAgent() {
  return useMutation<{ message: string }, string>(
    (agentId) => agentAPI.delete(agentId)
  );
}

// ============================================================================
// DELEGATION HOOKS
// ============================================================================

/**
 * Hook to fetch delegations list with filtering
 */
export function useDelegations(filters: DelegationFilters = {}, immediate: boolean = true) {
  return useAsyncData(
    () => delegationAPI.list(filters),
    [filters.status, filters.agent_id, filters.user_id],
    immediate
  );
}

/**
 * Hook to fetch a single delegation by ID
 */
export function useDelegation(delegationId: string | null, immediate: boolean = true) {
  return useAsyncData(
    () => delegationId ? delegationAPI.get(delegationId) : Promise.resolve(null),
    [delegationId],
    immediate && !!delegationId
  );
}

/**
 * Hook to create a new delegation
 */
export function useCreateDelegation() {
  return useMutation<{ message: string; delegation: Delegation }, CreateDelegationRequest>(
    (data) => delegationAPI.create(data)
  );
}

/**
 * Hook to approve a delegation
 */
export function useApproveDelegation() {
  return useMutation<{ message: string; delegation: Delegation; delegation_token: string }, string>(
    (delegationId) => delegationAPI.approve(delegationId)
  );
}

/**
 * Hook to deny a delegation
 */
export function useDenyDelegation() {
  return useMutation<{ message: string; delegation: Delegation }, string>(
    (delegationId) => delegationAPI.deny(delegationId)
  );
}

/**
 * Hook to revoke a delegation
 */
export function useRevokeDelegation() {
  return useMutation<{ message: string }, string>(
    (delegationId) => delegationAPI.revoke(delegationId)
  );
}

// ============================================================================
// TOKEN HOOKS
// ============================================================================

/**
 * Hook to fetch active tokens
 */
export function useActiveTokens(immediate: boolean = true) {
  return useAsyncData(
    () => tokenAPI.listActive(),
    [],
    immediate
  );
}

/**
 * Hook to introspect a token
 */
export function useTokenIntrospection() {
  return useMutation<{ token_info: TokenInfo }, TokenIntrospectionRequest>(
    (data) => tokenAPI.introspect(data)
  );
}

/**
 * Hook to revoke a token
 */
export function useRevokeToken() {
  return useMutation<{ message: string }, TokenRevocationRequest>(
    (data) => tokenAPI.revoke(data)
  );
}

// ============================================================================
// DEMO & SIMULATION HOOKS
// ============================================================================

/**
 * Hook to run the demo flow
 */
export function useRunDemo() {
  return useMutation<{ demo_result: DemoResult }, void>(
    () => demoAPI.run()
  );
}

/**
 * Hook to fetch simulation scenarios
 */
export function useSimulationScenarios(immediate: boolean = true) {
  return useAsyncData(
    () => simulationAPI.listScenarios(),
    [],
    immediate
  );
}

/**
 * Hook to run a simulation scenario
 */
export function useRunSimulation() {
  return useMutation<{ simulation_result: SimulationResult }, string>(
    (scenarioId) => simulationAPI.runScenario(scenarioId)
  );
}

// ============================================================================
// SYSTEM HOOKS
// ============================================================================

/**
 * Hook to fetch system status
 */
export function useSystemStatus(immediate: boolean = true) {
  return useAsyncData(
    () => systemAPI.getStatus(),
    [],
    immediate
  );
}

/**
 * Hook to fetch system logs
 */
export function useSystemLogs(filters: LogFilters = {}, immediate: boolean = true) {
  return useAsyncData(
    () => systemAPI.getLogs(filters),
    [filters.limit],
    immediate
  );
}

// ============================================================================
// COMPOSITE HOOKS
// ============================================================================

/**
 * Hook that combines agents and delegations for dashboard overview
 */
export function useDashboardData() {
  const agents = useAgents();
  const delegations = useDelegations();
  const systemStatus = useSystemStatus();
  const activeTokens = useActiveTokens();

  const loading = agents.loading || delegations.loading || systemStatus.loading || activeTokens.loading;
  const error = agents.error || delegations.error || systemStatus.error || activeTokens.error;

  const refetchAll = useCallback(async () => {
    await Promise.all([
      agents.refetch(),
      delegations.refetch(),
      systemStatus.refetch(),
      activeTokens.refetch()
    ]);
  }, [agents.refetch, delegations.refetch, systemStatus.refetch, activeTokens.refetch]);

  return {
    agents: agents.data,
    delegations: delegations.data,
    systemStatus: systemStatus.data,
    activeTokens: activeTokens.data,
    loading,
    error,
    refetch: refetchAll
  };
}

/**
 * Hook for managing agent with its delegations
 */
export function useAgentWithDelegations(agentId: string | null) {
  const agent = useAgent(agentId);
  const delegations = useDelegations(
    agentId ? { agent_id: agentId } : {},
    !!agentId
  );

  const loading = agent.loading || delegations.loading;
  const error = agent.error || delegations.error;

  const refetchAll = useCallback(async () => {
    await Promise.all([
      agent.refetch(),
      delegations.refetch()
    ]);
  }, [agent.refetch, delegations.refetch]);

  return {
    agent: agent.data,
    delegations: delegations.data,
    loading,
    error,
    refetch: refetchAll
  };
}

/**
 * Hook for real-time polling of system data
 */
export function usePolling<T>(
  fetchFn: () => Promise<T>,
  interval: number = 5000,
  enabled: boolean = true
): AsyncState<T> & { refetch: () => Promise<void> } {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: true,
    error: null
  });

  const mountedRef = useRef(true);
  const intervalRef = useRef<number | null>(null);

  const fetchData = useCallback(async () => {
    if (!mountedRef.current) return;

    try {
      const data = await fetchFn();
      if (mountedRef.current) {
        setState(prev => ({ ...prev, data, loading: false, error: null }));
      }
    } catch (error) {
      if (mountedRef.current) {
        const apiError = error instanceof APIException ? error : new APIException({
          error: 'Unknown error',
          message: error instanceof Error ? error.message : 'An unexpected error occurred',
          timestamp: new Date().toISOString()
        });
        setState(prev => ({ ...prev, loading: false, error: apiError }));
      }
    }
  }, [fetchFn]);

  useEffect(() => {
    if (!enabled) return;

    // Initial fetch
    fetchData();

    // Set up polling
    intervalRef.current = setInterval(fetchData, interval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [fetchData, interval, enabled]);

  useEffect(() => {
    return () => {
      mountedRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return {
    ...state,
    refetch: fetchData
  };
}