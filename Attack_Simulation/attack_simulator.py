#!/usr/bin/env python3
"""
Agent Delegation Protocol - Attack Simulator

This module implements comprehensive attack simulations against the Agent Delegation Protocol
to validate security controls and identify vulnerabilities.
"""

import argparse
import json
import time
import hashlib
import base64
import secrets
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import requests
import jwt


class AttackResult(Enum):
    """Attack simulation results."""
    SUCCESS = "SUCCESS"  # Attack succeeded (vulnerability found)
    BLOCKED = "BLOCKED"  # Attack was blocked (security control worked)
    ERROR = "ERROR"     # Technical error during attack
    PARTIAL = "PARTIAL"  # Attack partially succeeded


@dataclass
class AttackScenario:
    """Represents an attack scenario."""
    id: str
    name: str
    description: str
    category: str
    severity: str
    expected_result: AttackResult
    cve_references: List[str] = None


class AttackSimulator:
    """Main attack simulation framework."""
    
    def __init__(self, auth_url: str = "http://localhost:5000", 
                 resource_url: str = "http://localhost:6000"):
        self.auth_url = auth_url
        self.resource_url = resource_url
        self.jwt_secret = "jwt-signing-secret"  # Default secret for testing
        self.results = []
        
    def run_all_attacks(self) -> Dict:
        """Run all attack scenarios."""
        print("🚨 Starting comprehensive attack simulation...")
        print("=" * 60)
        
        categories = [
            "authentication",
            "authorization", 
            "protocol",
            "cryptographic",
            "infrastructure",
            "agent_specific"
        ]
        
        all_results = {}
        for category in categories:
            print(f"\n🎯 Running {category.upper()} attacks...")
            all_results[category] = self.run_category(category)
            
        return all_results
    
    def run_category(self, category: str) -> List[Dict]:
        """Run attacks for a specific category."""
        category_methods = {
            "authentication": self._run_authentication_attacks,
            "authorization": self._run_authorization_attacks,
            "protocol": self._run_protocol_attacks,
            "cryptographic": self._run_cryptographic_attacks,
            "infrastructure": self._run_infrastructure_attacks,
            "agent_specific": self._run_agent_specific_attacks
        }
        
        if category not in category_methods:
            raise ValueError(f"Unknown category: {category}")
            
        return category_methods[category]()
    
    def _run_authentication_attacks(self) -> List[Dict]:
        """Run authentication-related attacks."""
        results = []
        
        # A1: TLS Authentication Bypass
        results.append(self._simulate_tls_bypass())
        
        # A2: Tokenless Access
        results.append(self._simulate_tokenless_access())
        
        # A3: Expired Token Reuse
        results.append(self._simulate_expired_token_reuse())
        
        # A4: Impersonation with Public Metadata
        results.append(self._simulate_impersonation_attack())
        
        # A5: Token Misuse (Wrong Agent)
        results.append(self._simulate_token_misuse())
        
        return results    

    def _run_authorization_attacks(self) -> List[Dict]:
        """Run authorization-related attacks."""
        results = []
        
        # A6: Contact Policy Violation
        results.append(self._simulate_policy_violation())
        
        # Scope escalation attacks
        results.append(self._simulate_scope_escalation())
        
        # Privilege escalation
        results.append(self._simulate_privilege_escalation())
        
        return results
    
    def _run_protocol_attacks(self) -> List[Dict]:
        """Run protocol-specific attacks."""
        results = []
        
        # PKCE bypass attempts
        results.append(self._simulate_pkce_bypass())
        
        # Token exchange manipulation
        results.append(self._simulate_token_exchange_manipulation())
        
        # Flow manipulation
        results.append(self._simulate_flow_manipulation())
        
        return results
    
    def _run_cryptographic_attacks(self) -> List[Dict]:
        """Run cryptographic attacks."""
        results = []
        
        # JWT manipulation
        results.append(self._simulate_jwt_manipulation())
        
        # Signature bypass
        results.append(self._simulate_signature_bypass())
        
        # Algorithm confusion
        results.append(self._simulate_algorithm_confusion())
        
        return results
    
    def _run_infrastructure_attacks(self) -> List[Dict]:
        """Run infrastructure-level attacks."""
        results = []
        
        # DoS attacks
        results.append(self._simulate_dos_attack())
        
        # Rate limiting bypass
        results.append(self._simulate_rate_limit_bypass())
        
        # Resource exhaustion
        results.append(self._simulate_resource_exhaustion())
        
        return results
    
    def _run_agent_specific_attacks(self) -> List[Dict]:
        """Run agent-specific attacks."""
        results = []
        
        # C1: Malicious Agent Registration
        results.append(self._simulate_malicious_agent_registration())
        
        # C5: Sybil Attack
        results.append(self._simulate_sybil_attack())
        
        # A7: Self-Replication Registration
        results.append(self._simulate_self_replication())
        
        # Agent impersonation
        results.append(self._simulate_agent_impersonation())
        
        return results    
   
 # Individual attack implementations
    
    def _simulate_tls_bypass(self) -> Dict:
        """A1: TLS Authentication Bypass"""
        scenario = AttackScenario(
            id="A1",
            name="TLS Authentication Bypass",
            description="Attempt to bypass TLS authentication",
            category="authentication",
            severity="HIGH",
            expected_result=AttackResult.BLOCKED
        )
        
        try:
            # Attempt HTTP connection instead of HTTPS
            http_url = self.auth_url.replace("https://", "http://")
            response = requests.get(f"{http_url}/authorize", 
                                  params={"user": "alice", "client_id": "test"},
                                  timeout=5)
            
            if response.status_code == 200:
                result = AttackResult.SUCCESS
                details = "TLS bypass successful - HTTP connection allowed"
            else:
                result = AttackResult.BLOCKED
                details = "TLS bypass blocked - HTTPS required"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during TLS bypass test: {str(e)}"
        
        return self._create_result(scenario, result, details)
    
    def _simulate_tokenless_access(self) -> Dict:
        """A2: Tokenless Access"""
        scenario = AttackScenario(
            id="A2", 
            name="Tokenless Access",
            description="Attempt to access resources without valid token",
            category="authentication",
            severity="HIGH",
            expected_result=AttackResult.BLOCKED
        )
        
        try:
            # Attempt to access resource without Authorization header
            response = requests.get(f"{self.resource_url}/data", timeout=5)
            
            if response.status_code == 401:
                result = AttackResult.BLOCKED
                details = "Tokenless access properly blocked"
            elif response.status_code == 200:
                result = AttackResult.SUCCESS
                details = "VULNERABILITY: Tokenless access allowed"
            else:
                result = AttackResult.PARTIAL
                details = f"Unexpected response: {response.status_code}"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during tokenless access test: {str(e)}"
        
        return self._create_result(scenario, result, details)
    
    def _simulate_expired_token_reuse(self) -> Dict:
        """A3: Expired Token Reuse"""
        scenario = AttackScenario(
            id="A3",
            name="Expired Token Reuse", 
            description="Attempt to reuse expired tokens",
            category="authentication",
            severity="MEDIUM",
            expected_result=AttackResult.BLOCKED
        )
        
        try:
            # Create an expired token
            expired_payload = {
                "iss": self.auth_url,
                "sub": "alice",
                "actor": "test-agent",
                "scope": ["read:data"],
                "exp": datetime.utcnow() - timedelta(minutes=10),  # Expired
                "iat": datetime.utcnow() - timedelta(minutes=20)
            }
            
            expired_token = jwt.encode(expired_payload, self.jwt_secret, algorithm="HS256")
            
            # Attempt to use expired token
            headers = {"Authorization": f"Bearer {expired_token}"}
            response = requests.get(f"{self.resource_url}/data", headers=headers, timeout=5)
            
            if response.status_code == 403:
                result = AttackResult.BLOCKED
                details = "Expired token properly rejected"
            elif response.status_code == 200:
                result = AttackResult.SUCCESS
                details = "VULNERABILITY: Expired token accepted"
            else:
                result = AttackResult.PARTIAL
                details = f"Unexpected response: {response.status_code}"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during expired token test: {str(e)}"
        
        return self._create_result(scenario, result, details)  
  
    def _simulate_impersonation_attack(self) -> Dict:
        """A4: Impersonation with Public Metadata"""
        scenario = AttackScenario(
            id="A4",
            name="Agent Impersonation",
            description="Attempt to impersonate another agent",
            category="authentication", 
            severity="HIGH",
            expected_result=AttackResult.BLOCKED
        )
        
        try:
            # Create token with mismatched agent identity
            fake_payload = {
                "iss": self.auth_url,
                "sub": "alice",
                "actor": "legitimate-agent",  # Impersonating legitimate agent
                "scope": ["read:data", "write:data"],
                "exp": datetime.utcnow() + timedelta(minutes=5),
                "iat": datetime.utcnow()
            }
            
            # Sign with wrong secret or manipulate signature
            fake_token = jwt.encode(fake_payload, "wrong-secret", algorithm="HS256")
            
            headers = {"Authorization": f"Bearer {fake_token}"}
            response = requests.get(f"{self.resource_url}/data", headers=headers, timeout=5)
            
            if response.status_code == 403:
                result = AttackResult.BLOCKED
                details = "Impersonation attempt blocked"
            elif response.status_code == 200:
                result = AttackResult.SUCCESS
                details = "VULNERABILITY: Agent impersonation successful"
            else:
                result = AttackResult.PARTIAL
                details = f"Unexpected response: {response.status_code}"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during impersonation test: {str(e)}"
        
        return self._create_result(scenario, result, details)
    
    def _simulate_token_misuse(self) -> Dict:
        """A5: Token Misuse (Wrong Agent)"""
        scenario = AttackScenario(
            id="A5",
            name="Token Misuse",
            description="Use token issued to different agent",
            category="authentication",
            severity="MEDIUM", 
            expected_result=AttackResult.BLOCKED
        )
        
        try:
            # Get legitimate token for one agent
            auth_response = requests.get(f"{self.auth_url}/authorize", params={
                "user": "alice",
                "client_id": "agent-client-id", 
                "scope": "read:data"
            }, timeout=5)
            
            if auth_response.status_code != 200:
                return self._create_result(scenario, AttackResult.ERROR, 
                                         "Failed to get delegation token")
            
            delegation_token = auth_response.json()["delegation_token"]
            
            token_response = requests.post(f"{self.auth_url}/token", 
                                         data={"delegation_token": delegation_token},
                                         timeout=5)
            
            if token_response.status_code != 200:
                return self._create_result(scenario, AttackResult.ERROR,
                                         "Failed to exchange token")
            
            access_token = token_response.json()["access_token"]
            
            # Now try to use this token as if we're a different agent
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(f"{self.resource_url}/data", headers=headers, timeout=5)
            
            if response.status_code == 200:
                # Check if the response includes proper agent identification
                data = response.json()
                if data.get("agent") == "agent-client-id":
                    result = AttackResult.BLOCKED
                    details = "Token properly bound to original agent"
                else:
                    result = AttackResult.SUCCESS
                    details = "VULNERABILITY: Token misuse possible"
            else:
                result = AttackResult.BLOCKED
                details = "Token misuse blocked"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during token misuse test: {str(e)}"
        
        return self._create_result(scenario, result, details)    
   
 def _simulate_policy_violation(self) -> Dict:
        """A6: Contact Policy Violation"""
        scenario = AttackScenario(
            id="A6",
            name="Contact Policy Violation",
            description="Attempt to violate contact policies",
            category="authorization",
            severity="MEDIUM",
            expected_result=AttackResult.BLOCKED
        )
        
        try:
            # Request token with unauthorized scope
            auth_response = requests.get(f"{self.auth_url}/authorize", params={
                "user": "alice",
                "client_id": "agent-client-id",
                "scope": "admin:all unauthorized:scope"  # Requesting unauthorized scopes
            }, timeout=5)
            
            if auth_response.status_code == 200:
                result = AttackResult.PARTIAL
                details = "Unauthorized scope request accepted (needs policy enforcement)"
            else:
                result = AttackResult.BLOCKED
                details = "Unauthorized scope request blocked"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during policy violation test: {str(e)}"
        
        return self._create_result(scenario, result, details)
    
    def _simulate_scope_escalation(self) -> Dict:
        """Scope Escalation Attack"""
        scenario = AttackScenario(
            id="SE1",
            name="Scope Escalation",
            description="Attempt to escalate token scope",
            category="authorization",
            severity="HIGH",
            expected_result=AttackResult.BLOCKED
        )
        
        try:
            # Get token with limited scope
            auth_response = requests.get(f"{self.auth_url}/authorize", params={
                "user": "alice", 
                "client_id": "agent-client-id",
                "scope": "read:data"
            }, timeout=5)
            
            delegation_token = auth_response.json()["delegation_token"]
            
            # Decode and modify the delegation token to add more scopes
            try:
                decoded = jwt.decode(delegation_token, self.jwt_secret, algorithms=["HS256"])
                decoded["scope"] = ["read:data", "write:data", "admin:all"]  # Escalate scope
                
                # Re-encode with modified scope
                modified_token = jwt.encode(decoded, self.jwt_secret, algorithm="HS256")
                
                # Try to exchange modified token
                token_response = requests.post(f"{self.auth_url}/token",
                                             data={"delegation_token": modified_token},
                                             timeout=5)
                
                if token_response.status_code == 200:
                    result = AttackResult.SUCCESS
                    details = "VULNERABILITY: Scope escalation successful"
                else:
                    result = AttackResult.BLOCKED
                    details = "Scope escalation blocked"
                    
            except jwt.InvalidTokenError:
                result = AttackResult.BLOCKED
                details = "Token modification detected and blocked"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during scope escalation test: {str(e)}"
        
        return self._create_result(scenario, result, details)
    
    def _simulate_privilege_escalation(self) -> Dict:
        """Privilege Escalation Attack"""
        scenario = AttackScenario(
            id="PE1",
            name="Privilege Escalation", 
            description="Attempt to escalate user privileges",
            category="authorization",
            severity="CRITICAL",
            expected_result=AttackResult.BLOCKED
        )
        
        try:
            # Get token for regular user
            auth_response = requests.get(f"{self.auth_url}/authorize", params={
                "user": "alice",
                "client_id": "agent-client-id", 
                "scope": "read:data"
            }, timeout=5)
            
            delegation_token = auth_response.json()["delegation_token"]
            
            # Decode and modify to escalate user privileges
            try:
                decoded = jwt.decode(delegation_token, self.jwt_secret, algorithms=["HS256"])
                decoded["delegator"] = "admin"  # Try to escalate to admin user
                
                modified_token = jwt.encode(decoded, self.jwt_secret, algorithm="HS256")
                
                token_response = requests.post(f"{self.auth_url}/token",
                                             data={"delegation_token": modified_token},
                                             timeout=5)
                
                if token_response.status_code == 200:
                    access_token = token_response.json()["access_token"]
                    headers = {"Authorization": f"Bearer {access_token}"}
                    resource_response = requests.get(f"{self.resource_url}/data", 
                                                   headers=headers, timeout=5)
                    
                    if resource_response.status_code == 200:
                        data = resource_response.json()
                        if data.get("user") == "admin":
                            result = AttackResult.SUCCESS
                            details = "CRITICAL VULNERABILITY: Privilege escalation successful"
                        else:
                            result = AttackResult.BLOCKED
                            details = "Privilege escalation blocked"
                    else:
                        result = AttackResult.BLOCKED
                        details = "Privilege escalation blocked at resource server"
                else:
                    result = AttackResult.BLOCKED
                    details = "Privilege escalation blocked at token exchange"
                    
            except jwt.InvalidTokenError:
                result = AttackResult.BLOCKED
                details = "Token modification detected and blocked"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during privilege escalation test: {str(e)}"
        
        return self._create_result(scenario, result, details)    
  
  def _simulate_pkce_bypass(self) -> Dict:
        """PKCE Bypass Attack"""
        scenario = AttackScenario(
            id="PB1",
            name="PKCE Bypass",
            description="Attempt to bypass PKCE protection",
            category="protocol",
            severity="HIGH", 
            expected_result=AttackResult.BLOCKED
        )
        
        try:
            # Generate PKCE parameters
            code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
            code_challenge = base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode('utf-8')).digest()
            ).decode('utf-8').rstrip('=')
            
            # Get delegation token with PKCE
            auth_response = requests.get(f"{self.auth_url}/authorize", params={
                "user": "alice",
                "client_id": "agent-client-id",
                "scope": "read:data",
                "code_challenge": code_challenge,
                "code_challenge_method": "S256"
            }, timeout=5)
            
            delegation_token = auth_response.json()["delegation_token"]
            
            # Try to exchange without providing code_verifier
            token_response = requests.post(f"{self.auth_url}/token",
                                         data={"delegation_token": delegation_token},
                                         timeout=5)
            
            if token_response.status_code == 403:
                result = AttackResult.BLOCKED
                details = "PKCE bypass blocked - verifier required"
            elif token_response.status_code == 200:
                result = AttackResult.SUCCESS
                details = "VULNERABILITY: PKCE bypass successful"
            else:
                result = AttackResult.PARTIAL
                details = f"Unexpected response: {token_response.status_code}"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during PKCE bypass test: {str(e)}"
        
        return self._create_result(scenario, result, details)
    
    def _simulate_token_exchange_manipulation(self) -> Dict:
        """Token Exchange Manipulation"""
        scenario = AttackScenario(
            id="TEM1",
            name="Token Exchange Manipulation",
            description="Manipulate token exchange process",
            category="protocol",
            severity="MEDIUM",
            expected_result=AttackResult.BLOCKED
        )
        
        try:
            # Try to exchange invalid/malformed delegation token
            malformed_tokens = [
                "invalid.token.here",
                "",
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid.signature",
                None
            ]
            
            blocked_count = 0
            for token in malformed_tokens:
                data = {"delegation_token": token} if token is not None else {}
                response = requests.post(f"{self.auth_url}/token", data=data, timeout=5)
                if response.status_code == 403:
                    blocked_count += 1
            
            if blocked_count == len(malformed_tokens):
                result = AttackResult.BLOCKED
                details = "All malformed token exchanges blocked"
            elif blocked_count == 0:
                result = AttackResult.SUCCESS
                details = "VULNERABILITY: Malformed tokens accepted"
            else:
                result = AttackResult.PARTIAL
                details = f"Partial protection: {blocked_count}/{len(malformed_tokens)} blocked"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during token exchange manipulation test: {str(e)}"
        
        return self._create_result(scenario, result, details)
    
    def _simulate_flow_manipulation(self) -> Dict:
        """Protocol Flow Manipulation"""
        scenario = AttackScenario(
            id="FM1",
            name="Flow Manipulation",
            description="Attempt to manipulate protocol flow",
            category="protocol",
            severity="MEDIUM",
            expected_result=AttackResult.BLOCKED
        )
        
        try:
            # Try to skip authorization step and directly request access token
            fake_delegation = {
                "iss": self.auth_url,
                "sub": "agent-client-id",
                "delegator": "alice",
                "scope": ["read:data"],
                "exp": datetime.utcnow() + timedelta(minutes=10),
                "iat": datetime.utcnow()
            }
            
            # Create token without going through proper authorization
            fake_token = jwt.encode(fake_delegation, "wrong-secret", algorithm="HS256")
            
            response = requests.post(f"{self.auth_url}/token",
                                   data={"delegation_token": fake_token},
                                   timeout=5)
            
            if response.status_code == 403:
                result = AttackResult.BLOCKED
                details = "Flow manipulation blocked"
            elif response.status_code == 200:
                result = AttackResult.SUCCESS
                details = "VULNERABILITY: Flow manipulation successful"
            else:
                result = AttackResult.PARTIAL
                details = f"Unexpected response: {response.status_code}"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during flow manipulation test: {str(e)}"
        
        return self._create_result(scenario, result, details)  
  
    def _simulate_jwt_manipulation(self) -> Dict:
        """JWT Manipulation Attack"""
        scenario = AttackScenario(
            id="JM1",
            name="JWT Manipulation",
            description="Attempt to manipulate JWT tokens",
            category="cryptographic",
            severity="HIGH",
            expected_result=AttackResult.BLOCKED
        )
        
        try:
            # Get a valid token first
            auth_response = requests.get(f"{self.auth_url}/authorize", params={
                "user": "alice",
                "client_id": "agent-client-id",
                "scope": "read:data"
            }, timeout=5)
            
            delegation_token = auth_response.json()["delegation_token"]
            
            token_response = requests.post(f"{self.auth_url}/token",
                                         data={"delegation_token": delegation_token},
                                         timeout=5)
            
            access_token = token_response.json()["access_token"]
            
            # Manipulate the token
            parts = access_token.split('.')
            if len(parts) == 3:
                # Modify payload
                payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
                payload['scope'] = ['admin:all']  # Escalate scope
                
                modified_payload = base64.urlsafe_b64encode(
                    json.dumps(payload).encode()
                ).decode().rstrip('=')
                
                manipulated_token = f"{parts[0]}.{modified_payload}.{parts[2]}"
                
                # Try to use manipulated token
                headers = {"Authorization": f"Bearer {manipulated_token}"}
                response = requests.get(f"{self.resource_url}/data", headers=headers, timeout=5)
                
                if response.status_code == 403:
                    result = AttackResult.BLOCKED
                    details = "JWT manipulation blocked"
                elif response.status_code == 200:
                    result = AttackResult.SUCCESS
                    details = "VULNERABILITY: JWT manipulation successful"
                else:
                    result = AttackResult.PARTIAL
                    details = f"Unexpected response: {response.status_code}"
            else:
                result = AttackResult.ERROR
                details = "Invalid JWT format"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during JWT manipulation test: {str(e)}"
        
        return self._create_result(scenario, result, details)
    
    def _simulate_signature_bypass(self) -> Dict:
        """JWT Signature Bypass"""
        scenario = AttackScenario(
            id="SB1", 
            name="Signature Bypass",
            description="Attempt to bypass JWT signature validation",
            category="cryptographic",
            severity="CRITICAL",
            expected_result=AttackResult.BLOCKED
        )
        
        try:
            # Create unsigned token (algorithm: none)
            unsigned_payload = {
                "iss": self.auth_url,
                "sub": "alice", 
                "actor": "agent-client-id",
                "scope": ["admin:all"],
                "exp": datetime.utcnow() + timedelta(minutes=5),
                "iat": datetime.utcnow()
            }
            
            # Create token with "none" algorithm
            header = {"alg": "none", "typ": "JWT"}
            encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
            encoded_payload = base64.urlsafe_b64encode(json.dumps(unsigned_payload).encode()).decode().rstrip('=')
            
            unsigned_token = f"{encoded_header}.{encoded_payload}."
            
            headers = {"Authorization": f"Bearer {unsigned_token}"}
            response = requests.get(f"{self.resource_url}/data", headers=headers, timeout=5)
            
            if response.status_code == 403:
                result = AttackResult.BLOCKED
                details = "Signature bypass blocked"
            elif response.status_code == 200:
                result = AttackResult.SUCCESS
                details = "CRITICAL VULNERABILITY: Signature bypass successful"
            else:
                result = AttackResult.PARTIAL
                details = f"Unexpected response: {response.status_code}"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during signature bypass test: {str(e)}"
        
        return self._create_result(scenario, result, details)
    
    def _simulate_algorithm_confusion(self) -> Dict:
        """Algorithm Confusion Attack"""
        scenario = AttackScenario(
            id="AC1",
            name="Algorithm Confusion",
            description="Exploit algorithm confusion vulnerabilities",
            category="cryptographic", 
            severity="HIGH",
            expected_result=AttackResult.BLOCKED
        )
        
        try:
            # Try different algorithms
            algorithms = ["HS256", "HS512", "RS256", "none"]
            payload = {
                "iss": self.auth_url,
                "sub": "alice",
                "actor": "agent-client-id", 
                "scope": ["read:data"],
                "exp": datetime.utcnow() + timedelta(minutes=5),
                "iat": datetime.utcnow()
            }
            
            vulnerable_count = 0
            for alg in algorithms:
                try:
                    if alg == "none":
                        # Handle "none" algorithm specially
                        header = {"alg": "none", "typ": "JWT"}
                        encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
                        encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
                        token = f"{encoded_header}.{encoded_payload}."
                    else:
                        token = jwt.encode(payload, self.jwt_secret, algorithm=alg)
                    
                    headers = {"Authorization": f"Bearer {token}"}
                    response = requests.get(f"{self.resource_url}/data", headers=headers, timeout=5)
                    
                    if response.status_code == 200:
                        vulnerable_count += 1
                        
                except Exception:
                    continue  # Algorithm not supported, which is expected
            
            if vulnerable_count > 1:
                result = AttackResult.SUCCESS
                details = f"VULNERABILITY: Multiple algorithms accepted ({vulnerable_count})"
            elif vulnerable_count == 1:
                result = AttackResult.BLOCKED
                details = "Only expected algorithm accepted"
            else:
                result = AttackResult.BLOCKED
                details = "All algorithm confusion attempts blocked"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during algorithm confusion test: {str(e)}"
        
        return self._create_result(scenario, result, details)  
  
    def _simulate_dos_attack(self) -> Dict:
        """Denial of Service Attack"""
        scenario = AttackScenario(
            id="DOS1",
            name="DoS Attack",
            description="Attempt denial of service attack",
            category="infrastructure",
            severity="HIGH",
            expected_result=AttackResult.BLOCKED
        )
        
        try:
            # Send rapid requests to overwhelm server
            request_count = 50
            success_count = 0
            error_count = 0
            
            start_time = time.time()
            
            for i in range(request_count):
                try:
                    response = requests.get(f"{self.auth_url}/health", timeout=1)
                    if response.status_code == 200:
                        success_count += 1
                except Exception:
                    error_count += 1
            
            end_time = time.time()
            duration = end_time - start_time
            
            if error_count > request_count * 0.5:  # More than 50% errors
                result = AttackResult.SUCCESS
                details = f"VULNERABILITY: DoS successful - {error_count}/{request_count} requests failed"
            elif success_count == request_count:
                result = AttackResult.BLOCKED
                details = f"DoS blocked - all requests handled in {duration:.2f}s"
            else:
                result = AttackResult.PARTIAL
                details = f"Partial DoS - {error_count}/{request_count} requests failed"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during DoS test: {str(e)}"
        
        return self._create_result(scenario, result, details)
    
    def _simulate_rate_limit_bypass(self) -> Dict:
        """Rate Limiting Bypass"""
        scenario = AttackScenario(
            id="RLB1",
            name="Rate Limit Bypass",
            description="Attempt to bypass rate limiting",
            category="infrastructure",
            severity="MEDIUM",
            expected_result=AttackResult.BLOCKED
        )
        
        try:
            # Send requests rapidly to test rate limiting
            rapid_requests = 20
            success_count = 0
            
            for i in range(rapid_requests):
                try:
                    response = requests.get(f"{self.auth_url}/authorize", params={
                        "user": "alice",
                        "client_id": "agent-client-id",
                        "scope": "read:data"
                    }, timeout=2)
                    
                    if response.status_code == 200:
                        success_count += 1
                    elif response.status_code == 429:  # Too Many Requests
                        break
                        
                except Exception:
                    continue
            
            if success_count == rapid_requests:
                result = AttackResult.SUCCESS
                details = "VULNERABILITY: No rate limiting detected"
            elif success_count < rapid_requests * 0.5:
                result = AttackResult.BLOCKED
                details = f"Rate limiting active - only {success_count}/{rapid_requests} succeeded"
            else:
                result = AttackResult.PARTIAL
                details = f"Weak rate limiting - {success_count}/{rapid_requests} succeeded"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during rate limit bypass test: {str(e)}"
        
        return self._create_result(scenario, result, details)
    
    def _simulate_resource_exhaustion(self) -> Dict:
        """Resource Exhaustion Attack"""
        scenario = AttackScenario(
            id="RE1",
            name="Resource Exhaustion",
            description="Attempt to exhaust server resources",
            category="infrastructure",
            severity="MEDIUM",
            expected_result=AttackResult.BLOCKED
        )
        
        try:
            # Try to exhaust resources with large payloads
            large_payload = "x" * 10000  # 10KB payload
            
            response = requests.post(f"{self.auth_url}/register", 
                                   json={"client_id": large_payload, "name": "test"},
                                   timeout=5)
            
            if response.status_code == 400:
                result = AttackResult.BLOCKED
                details = "Large payload rejected"
            elif response.status_code == 201:
                result = AttackResult.SUCCESS
                details = "VULNERABILITY: Large payload accepted"
            else:
                result = AttackResult.PARTIAL
                details = f"Unexpected response: {response.status_code}"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during resource exhaustion test: {str(e)}"
        
        return self._create_result(scenario, result, details)    

    def _simulate_malicious_agent_registration(self) -> Dict:
        """C1: Malicious Agent Registration"""
        scenario = AttackScenario(
            id="C1",
            name="Malicious Agent Registration",
            description="Register malicious agent",
            category="agent_specific",
            severity="HIGH",
            expected_result=AttackResult.PARTIAL  # Registration might succeed, but usage should be limited
        )
        
        try:
            # Register obviously malicious agent
            malicious_data = {
                "client_id": "malicious-agent-666",
                "name": "Definitely Not Malicious Agent"
            }
            
            response = requests.post(f"{self.auth_url}/register", json=malicious_data, timeout=5)
            
            if response.status_code == 201:
                # Registration succeeded, now try to use it
                auth_response = requests.get(f"{self.auth_url}/authorize", params={
                    "user": "alice",
                    "client_id": "malicious-agent-666",
                    "scope": "read:data"
                }, timeout=5)
                
                if auth_response.status_code == 200:
                    result = AttackResult.SUCCESS
                    details = "VULNERABILITY: Malicious agent registered and authorized"
                else:
                    result = AttackResult.PARTIAL
                    details = "Malicious agent registered but authorization blocked"
            else:
                result = AttackResult.BLOCKED
                details = "Malicious agent registration blocked"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during malicious agent registration test: {str(e)}"
        
        return self._create_result(scenario, result, details)
    
    def _simulate_sybil_attack(self) -> Dict:
        """C5: Sybil Attack"""
        scenario = AttackScenario(
            id="C5",
            name="Sybil Attack",
            description="Register multiple agent identities",
            category="agent_specific",
            severity="MEDIUM",
            expected_result=AttackResult.PARTIAL
        )
        
        try:
            # Register multiple agents rapidly
            agent_count = 10
            successful_registrations = 0
            
            for i in range(agent_count):
                agent_data = {
                    "client_id": f"sybil-agent-{i}",
                    "name": f"Sybil Agent {i}"
                }
                
                try:
                    response = requests.post(f"{self.auth_url}/register", 
                                           json=agent_data, timeout=2)
                    if response.status_code == 201:
                        successful_registrations += 1
                except Exception:
                    continue
            
            if successful_registrations == agent_count:
                result = AttackResult.SUCCESS
                details = f"VULNERABILITY: All {agent_count} sybil agents registered"
            elif successful_registrations > agent_count * 0.5:
                result = AttackResult.PARTIAL
                details = f"Partial sybil attack - {successful_registrations}/{agent_count} registered"
            else:
                result = AttackResult.BLOCKED
                details = f"Sybil attack mostly blocked - only {successful_registrations}/{agent_count} registered"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during sybil attack test: {str(e)}"
        
        return self._create_result(scenario, result, details)
    
    def _simulate_self_replication(self) -> Dict:
        """A7: Self-Replication Registration"""
        scenario = AttackScenario(
            id="A7",
            name="Self-Replication",
            description="Attempt agent self-replication",
            category="agent_specific",
            severity="HIGH",
            expected_result=AttackResult.BLOCKED
        )
        
        try:
            # Simulate an agent trying to register clones of itself
            original_agent = "agent-client-id"
            clone_agents = [f"{original_agent}-clone-{i}" for i in range(5)]
            
            successful_clones = 0
            for clone_id in clone_agents:
                clone_data = {
                    "client_id": clone_id,
                    "name": f"Clone of {original_agent}"
                }
                
                try:
                    response = requests.post(f"{self.auth_url}/register", 
                                           json=clone_data, timeout=2)
                    if response.status_code == 201:
                        successful_clones += 1
                except Exception:
                    continue
            
            if successful_clones == len(clone_agents):
                result = AttackResult.SUCCESS
                details = "VULNERABILITY: All agent clones registered successfully"
            elif successful_clones > 0:
                result = AttackResult.PARTIAL
                details = f"Partial self-replication - {successful_clones}/{len(clone_agents)} clones registered"
            else:
                result = AttackResult.BLOCKED
                details = "Self-replication blocked"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during self-replication test: {str(e)}"
        
        return self._create_result(scenario, result, details)
    
    def _simulate_agent_impersonation(self) -> Dict:
        """Agent Impersonation Attack"""
        scenario = AttackScenario(
            id="AI1",
            name="Agent Impersonation",
            description="Impersonate legitimate agent",
            category="agent_specific",
            severity="HIGH",
            expected_result=AttackResult.BLOCKED
        )
        
        try:
            # Try to register agent with similar name to legitimate one
            impersonation_attempts = [
                {"client_id": "agent-client-1d", "name": "CalendarAgent"},  # Similar ID
                {"client_id": "agent-client-id-v2", "name": "CalendarAgent"},  # Extended ID
                {"client_id": "legitimate-agent", "name": "CalendarAgent"}  # Different but legitimate-sounding
            ]
            
            successful_impersonations = 0
            for attempt in impersonation_attempts:
                try:
                    response = requests.post(f"{self.auth_url}/register", 
                                           json=attempt, timeout=2)
                    if response.status_code == 201:
                        successful_impersonations += 1
                except Exception:
                    continue
            
            if successful_impersonations == len(impersonation_attempts):
                result = AttackResult.SUCCESS
                details = "VULNERABILITY: All impersonation attempts successful"
            elif successful_impersonations > 0:
                result = AttackResult.PARTIAL
                details = f"Partial impersonation success - {successful_impersonations}/{len(impersonation_attempts)}"
            else:
                result = AttackResult.BLOCKED
                details = "Agent impersonation blocked"
                
        except Exception as e:
            result = AttackResult.ERROR
            details = f"Error during agent impersonation test: {str(e)}"
        
        return self._create_result(scenario, result, details)    
  
  def _create_result(self, scenario: AttackScenario, result: AttackResult, details: str) -> Dict:
        """Create standardized result dictionary."""
        return {
            "scenario": {
                "id": scenario.id,
                "name": scenario.name,
                "description": scenario.description,
                "category": scenario.category,
                "severity": scenario.severity,
                "expected_result": scenario.expected_result.value
            },
            "result": result.value,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "success": result == scenario.expected_result
        }
    
    def generate_report(self, results: Dict) -> str:
        """Generate comprehensive security report."""
        report = []
        report.append("# Agent Delegation Protocol - Security Assessment Report")
        report.append(f"Generated: {datetime.utcnow().isoformat()}")
        report.append("")
        
        # Executive Summary
        total_tests = sum(len(category_results) for category_results in results.values())
        vulnerabilities = []
        blocked_attacks = []
        
        for category, category_results in results.items():
            for result in category_results:
                if result["result"] == "SUCCESS" and result["scenario"]["expected_result"] == "BLOCKED":
                    vulnerabilities.append(result)
                elif result["result"] == "BLOCKED":
                    blocked_attacks.append(result)
        
        report.append("## Executive Summary")
        report.append(f"- **Total Tests**: {total_tests}")
        report.append(f"- **Vulnerabilities Found**: {len(vulnerabilities)}")
        report.append(f"- **Attacks Blocked**: {len(blocked_attacks)}")
        report.append(f"- **Success Rate**: {(len(blocked_attacks)/total_tests)*100:.1f}%")
        report.append("")
        
        # Vulnerabilities
        if vulnerabilities:
            report.append("## 🚨 Critical Vulnerabilities Found")
            for vuln in vulnerabilities:
                report.append(f"### {vuln['scenario']['id']}: {vuln['scenario']['name']}")
                report.append(f"**Severity**: {vuln['scenario']['severity']}")
                report.append(f"**Details**: {vuln['details']}")
                report.append("")
        
        # Category Results
        for category, category_results in results.items():
            report.append(f"## {category.upper()} Attack Results")
            report.append("")
            
            for result in category_results:
                status_emoji = {
                    "SUCCESS": "❌" if result["scenario"]["expected_result"] == "BLOCKED" else "✅",
                    "BLOCKED": "✅",
                    "PARTIAL": "⚠️",
                    "ERROR": "🔧"
                }
                
                emoji = status_emoji.get(result["result"], "❓")
                report.append(f"{emoji} **{result['scenario']['id']}**: {result['scenario']['name']}")
                report.append(f"   - Result: {result['result']}")
                report.append(f"   - Details: {result['details']}")
                report.append("")
        
        return "\n".join(report)


def main():
    """Main entry point for attack simulator."""
    parser = argparse.ArgumentParser(description="Agent Delegation Protocol Attack Simulator")
    parser.add_argument("--category", help="Run specific attack category")
    parser.add_argument("--all", action="store_true", help="Run all attack scenarios")
    parser.add_argument("--report", action="store_true", help="Generate security report")
    parser.add_argument("--auth-url", default="http://localhost:5000", help="Authorization server URL")
    parser.add_argument("--resource-url", default="http://localhost:6000", help="Resource server URL")
    
    args = parser.parse_args()
    
    simulator = AttackSimulator(args.auth_url, args.resource_url)
    
    if args.all:
        results = simulator.run_all_attacks()
        print("\n" + "="*60)
        print("ATTACK SIMULATION COMPLETE")
        print("="*60)
        
        if args.report:
            report = simulator.generate_report(results)
            with open("security_assessment_report.md", "w") as f:
                f.write(report)
            print("📊 Security report saved to: security_assessment_report.md")
            
    elif args.category:
        results = {args.category: simulator.run_category(args.category)}
        print(f"\n{args.category.upper()} attacks completed")
        
    else:
        print("Use --all to run all attacks or --category <name> for specific category")
        print("Available categories: authentication, authorization, protocol, cryptographic, infrastructure, agent_specific")


if __name__ == "__main__":
    main()