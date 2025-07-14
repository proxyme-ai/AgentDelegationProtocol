#!/usr/bin/env python3
"""
A1: TLS Authentication Bypass Attack Scenario

This scenario tests whether the protocol properly enforces TLS/HTTPS connections
and rejects insecure HTTP connections.

Attack Vector: Attempt to establish HTTP connections instead of HTTPS
Expected Result: Connection should be rejected or redirected to HTTPS
Risk Level: HIGH
"""

import requests
import sys
from datetime import datetime


class TLSBypassAttack:
    """TLS Authentication Bypass attack implementation."""
    
    def __init__(self, target_url="http://localhost:5000"):
        self.target_url = target_url
        self.https_url = target_url.replace("http://", "https://")
        
    def execute_attack(self):
        """Execute the TLS bypass attack."""
        print("🚨 Executing A1: TLS Authentication Bypass Attack")
        print("=" * 60)
        print(f"Target: {self.target_url}")
        print(f"HTTPS Target: {self.https_url}")
        print()
        
        results = []
        
        # Test 1: Direct HTTP connection attempt
        results.append(self._test_http_connection())
        
        # Test 2: HTTP to HTTPS redirect test
        results.append(self._test_https_redirect())
        
        # Test 3: Mixed content test
        results.append(self._test_mixed_content())
        
        # Test 4: Protocol downgrade test
        results.append(self._test_protocol_downgrade())
        
        return self._generate_report(results)
    
    def _test_http_connection(self):
        """Test direct HTTP connection to authorization endpoint."""
        print("🔍 Test 1: Direct HTTP Connection")
        
        try:
            response = requests.get(
                f"{self.target_url}/authorize",
                params={"user": "alice", "client_id": "test-agent"},
                timeout=5,
                allow_redirects=False
            )
            
            if response.status_code == 200:
                result = "VULNERABLE"
                details = "HTTP connection accepted - TLS bypass successful"
                severity = "CRITICAL"
            elif response.status_code in [301, 302, 307, 308]:
                # Check if redirected to HTTPS
                location = response.headers.get('Location', '')
                if location.startswith('https://'):
                    result = "SECURE"
                    details = "HTTP redirected to HTTPS"
                    severity = "LOW"
                else:
                    result = "VULNERABLE"
                    details = f"HTTP redirected to insecure location: {location}"
                    severity = "HIGH"
            else:
                result = "SECURE"
                details = f"HTTP connection rejected (status: {response.status_code})"
                severity = "LOW"
                
        except requests.exceptions.ConnectionError:
            result = "SECURE"
            details = "HTTP connection refused"
            severity = "LOW"
        except Exception as e:
            result = "ERROR"
            details = f"Test error: {str(e)}"
            severity = "UNKNOWN"
        
        print(f"   Result: {result}")
        print(f"   Details: {details}")
        print()
        
        return {
            "test": "Direct HTTP Connection",
            "result": result,
            "details": details,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _test_https_redirect(self):
        """Test if HTTP requests are properly redirected to HTTPS."""
        print("🔍 Test 2: HTTPS Redirect")
        
        try:
            response = requests.get(
                f"{self.target_url}/health",
                timeout=5,
                allow_redirects=True
            )
            
            # Check if final URL is HTTPS
            if response.url.startswith('https://'):
                result = "SECURE"
                details = "HTTP properly redirected to HTTPS"
                severity = "LOW"
            elif response.status_code == 200:
                result = "VULNERABLE"
                details = "HTTP connection allowed without HTTPS redirect"
                severity = "HIGH"
            else:
                result = "PARTIAL"
                details = f"Unexpected response: {response.status_code}"
                severity = "MEDIUM"
                
        except Exception as e:
            result = "ERROR"
            details = f"Test error: {str(e)}"
            severity = "UNKNOWN"
        
        print(f"   Result: {result}")
        print(f"   Details: {details}")
        print()
        
        return {
            "test": "HTTPS Redirect",
            "result": result,
            "details": details,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _test_mixed_content(self):
        """Test for mixed content vulnerabilities."""
        print("🔍 Test 3: Mixed Content")
        
        try:
            # Try to access HTTPS endpoint but reference HTTP resources
            headers = {
                'Referer': self.target_url,  # HTTP referer
                'Origin': self.target_url    # HTTP origin
            }
            
            response = requests.get(
                f"{self.https_url}/health",
                headers=headers,
                timeout=5,
                verify=False  # Skip SSL verification for testing
            )
            
            # Check security headers
            security_headers = [
                'Strict-Transport-Security',
                'Content-Security-Policy',
                'X-Content-Type-Options',
                'X-Frame-Options'
            ]
            
            missing_headers = []
            for header in security_headers:
                if header not in response.headers:
                    missing_headers.append(header)
            
            if missing_headers:
                result = "VULNERABLE"
                details = f"Missing security headers: {', '.join(missing_headers)}"
                severity = "MEDIUM"
            else:
                result = "SECURE"
                details = "All security headers present"
                severity = "LOW"
                
        except Exception as e:
            result = "ERROR"
            details = f"Test error: {str(e)}"
            severity = "UNKNOWN"
        
        print(f"   Result: {result}")
        print(f"   Details: {details}")
        print()
        
        return {
            "test": "Mixed Content",
            "result": result,
            "details": details,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _test_protocol_downgrade(self):
        """Test for protocol downgrade attacks."""
        print("🔍 Test 4: Protocol Downgrade")
        
        try:
            # Attempt to force HTTP/1.0 or weak TLS
            session = requests.Session()
            
            # Try with different User-Agent that might trigger downgrade
            headers = {
                'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
                'Connection': 'close',
                'Upgrade-Insecure-Requests': '0'
            }
            
            response = session.get(
                f"{self.target_url}/health",
                headers=headers,
                timeout=5
            )
            
            # Check if connection was downgraded
            if response.status_code == 200:
                # Check response headers for security indicators
                if 'Upgrade-Insecure-Requests' in response.headers:
                    result = "SECURE"
                    details = "Server promotes secure connections"
                    severity = "LOW"
                else:
                    result = "VULNERABLE"
                    details = "Server accepts insecure connections without upgrade"
                    severity = "MEDIUM"
            else:
                result = "SECURE"
                details = "Insecure connection rejected"
                severity = "LOW"
                
        except Exception as e:
            result = "ERROR"
            details = f"Test error: {str(e)}"
            severity = "UNKNOWN"
        
        print(f"   Result: {result}")
        print(f"   Details: {details}")
        print()
        
        return {
            "test": "Protocol Downgrade",
            "result": result,
            "details": details,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _generate_report(self, results):
        """Generate attack report."""
        print("📊 Attack Report: A1 - TLS Authentication Bypass")
        print("=" * 60)
        
        vulnerable_tests = [r for r in results if r['result'] == 'VULNERABLE']
        secure_tests = [r for r in results if r['result'] == 'SECURE']
        error_tests = [r for r in results if r['result'] == 'ERROR']
        
        print(f"Total Tests: {len(results)}")
        print(f"Vulnerable: {len(vulnerable_tests)}")
        print(f"Secure: {len(secure_tests)}")
        print(f"Errors: {len(error_tests)}")
        print()
        
        if vulnerable_tests:
            print("🚨 VULNERABILITIES FOUND:")
            for vuln in vulnerable_tests:
                print(f"   - {vuln['test']}: {vuln['details']}")
            print()
        
        # Overall assessment
        if len(vulnerable_tests) == 0:
            overall_result = "SECURE"
            recommendation = "TLS enforcement appears to be properly implemented."
        elif len(vulnerable_tests) < len(results) / 2:
            overall_result = "PARTIALLY_SECURE"
            recommendation = "Some TLS vulnerabilities found. Review and fix identified issues."
        else:
            overall_result = "VULNERABLE"
            recommendation = "CRITICAL: Multiple TLS vulnerabilities found. Immediate action required."
        
        print(f"Overall Assessment: {overall_result}")
        print(f"Recommendation: {recommendation}")
        
        return {
            "attack_id": "A1",
            "attack_name": "TLS Authentication Bypass",
            "overall_result": overall_result,
            "recommendation": recommendation,
            "test_results": results,
            "summary": {
                "total_tests": len(results),
                "vulnerable": len(vulnerable_tests),
                "secure": len(secure_tests),
                "errors": len(error_tests)
            }
        }


def main():
    """Main execution function."""
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        target_url = "http://localhost:5000"
    
    attack = TLSBypassAttack(target_url)
    report = attack.execute_attack()
    
    # Exit with appropriate code
    if report['overall_result'] == 'VULNERABLE':
        sys.exit(1)
    elif report['overall_result'] == 'PARTIALLY_SECURE':
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()