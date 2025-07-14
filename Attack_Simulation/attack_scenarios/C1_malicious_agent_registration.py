#!/usr/bin/env python3
"""
C1: Malicious Agent Registration Attack Scenario

This scenario tests the protocol's ability to detect and prevent registration
of malicious agents through various evasion techniques.

Attack Vector: Register agents with malicious characteristics
Expected Result: Malicious agents should be detected and blocked
Risk Level: HIGH
"""

import requests
import json
import sys
import time
import random
import string
from datetime import datetime


class MaliciousAgentRegistrationAttack:
    """Malicious Agent Registration attack implementation."""
    
    def __init__(self, target_url="http://localhost:5000"):
        self.target_url = target_url
        self.registered_agents = []
        
    def execute_attack(self):
        """Execute the malicious agent registration attack."""
        print("🚨 Executing C1: Malicious Agent Registration Attack")
        print("=" * 60)
        print(f"Target: {self.target_url}")
        print()
        
        results = []
        
        # Test 1: Obviously malicious agent names
        results.append(self._test_obvious_malicious_names())
        
        # Test 2: Suspicious agent behaviors
        results.append(self._test_suspicious_behaviors())
        
        # Test 3: Mass registration attempt
        results.append(self._test_mass_registration())
        
        # Test 4: Impersonation attempts
        results.append(self._test_impersonation_attempts())
        
        # Test 5: Payload injection attempts
        results.append(self._test_payload_injection())
        
        # Test 6: Rate limit evasion
        results.append(self._test_rate_limit_evasion())
        
        return self._generate_report(results)
    
    def _test_obvious_malicious_names(self):
        """Test registration with obviously malicious agent names."""
        print("🔍 Test 1: Obviously Malicious Names")
        
        malicious_names = [
            {"client_id": "malware-agent", "name": "Malware Agent"},
            {"client_id": "data-stealer", "name": "Data Stealer"},
            {"client_id": "backdoor-agent", "name": "Backdoor Agent"},
            {"client_id": "keylogger-bot", "name": "Keylogger Bot"},
            {"client_id": "ransomware-agent", "name": "Ransomware Agent"},
            {"client_id": "botnet-node", "name": "Botnet Node"},
            {"client_id": "exploit-kit", "name": "Exploit Kit"},
            {"client_id": "trojan-horse", "name": "Trojan Horse"}
        ]
        
        successful_registrations = 0
        blocked_registrations = 0
        
        for agent_data in malicious_names:
            try:
                response = requests.post(
                    f"{self.target_url}/register",
                    json=agent_data,
                    timeout=5
                )
                
                if response.status_code == 201:
                    successful_registrations += 1
                    self.registered_agents.append(agent_data['client_id'])
                    print(f"   ❌ REGISTERED: {agent_data['name']}")
                else:
                    blocked_registrations += 1
                    print(f"   ✅ BLOCKED: {agent_data['name']} (Status: {response.status_code})")
                    
            except Exception as e:
                print(f"   🔧 ERROR: {agent_data['name']} - {str(e)}")
        
        if successful_registrations > 0:
            result = "VULNERABLE"
            details = f"{successful_registrations}/{len(malicious_names)} malicious agents registered"
            severity = "HIGH"
        else:
            result = "SECURE"
            details = "All obviously malicious agents blocked"
            severity = "LOW"
        
        print(f"   Result: {result}")
        print(f"   Details: {details}")
        print()
        
        return {
            "test": "Obviously Malicious Names",
            "result": result,
            "details": details,
            "severity": severity,
            "successful_registrations": successful_registrations,
            "blocked_registrations": blocked_registrations,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _test_suspicious_behaviors(self):
        """Test registration with suspicious behavioral patterns."""
        print("🔍 Test 2: Suspicious Behaviors")
        
        suspicious_agents = [
            # Agents with suspicious metadata
            {"client_id": "normal-agent-1", "name": "Normal Agent", "description": "rm -rf /"},
            {"client_id": "helper-bot", "name": "Helper Bot", "contact": "hacker@darkweb.onion"},
            {"client_id": "productivity-tool", "name": "Productivity Tool", "version": "0.0.1-EXPLOIT"},
            
            # Agents with encoding attempts
            {"client_id": "dGVzdC1hZ2VudA==", "name": "Test Agent"},  # Base64 encoded
            {"client_id": "test%2Dagent", "name": "URL Encoded Agent"},  # URL encoded
            
            # Agents with suspicious patterns
            {"client_id": "agent-" + "A" * 100, "name": "Buffer Overflow Test"},
            {"client_id": "../../etc/passwd", "name": "Path Traversal Agent"},
            {"client_id": "'; DROP TABLE agents; --", "name": "SQL Injection Agent"}
        ]
        
        successful_registrations = 0
        blocked_registrations = 0
        
        for agent_data in suspicious_agents:
            try:
                response = requests.post(
                    f"{self.target_url}/register",
                    json=agent_data,
                    timeout=5
                )
                
                if response.status_code == 201:
                    successful_registrations += 1
                    self.registered_agents.append(agent_data['client_id'])
                    print(f"   ❌ REGISTERED: {agent_data['client_id']}")
                else:
                    blocked_registrations += 1
                    print(f"   ✅ BLOCKED: {agent_data['client_id']} (Status: {response.status_code})")
                    
            except Exception as e:
                print(f"   🔧 ERROR: {agent_data['client_id']} - {str(e)}")
        
        if successful_registrations > len(suspicious_agents) * 0.5:
            result = "VULNERABLE"
            details = f"{successful_registrations}/{len(suspicious_agents)} suspicious agents registered"
            severity = "HIGH"
        elif successful_registrations > 0:
            result = "PARTIAL"
            details = f"{successful_registrations}/{len(suspicious_agents)} suspicious agents registered"
            severity = "MEDIUM"
        else:
            result = "SECURE"
            details = "All suspicious agents blocked"
            severity = "LOW"
        
        print(f"   Result: {result}")
        print(f"   Details: {details}")
        print()
        
        return {
            "test": "Suspicious Behaviors",
            "result": result,
            "details": details,
            "severity": severity,
            "successful_registrations": successful_registrations,
            "blocked_registrations": blocked_registrations,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _test_mass_registration(self):
        """Test mass registration to detect rate limiting."""
        print("🔍 Test 3: Mass Registration")
        
        # Generate many agent registration requests
        mass_agents = []
        for i in range(20):
            agent_data = {
                "client_id": f"mass-agent-{i:03d}",
                "name": f"Mass Agent {i}"
            }
            mass_agents.append(agent_data)
        
        successful_registrations = 0
        blocked_registrations = 0
        rate_limited = 0
        
        start_time = time.time()
        
        for agent_data in mass_agents:
            try:
                response = requests.post(
                    f"{self.target_url}/register",
                    json=agent_data,
                    timeout=2
                )
                
                if response.status_code == 201:
                    successful_registrations += 1
                    self.registered_agents.append(agent_data['client_id'])
                elif response.status_code == 429:  # Too Many Requests
                    rate_limited += 1
                    print(f"   ⚠️ RATE LIMITED: {agent_data['client_id']}")
                    break  # Stop if rate limited
                else:
                    blocked_registrations += 1
                    
            except Exception as e:
                print(f"   🔧 ERROR: {agent_data['client_id']} - {str(e)}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"   Registered: {successful_registrations}")
        print(f"   Rate Limited: {rate_limited}")
        print(f"   Duration: {duration:.2f}s")
        
        if rate_limited > 0:
            result = "SECURE"
            details = f"Rate limiting active - {rate_limited} requests blocked"
            severity = "LOW"
        elif successful_registrations == len(mass_agents):
            result = "VULNERABLE"
            details = f"No rate limiting - all {successful_registrations} agents registered"
            severity = "HIGH"
        else:
            result = "PARTIAL"
            details = f"{successful_registrations}/{len(mass_agents)} agents registered"
            severity = "MEDIUM"
        
        print(f"   Result: {result}")
        print(f"   Details: {details}")
        print()
        
        return {
            "test": "Mass Registration",
            "result": result,
            "details": details,
            "severity": severity,
            "successful_registrations": successful_registrations,
            "rate_limited": rate_limited,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _test_impersonation_attempts(self):
        """Test attempts to impersonate legitimate agents."""
        print("🔍 Test 4: Impersonation Attempts")
        
        # Try to impersonate existing legitimate agents
        impersonation_attempts = [
            {"client_id": "agent-client-id-fake", "name": "CalendarAgent"},  # Similar to existing
            {"client_id": "agent-client-1d", "name": "CalendarAgent"},      # Typosquatting
            {"client_id": "agent_client_id", "name": "CalendarAgent"},      # Underscore variant
            {"client_id": "AGENT-CLIENT-ID", "name": "CalendarAgent"},      # Case variant
            {"client_id": "agent-client-id-v2", "name": "CalendarAgent"},   # Version variant
            {"client_id": "legitimate-agent", "name": "System Agent"},       # Generic legitimate name
        ]
        
        successful_registrations = 0
        blocked_registrations = 0
        
        for agent_data in impersonation_attempts:
            try:
                response = requests.post(
                    f"{self.target_url}/register",
                    json=agent_data,
                    timeout=5
                )
                
                if response.status_code == 201:
                    successful_registrations += 1
                    self.registered_agents.append(agent_data['client_id'])
                    print(f"   ❌ REGISTERED: {agent_data['client_id']}")
                elif response.status_code == 400 and "exists" in response.text.lower():
                    blocked_registrations += 1
                    print(f"   ✅ BLOCKED: {agent_data['client_id']} (Already exists)")
                else:
                    blocked_registrations += 1
                    print(f"   ✅ BLOCKED: {agent_data['client_id']} (Status: {response.status_code})")
                    
            except Exception as e:
                print(f"   🔧 ERROR: {agent_data['client_id']} - {str(e)}")
        
        if successful_registrations > 0:
            result = "VULNERABLE"
            details = f"{successful_registrations}/{len(impersonation_attempts)} impersonation attempts successful"
            severity = "HIGH"
        else:
            result = "SECURE"
            details = "All impersonation attempts blocked"
            severity = "LOW"
        
        print(f"   Result: {result}")
        print(f"   Details: {details}")
        print()
        
        return {
            "test": "Impersonation Attempts",
            "result": result,
            "details": details,
            "severity": severity,
            "successful_registrations": successful_registrations,
            "blocked_registrations": blocked_registrations,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _test_payload_injection(self):
        """Test various payload injection attempts."""
        print("🔍 Test 5: Payload Injection")
        
        injection_payloads = [
            # XSS attempts
            {"client_id": "xss-test", "name": "<script>alert('XSS')</script>"},
            {"client_id": "xss-test-2", "name": "javascript:alert('XSS')"},
            
            # Command injection
            {"client_id": "cmd-inject", "name": "Agent; rm -rf /"},
            {"client_id": "cmd-inject-2", "name": "Agent`whoami`"},
            
            # JSON injection
            {"client_id": "json-inject", "name": '", "admin": true, "fake": "'},
            
            # Large payloads
            {"client_id": "large-payload", "name": "A" * 10000},
            
            # Unicode/encoding attacks
            {"client_id": "unicode-test", "name": "Agent\u0000\u0001\u0002"},
            {"client_id": "utf8-test", "name": "Agent\xc0\x80"},
        ]
        
        successful_registrations = 0
        blocked_registrations = 0
        
        for agent_data in injection_payloads:
            try:
                response = requests.post(
                    f"{self.target_url}/register",
                    json=agent_data,
                    timeout=5
                )
                
                if response.status_code == 201:
                    successful_registrations += 1
                    self.registered_agents.append(agent_data['client_id'])
                    print(f"   ❌ REGISTERED: {agent_data['client_id']}")
                else:
                    blocked_registrations += 1
                    print(f"   ✅ BLOCKED: {agent_data['client_id']} (Status: {response.status_code})")
                    
            except Exception as e:
                blocked_registrations += 1
                print(f"   ✅ BLOCKED: {agent_data['client_id']} (Exception: {type(e).__name__})")
        
        if successful_registrations > 0:
            result = "VULNERABLE"
            details = f"{successful_registrations}/{len(injection_payloads)} injection attempts successful"
            severity = "HIGH"
        else:
            result = "SECURE"
            details = "All injection attempts blocked"
            severity = "LOW"
        
        print(f"   Result: {result}")
        print(f"   Details: {details}")
        print()
        
        return {
            "test": "Payload Injection",
            "result": result,
            "details": details,
            "severity": severity,
            "successful_registrations": successful_registrations,
            "blocked_registrations": blocked_registrations,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _test_rate_limit_evasion(self):
        """Test rate limit evasion techniques."""
        print("🔍 Test 6: Rate Limit Evasion")
        
        evasion_techniques = [
            # Different User-Agents
            {"headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}},
            {"headers": {"User-Agent": "curl/7.68.0"}},
            {"headers": {"User-Agent": "Python-requests/2.25.1"}},
            
            # Different X-Forwarded-For headers
            {"headers": {"X-Forwarded-For": "192.168.1.100"}},
            {"headers": {"X-Forwarded-For": "10.0.0.100"}},
            {"headers": {"X-Real-IP": "172.16.0.100"}},
        ]
        
        successful_registrations = 0
        blocked_registrations = 0
        
        for i, technique in enumerate(evasion_techniques):
            agent_data = {
                "client_id": f"evasion-agent-{i}",
                "name": f"Evasion Agent {i}"
            }
            
            try:
                response = requests.post(
                    f"{self.target_url}/register",
                    json=agent_data,
                    headers=technique.get("headers", {}),
                    timeout=5
                )
                
                if response.status_code == 201:
                    successful_registrations += 1
                    self.registered_agents.append(agent_data['client_id'])
                    print(f"   ❌ REGISTERED: {agent_data['client_id']} (Evasion successful)")
                else:
                    blocked_registrations += 1
                    print(f"   ✅ BLOCKED: {agent_data['client_id']} (Status: {response.status_code})")
                    
                # Small delay between requests
                time.sleep(0.1)
                
            except Exception as e:
                blocked_registrations += 1
                print(f"   ✅ BLOCKED: {agent_data['client_id']} (Exception: {type(e).__name__})")
        
        if successful_registrations == len(evasion_techniques):
            result = "VULNERABLE"
            details = "All rate limit evasion techniques successful"
            severity = "MEDIUM"
        elif successful_registrations > 0:
            result = "PARTIAL"
            details = f"{successful_registrations}/{len(evasion_techniques)} evasion techniques successful"
            severity = "MEDIUM"
        else:
            result = "SECURE"
            details = "All evasion attempts blocked"
            severity = "LOW"
        
        print(f"   Result: {result}")
        print(f"   Details: {details}")
        print()
        
        return {
            "test": "Rate Limit Evasion",
            "result": result,
            "details": details,
            "severity": severity,
            "successful_registrations": successful_registrations,
            "blocked_registrations": blocked_registrations,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _generate_report(self, results):
        """Generate attack report."""
        print("📊 Attack Report: C1 - Malicious Agent Registration")
        print("=" * 60)
        
        vulnerable_tests = [r for r in results if r['result'] == 'VULNERABLE']
        secure_tests = [r for r in results if r['result'] == 'SECURE']
        partial_tests = [r for r in results if r['result'] == 'PARTIAL']
        
        total_registered = sum(r.get('successful_registrations', 0) for r in results)
        
        print(f"Total Tests: {len(results)}")
        print(f"Vulnerable: {len(vulnerable_tests)}")
        print(f"Partially Secure: {len(partial_tests)}")
        print(f"Secure: {len(secure_tests)}")
        print(f"Total Malicious Agents Registered: {total_registered}")
        print()
        
        if vulnerable_tests:
            print("🚨 VULNERABILITIES FOUND:")
            for vuln in vulnerable_tests:
                print(f"   - {vuln['test']}: {vuln['details']}")
            print()
        
        if self.registered_agents:
            print("⚠️ REGISTERED MALICIOUS AGENTS:")
            for agent_id in self.registered_agents[:10]:  # Show first 10
                print(f"   - {agent_id}")
            if len(self.registered_agents) > 10:
                print(f"   ... and {len(self.registered_agents) - 10} more")
            print()
        
        # Overall assessment
        if len(vulnerable_tests) >= 3:
            overall_result = "CRITICAL"
            recommendation = "CRITICAL: Multiple agent registration vulnerabilities. Implement comprehensive validation immediately."
        elif len(vulnerable_tests) > 0:
            overall_result = "VULNERABLE"
            recommendation = "Agent registration vulnerabilities found. Enhance validation mechanisms."
        elif len(partial_tests) > 2:
            overall_result = "WEAK"
            recommendation = "Partial protection detected. Strengthen agent registration controls."
        else:
            overall_result = "SECURE"
            recommendation = "Agent registration appears to be properly protected."
        
        print(f"Overall Assessment: {overall_result}")
        print(f"Recommendation: {recommendation}")
        
        return {
            "attack_id": "C1",
            "attack_name": "Malicious Agent Registration",
            "overall_result": overall_result,
            "recommendation": recommendation,
            "test_results": results,
            "registered_agents": self.registered_agents,
            "summary": {
                "total_tests": len(results),
                "vulnerable": len(vulnerable_tests),
                "partial": len(partial_tests),
                "secure": len(secure_tests),
                "total_registered": total_registered
            }
        }


def main():
    """Main execution function."""
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        target_url = "http://localhost:5000"
    
    attack = MaliciousAgentRegistrationAttack(target_url)
    report = attack.execute_attack()
    
    # Exit with appropriate code
    if report['overall_result'] in ['CRITICAL', 'VULNERABLE']:
        sys.exit(1)
    elif report['overall_result'] == 'WEAK':
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()