# Attack Scenarios

This directory contains individual attack scenario implementations and detailed analysis.

## Scenario Categories

### Authentication Attacks
- `A1_tls_bypass.py` - TLS Authentication Bypass
- `A2_tokenless_access.py` - Tokenless Access Attempt
- `A3_expired_token_reuse.py` - Expired Token Reuse
- `A4_agent_impersonation.py` - Agent Impersonation Attack
- `A5_token_misuse.py` - Token Misuse (Wrong Agent)

### Authorization Attacks
- `A6_policy_violation.py` - Contact Policy Violation
- `SE1_scope_escalation.py` - Scope Escalation
- `PE1_privilege_escalation.py` - Privilege Escalation

### Protocol Attacks
- `PB1_pkce_bypass.py` - PKCE Bypass
- `TEM1_token_exchange_manipulation.py` - Token Exchange Manipulation
- `FM1_flow_manipulation.py` - Protocol Flow Manipulation

### Cryptographic Attacks
- `JM1_jwt_manipulation.py` - JWT Token Manipulation
- `SB1_signature_bypass.py` - JWT Signature Bypass
- `AC1_algorithm_confusion.py` - Algorithm Confusion

### Infrastructure Attacks
- `DOS1_denial_of_service.py` - Denial of Service
- `RLB1_rate_limit_bypass.py` - Rate Limiting Bypass
- `RE1_resource_exhaustion.py` - Resource Exhaustion

### Agent-Specific Attacks
- `C1_malicious_agent_registration.py` - Malicious Agent Registration
- `C5_sybil_attack.py` - Sybil Attack (Multiple Identities)
- `A7_self_replication.py` - Agent Self-Replication
- `AI1_agent_impersonation.py` - Agent Identity Impersonation

## Usage

Each scenario file can be run independently:

```bash
python attack_scenarios/A1_tls_bypass.py
```

Or use the main simulator to run all scenarios:

```bash
python ../attack_simulator.py --all
```