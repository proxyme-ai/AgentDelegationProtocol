# Agent Delegation Protocol - API Documentation

This document describes the enhanced API endpoints added to support the frontend application.

## Overview

The Agent Delegation Protocol now includes a comprehensive REST API that provides:
- Agent management (CRUD operations)
- Delegation management and approval workflow
- Token management and introspection
- Demo and simulation capabilities
- System status and monitoring

## Base URLs

- **Authorization Server**: `http://localhost:5000`
- **Resource Server**: `http://localhost:6000`
- **API Server**: `http://localhost:7000`

## Authentication

Most endpoints require proper authentication. The API uses JWT tokens for authentication and authorization.

## Agent Management Endpoints

### List Agents
```http
GET /api/agents
```

Query Parameters:
- `status` (optional): Filter by agent status (`active`, `inactive`, `suspended`)
- `search` (optional): Search agents by name or description

Response:
```json
{
  "agents": [
    {
      "id": "agent-12345",
      "name": "Calendar Agent",
      "description": "Manages calendar operations",
      "scopes": ["read:calendar", "write:calendar"],
      "status": "active",
      "created_at": "2025-01-01T00:00:00.000000",
      "last_used": "2025-01-01T12:00:00.000000",
      "delegation_count": 5
    }
  ],
  "total": 1,
  "timestamp": "2025-01-01T12:00:00.000000"
}
```

### Create Agent
```http
POST /api/agents
Content-Type: application/json

{
  "name": "New Agent",
  "description": "Agent description",
  "scopes": ["read:data", "write:data"],
  "status": "active"
}
```

### Get Agent Details
```http
GET /api/agents/{agent_id}
```

### Update Agent
```http
PUT /api/agents/{agent_id}
Content-Type: application/json

{
  "name": "Updated Agent Name",
  "description": "Updated description",
  "scopes": ["read:data"],
  "status": "inactive"
}
```

### Delete Agent
```http
DELETE /api/agents/{agent_id}
```

## Delegation Management Endpoints

### List Delegations
```http
GET /api/delegations
```

Query Parameters:
- `status` (optional): Filter by delegation status
- `agent_id` (optional): Filter by agent ID
- `user_id` (optional): Filter by user ID

### Create Delegation
```http
POST /api/delegations
Content-Type: application/json

{
  "agent_id": "agent-12345",
  "user_id": "alice",
  "scopes": ["read:data"]
}
```

### Get Delegation Details
```http
GET /api/delegations/{delegation_id}
```

### Approve Delegation
```http
PUT /api/delegations/{delegation_id}/approve
```

### Deny Delegation
```http
PUT /api/delegations/{delegation_id}/deny
```

### Revoke Delegation
```http
DELETE /api/delegations/{delegation_id}
```

## Token Management Endpoints

### List Active Tokens
```http
GET /api/tokens/active
```

### Token Introspection
```http
POST /api/tokens/introspect
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response:
```json
{
  "token_info": {
    "type": "access",
    "claims": {
      "iss": "http://localhost:5000",
      "sub": "alice",
      "actor": "agent-12345",
      "scope": ["read:data"],
      "exp": 1640995200,
      "iat": 1640991600
    },
    "is_valid": true,
    "is_revoked": false,
    "is_expired": false,
    "expires_at": "2025-01-01T13:00:00.000000",
    "issued_at": "2025-01-01T12:00:00.000000",
    "time_to_expiry_seconds": 3600
  }
}
```

### Revoke Token
```http
POST /api/tokens/revoke
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Demo and Simulation Endpoints

### Run Demo Flow
```http
POST /api/demo/run
```

Executes a complete demonstration of the delegation protocol flow.

### List Simulation Scenarios
```http
GET /api/simulate/scenarios
```

### Run Simulation
```http
POST /api/simulate/{scenario_id}
```

Available scenarios:
- `happy_path`: Normal delegation flow
- `token_expiry`: Token expiration scenario
- `revocation`: Token revocation scenario
- `invalid_agent`: Invalid agent scenario

## System Status Endpoints

### System Status
```http
GET /api/status
```

Response:
```json
{
  "status": "healthy",
  "service": "api-server",
  "version": "1.0.0",
  "timestamp": "2025-01-01T12:00:00.000000",
  "statistics": {
    "total_agents": 5,
    "active_agents": 4,
    "total_delegations": 10,
    "pending_delegations": 2,
    "active_delegations": 6,
    "active_tokens": 8,
    "revoked_tokens": 3
  }
}
```

### System Logs
```http
GET /api/logs?limit=50
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "timestamp": "2025-01-01T12:00:00.000000"
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation error)
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `409`: Conflict (resource already exists)
- `500`: Internal Server Error

## CORS Configuration

The API servers are configured with CORS support for the following origins:
- `http://localhost:3000` (React development server)
- `http://localhost:7000` (Demo frontend)
- `http://localhost:8080` (Alternative frontend port)

## Rate Limiting

API endpoints are rate-limited to 60 requests per minute per IP address.

## Data Models

### Agent
```typescript
interface Agent {
  id: string;
  name: string;
  description: string;
  scopes: string[];
  status: 'active' | 'inactive' | 'suspended';
  created_at: string;
  last_used?: string;
  delegation_count: number;
}
```

### Delegation
```typescript
interface Delegation {
  id: string;
  agent_id: string;
  agent_name: string;
  user_id: string;
  scopes: string[];
  status: 'pending' | 'approved' | 'denied' | 'expired' | 'revoked';
  created_at: string;
  approved_at?: string;
  expires_at: string;
  delegation_token?: string;
  access_token?: string;
}
```

### Token Info
```typescript
interface TokenInfo {
  type: 'delegation' | 'access';
  claims: Record<string, any>;
  is_valid: boolean;
  is_revoked: boolean;
  is_expired: boolean;
  expires_at: string;
  issued_at: string;
  time_to_expiry_seconds: number;
}
```

## Configuration

The API server can be configured using environment variables. See `.env.example` for all available options.

Key configuration options:
- `JWT_SECRET`: Secret key for JWT token signing
- `ACCESS_TOKEN_EXPIRY_MINUTES`: Access token expiry time
- `DELEGATION_TOKEN_EXPIRY_MINUTES`: Delegation token expiry time
- `CORS_ORIGINS`: Allowed CORS origins
- `RATE_LIMIT_PER_MINUTE`: API rate limit

## Testing

Use the provided test scripts to validate the API:

```bash
# Validate setup
python validate_setup.py

# Test API endpoints
python test_api.py
```

## Starting the Servers

To start all servers:

```bash
# Install dependencies
pip install -r requirements.txt

# Start all servers
python run_servers.py
```

This will start:
- Authorization Server on port 5000
- Resource Server on port 6000
- API Server on port 7000