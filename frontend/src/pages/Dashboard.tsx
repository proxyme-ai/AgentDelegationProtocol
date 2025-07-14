import { useState, useCallback } from 'react';
import { useDashboardData, useRunDemo, useSystemLogs, usePolling } from '../services/hooks';
import { systemAPI } from '../services/api';
import { useToast, ToastContainer } from '../components/Toast';
import { Loading, LoadingCard } from '../components/Loading';
import type { DemoResult, SystemActivity } from '../types';

// ============================================================================
// DASHBOARD COMPONENTS
// ============================================================================

interface StatsCardProps {
  title: string;
  value: number | string;
  icon: string;
  color: string;
  subtitle?: string;
}

function StatsCard({ title, value, icon, color, subtitle }: StatsCardProps) {
  return (
    <div className="card bg-base-100 shadow-sm">
      <div className="card-body p-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-base-content/70">{title}</h3>
            <p className={`text-2xl font-bold ${color}`}>{value}</p>
            {subtitle && <p className="text-xs text-base-content/50">{subtitle}</p>}
          </div>
          <div className={`text-3xl ${color}`}>{icon}</div>
        </div>
      </div>
    </div>
  );
}

interface DemoStepProps {
  step: number;
  title: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  result?: string;
}

function DemoStep({ step, title, description, status, result }: DemoStepProps) {
  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'running':
        return '⏳';
      case 'error':
        return '❌';
      default:
        return '⚪';
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'text-success';
      case 'running':
        return 'text-warning';
      case 'error':
        return 'text-error';
      default:
        return 'text-base-content/50';
    }
  };

  return (
    <div className="flex items-start space-x-3 p-3 rounded-lg bg-base-200/50">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-base-100 flex items-center justify-center text-sm font-bold">
        {step}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center space-x-2">
          <h4 className="font-medium">{title}</h4>
          <span className={`text-lg ${getStatusColor()}`}>{getStatusIcon()}</span>
        </div>
        <p className="text-sm text-base-content/70 mt-1">{description}</p>
        {result && status === 'completed' && (
          <div className="mt-2 p-2 bg-base-100 rounded text-xs font-mono text-success">
            {result}
          </div>
        )}
        {status === 'running' && (
          <div className="mt-2">
            <div className="loading loading-dots loading-sm"></div>
          </div>
        )}
      </div>
    </div>
  );
}

interface ActivityItemProps {
  activity: SystemActivity;
}

function ActivityItem({ activity }: ActivityItemProps) {
  const getActionIcon = (action: string) => {
    if (action.includes('create') || action.includes('register')) return '➕';
    if (action.includes('approve')) return '✅';
    if (action.includes('deny') || action.includes('revoke')) return '❌';
    if (action.includes('token')) return '🔑';
    if (action.includes('delegation')) return '🤝';
    return '📝';
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="flex items-start space-x-3 p-3 hover:bg-base-200/50 rounded-lg transition-colors">
      <div className="flex-shrink-0 text-lg">
        {getActionIcon(activity.action)}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium">{activity.action}</p>
        <p className="text-xs text-base-content/70 mt-1">{activity.details}</p>
        <div className="flex items-center space-x-2 mt-1">
          <span className="text-xs text-base-content/50">
            {formatTimestamp(activity.timestamp)}
          </span>
          {activity.user_id && (
            <span className="text-xs bg-primary/20 text-primary px-1 rounded">
              User: {activity.user_id}
            </span>
          )}
          {activity.agent_id && (
            <span className="text-xs bg-secondary/20 text-secondary px-1 rounded">
              Agent: {activity.agent_id}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// MAIN DASHBOARD COMPONENT
// ============================================================================

export default function Dashboard() {
  const [demoSteps, setDemoSteps] = useState<Array<{
    step: number;
    action: string;
    result: string;
    status: 'pending' | 'running' | 'completed' | 'error';
  }>>([]);
  const [demoResult, setDemoResult] = useState<DemoResult | null>(null);
  const [activityFilter, setActivityFilter] = useState<string>('');
  
  // Toast notifications
  const toast = useToast();

  // Fetch dashboard data with real-time updates
  const { 
    agents, 
    delegations, 
    systemStatus, 
    activeTokens, 
    loading: dashboardLoading, 
    error: dashboardError,
    refetch: refetchDashboard 
  } = useDashboardData();

  // Poll system logs for activity feed
  const { 
    data: logsData, 
    loading: logsLoading 
  } = usePolling(
    () => systemAPI.getLogs({ limit: 20 }),
    5000, // Poll every 5 seconds
    true
  );

  // Demo execution hook
  const { mutate: runDemo, loading: demoLoading, error: demoError } = useRunDemo();

  // Handle demo execution with step-by-step visualization
  const handleRunDemo = useCallback(async () => {
    const steps = [
      { step: 1, action: 'Initialize Demo', result: 'Setting up demo environment...' },
      { step: 2, action: 'Create Agent', result: 'Registering demo agent...' },
      { step: 3, action: 'Request Delegation', result: 'Creating delegation request...' },
      { step: 4, action: 'Approve Delegation', result: 'Processing delegation approval...' },
      { step: 5, action: 'Generate Tokens', result: 'Creating delegation and access tokens...' },
      { step: 6, action: 'Access Resource', result: 'Testing resource access with tokens...' }
    ];

    setDemoSteps(steps.map(step => ({ ...step, status: 'pending' as const })));
    setDemoResult(null);

    try {
      // Simulate step-by-step execution
      for (let i = 0; i < steps.length; i++) {
        setDemoSteps(prev => prev.map((step, idx) => ({
          ...step,
          status: idx === i ? 'running' : idx < i ? 'completed' : 'pending'
        })));

        // Add delay for visualization
        await new Promise(resolve => setTimeout(resolve, 1000));
      }

      // Run actual demo
      const result = await runDemo();
      
      setDemoSteps(prev => prev.map(step => ({ ...step, status: 'completed' as const })));
      setDemoResult(result.demo_result);
      
      // Show success notification
      toast.success(
        'Demo Completed Successfully!',
        'The delegation protocol flow has been executed successfully.'
      );
      
      // Refresh dashboard data after demo
      await refetchDashboard();
    } catch (error) {
      setDemoSteps(prev => prev.map((step, idx) => ({
        ...step,
        status: idx < prev.findIndex(s => s.status === 'running') ? 'completed' : 
                idx === prev.findIndex(s => s.status === 'running') ? 'error' : 'pending'
      })));
      
      // Show error notification
      toast.error(
        'Demo Failed',
        error instanceof Error ? error.message : 'An unexpected error occurred during demo execution.'
      );
    }
  }, [runDemo, refetchDashboard]);

  // Filter activities
  const filteredActivities = logsData?.logs?.filter(activity => 
    !activityFilter || 
    activity.action.toLowerCase().includes(activityFilter.toLowerCase()) ||
    activity.details.toLowerCase().includes(activityFilter.toLowerCase())
  ) || [];

  if (dashboardLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-center h-64">
          <div className="loading loading-spinner loading-lg"></div>
        </div>
      </div>
    );
  }

  if (dashboardError) {
    return (
      <div className="p-6">
        <div className="alert alert-error">
          <span>Failed to load dashboard data: {dashboardError.message}</span>
        </div>
      </div>
    );
  }

  const stats = systemStatus?.statistics;

  return (
    <>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Agent Delegation Protocol</h1>
            <p className="text-base-content/70 mt-1">
              Comprehensive dashboard for managing AI agent delegations and protocol demonstration
            </p>
          </div>
          <div className="badge badge-primary badge-lg">
            {systemStatus?.status || 'Unknown'} Status
          </div>
        </div>

      {/* System Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Total Agents"
          value={stats?.total_agents || 0}
          icon="🤖"
          color="text-primary"
          subtitle={`${stats?.active_agents || 0} active`}
        />
        <StatsCard
          title="Delegations"
          value={stats?.total_delegations || 0}
          icon="🤝"
          color="text-secondary"
          subtitle={`${stats?.pending_delegations || 0} pending`}
        />
        <StatsCard
          title="Active Tokens"
          value={stats?.active_tokens || 0}
          icon="🔑"
          color="text-accent"
          subtitle="Currently valid"
        />
        <StatsCard
          title="System Health"
          value={systemStatus?.status === 'healthy' ? '100%' : 'Issues'}
          icon="💚"
          color={systemStatus?.status === 'healthy' ? 'text-success' : 'text-warning'}
          subtitle={systemStatus?.service || 'Unknown'}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Live Demo Section */}
        <div className="card bg-base-100 shadow">
          <div className="card-body">
            <div className="flex items-center justify-between mb-4">
              <h2 className="card-title">🚀 Live Protocol Demo</h2>
              <button
                className={`btn btn-primary ${demoLoading ? 'loading' : ''}`}
                onClick={handleRunDemo}
                disabled={demoLoading}
              >
                {demoLoading ? 'Running...' : 'Run Demo'}
              </button>
            </div>
            
            <p className="text-sm text-base-content/70 mb-4">
              Experience the complete delegation flow from agent registration to resource access
            </p>

            {demoError && (
              <div className="alert alert-error mb-4">
                <span>Demo failed: {demoError.message}</span>
              </div>
            )}

            <div className="space-y-3">
              {demoSteps.length > 0 ? (
                demoSteps.map((step, idx) => (
                  <DemoStep
                    key={idx}
                    step={step.step}
                    title={step.action}
                    description={step.result}
                    status={step.status}
                    result={step.status === 'completed' ? 'Success' : undefined}
                  />
                ))
              ) : (
                <div className="text-center py-8 text-base-content/50">
                  <p>Click "Run Demo" to see the protocol in action</p>
                </div>
              )}
            </div>

            {demoResult && (
              <div className="mt-4 p-4 bg-success/10 border border-success/20 rounded-lg">
                <h3 className="font-semibold text-success mb-2">Demo Completed Successfully!</h3>
                <div className="text-sm space-y-1">
                  <p><strong>Agent ID:</strong> {demoResult.agent_id}</p>
                  <p><strong>Delegation ID:</strong> {demoResult.delegation_id}</p>
                  <p><strong>Scopes:</strong> {demoResult.scopes.join(', ')}</p>
                  <p><strong>Message:</strong> {demoResult.message}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Recent Activity Feed */}
        <div className="card bg-base-100 shadow">
          <div className="card-body">
            <div className="flex items-center justify-between mb-4">
              <h2 className="card-title">📊 Recent Activity</h2>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  placeholder="Filter activities..."
                  className="input input-sm input-bordered"
                  value={activityFilter}
                  onChange={(e) => setActivityFilter(e.target.value)}
                />
                {logsLoading && <div className="loading loading-spinner loading-sm"></div>}
              </div>
            </div>

            <div className="space-y-2 max-h-96 overflow-y-auto">
              {filteredActivities.length > 0 ? (
                filteredActivities.map((activity) => (
                  <ActivityItem key={activity.id} activity={activity} />
                ))
              ) : (
                <div className="text-center py-8 text-base-content/50">
                  <p>No recent activity found</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions & Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pending Delegations */}
        <div className="card bg-base-100 shadow">
          <div className="card-body">
            <h3 className="card-title text-lg">⏳ Pending Delegations</h3>
            <div className="space-y-2">
              {delegations?.delegations?.filter(d => d.status === 'pending').slice(0, 3).map((delegation) => (
                <div key={delegation.id} className="flex items-center justify-between p-2 bg-base-200 rounded">
                  <div>
                    <p className="font-medium text-sm">{delegation.agentName}</p>
                    <p className="text-xs text-base-content/70">{delegation.scopes.join(', ')}</p>
                  </div>
                  <div className="badge badge-warning badge-sm">Pending</div>
                </div>
              )) || (
                <p className="text-sm text-base-content/50">No pending delegations</p>
              )}
            </div>
          </div>
        </div>

        {/* Active Agents */}
        <div className="card bg-base-100 shadow">
          <div className="card-body">
            <h3 className="card-title text-lg">🤖 Active Agents</h3>
            <div className="space-y-2">
              {agents?.agents?.filter(a => a.status === 'active').slice(0, 3).map((agent) => (
                <div key={agent.id} className="flex items-center justify-between p-2 bg-base-200 rounded">
                  <div>
                    <p className="font-medium text-sm">{agent.name}</p>
                    <p className="text-xs text-base-content/70">{agent.delegationCount} delegations</p>
                  </div>
                  <div className="badge badge-success badge-sm">Active</div>
                </div>
              )) || (
                <p className="text-sm text-base-content/50">No active agents</p>
              )}
            </div>
          </div>
        </div>

        {/* Token Status */}
        <div className="card bg-base-100 shadow">
          <div className="card-body">
            <h3 className="card-title text-lg">🔑 Token Status</h3>
            <div className="space-y-2">
              {activeTokens?.active_tokens?.slice(0, 3).map((token, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 bg-base-200 rounded">
                  <div>
                    <p className="font-medium text-sm">{token.type} token</p>
                    <p className="text-xs text-base-content/70">
                      Expires in {Math.floor(token.time_to_expiry_seconds / 60)}m
                    </p>
                  </div>
                  <div className={`badge badge-sm ${token.isValid ? 'badge-success' : 'badge-error'}`}>
                    {token.isValid ? 'Valid' : 'Invalid'}
                  </div>
                </div>
              )) || (
                <p className="text-sm text-base-content/50">No active tokens</p>
              )}
            </div>
          </div>
        </div>
      </div>
      </div>
      
      {/* Toast Notifications */}
      <ToastContainer messages={toast.messages} onClose={toast.removeToast} />
    </>
  );
}
