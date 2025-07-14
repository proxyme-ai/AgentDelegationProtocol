#!/usr/bin/env python3
"""
Agent Delegation Protocol - Attack Simulation Runner

This script orchestrates comprehensive security testing of the Agent Delegation Protocol
by running the attack simulator and generating detailed reports with visualizations.
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from attack_simulator import AttackSimulator


class AttackSimulationRunner:
    """Orchestrates comprehensive attack simulation and reporting."""
    
    def __init__(self, auth_url="http://localhost:5000", resource_url="http://localhost:6000"):
        self.auth_url = auth_url
        self.resource_url = resource_url
        self.output_dir = Path("simulation_results")
        self.output_dir.mkdir(exist_ok=True)
        
    def run_comprehensive_simulation(self):
        """Run comprehensive attack simulation with full reporting."""
        print("🚀 Starting Comprehensive Attack Simulation")
        print("=" * 80)
        print(f"Auth Server: {self.auth_url}")
        print(f"Resource Server: {self.resource_url}")
        print(f"Output Directory: {self.output_dir}")
        print()
        
        # Check if servers are running
        if not self._check_servers():
            print("❌ Servers not accessible. Please start the servers first.")
            return False
        
        # Initialize simulator
        simulator = AttackSimulator(self.auth_url, self.resource_url)
        
        # Run all attacks
        print("🎯 Executing attack scenarios...")
        start_time = time.time()
        
        try:
            results = simulator.run_all_attacks()
            end_time = time.time()
            
            # Generate comprehensive report
            self._generate_comprehensive_report(results, end_time - start_time)
            
            # Generate individual scenario reports
            self._generate_scenario_reports(results)
            
            # Generate executive summary
            self._generate_executive_summary(results)
            
            # Generate mitigation recommendations
            self._generate_mitigation_report(results)
            
            print("\n✅ Simulation completed successfully!")
            print(f"📊 Reports generated in: {self.output_dir}")
            
            return True
            
        except Exception as e:
            print(f"❌ Simulation failed: {str(e)}")
            return False
    
    def _check_servers(self):
        """Check if required servers are running."""
        import requests
        
        try:
            # Check auth server
            auth_response = requests.get(f"{self.auth_url}/health", timeout=5)
            if auth_response.status_code != 200:
                print(f"⚠️ Auth server not responding properly: {auth_response.status_code}")
                return False
            
            # Check resource server
            resource_response = requests.get(f"{self.resource_url}/health", timeout=5)
            if resource_response.status_code != 200:
                print(f"⚠️ Resource server not responding properly: {resource_response.status_code}")
                return False
            
            print("✅ Both servers are accessible")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Server connectivity check failed: {str(e)}")
            return False
    
    def _generate_comprehensive_report(self, results, duration):
        """Generate comprehensive HTML report with visualizations."""
        
        # Calculate summary statistics
        total_tests = sum(len(category_results) for category_results in results.values())
        vulnerabilities = []
        blocked_attacks = []
        errors = []
        
        for category, category_results in results.items():
            for result in category_results:
                if result["result"] == "SUCCESS" and result["scenario"]["expected_result"] == "BLOCKED":
                    vulnerabilities.append(result)
                elif result["result"] == "BLOCKED":
                    blocked_attacks.append(result)
                elif result["result"] == "ERROR":
                    errors.append(result)
        
        # Generate HTML report
        html_content = self._create_html_report(results, {
            'total_tests': total_tests,
            'vulnerabilities': len(vulnerabilities),
            'blocked_attacks': len(blocked_attacks),
            'errors': len(errors),
            'duration': duration,
            'success_rate': (len(blocked_attacks) / total_tests * 100) if total_tests > 0 else 0
        })
        
        # Save HTML report
        html_file = self.output_dir / f"security_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Save JSON results
        json_file = self.output_dir / f"simulation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w') as f:
            json.dump({
                'timestamp': datetime.utcnow().isoformat(),
                'duration': duration,
                'summary': {
                    'total_tests': total_tests,
                    'vulnerabilities': len(vulnerabilities),
                    'blocked_attacks': len(blocked_attacks),
                    'errors': len(errors)
                },
                'results': results
            }, f, indent=2)
        
        print(f"📄 Comprehensive report: {html_file}")
        print(f"📊 JSON results: {json_file}")
    
    def _create_html_report(self, results, summary):
        """Create HTML report with charts and detailed analysis."""
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Delegation Protocol - Security Assessment Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .header h1 {{ color: #2c3e50; margin-bottom: 10px; }}
        .header .subtitle {{ color: #7f8c8d; font-size: 18px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }}
        .summary-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .summary-card.vulnerable {{ background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); }}
        .summary-card.secure {{ background: linear-gradient(135deg, #00d2d3 0%, #54a0ff 100%); }}
        .summary-card h3 {{ margin: 0 0 10px 0; font-size: 24px; }}
        .summary-card p {{ margin: 0; font-size: 14px; opacity: 0.9; }}
        .chart-container {{ margin: 40px 0; }}
        .chart-wrapper {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .results-section {{ margin-top: 40px; }}
        .category {{ margin-bottom: 30px; }}
        .category h3 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .test-result {{ background: #f8f9fa; margin: 10px 0; padding: 15px; border-radius: 8px; border-left: 4px solid #ddd; }}
        .test-result.success {{ border-left-color: #27ae60; }}
        .test-result.blocked {{ border-left-color: #27ae60; }}
        .test-result.vulnerable {{ border-left-color: #e74c3c; }}
        .test-result.error {{ border-left-color: #f39c12; }}
        .test-result.partial {{ border-left-color: #f39c12; }}
        .test-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .test-title {{ font-weight: bold; color: #2c3e50; }}
        .test-status {{ padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }}
        .status-success {{ background: #d4edda; color: #155724; }}
        .status-blocked {{ background: #d4edda; color: #155724; }}
        .status-vulnerable {{ background: #f8d7da; color: #721c24; }}
        .status-error {{ background: #fff3cd; color: #856404; }}
        .status-partial {{ background: #fff3cd; color: #856404; }}
        .recommendations {{ background: #e8f4fd; padding: 20px; border-radius: 10px; margin-top: 30px; }}
        .recommendations h3 {{ color: #2980b9; margin-top: 0; }}
        .vulnerability-list {{ background: #fdf2f2; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .vulnerability-list h3 {{ color: #c0392b; margin-top: 0; }}
        .vulnerability-item {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #e74c3c; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Agent Delegation Protocol</h1>
            <div class="subtitle">Security Assessment Report</div>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Duration: {summary['duration']:.2f} seconds</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>{summary['total_tests']}</h3>
                <p>Total Tests</p>
            </div>
            <div class="summary-card {'vulnerable' if summary['vulnerabilities'] > 0 else 'secure'}">
                <h3>{summary['vulnerabilities']}</h3>
                <p>Vulnerabilities</p>
            </div>
            <div class="summary-card secure">
                <h3>{summary['blocked_attacks']}</h3>
                <p>Attacks Blocked</p>
            </div>
            <div class="summary-card">
                <h3>{summary['success_rate']:.1f}%</h3>
                <p>Success Rate</p>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-wrapper">
                <canvas id="summaryChart" width="400" height="200"></canvas>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-wrapper">
                <canvas id="categoryChart" width="400" height="200"></canvas>
            </div>
        </div>
"""
        
        # Add vulnerability section if any found
        vulnerabilities = []
        for category, category_results in results.items():
            for result in category_results:
                if result["result"] == "SUCCESS" and result["scenario"]["expected_result"] == "BLOCKED":
                    vulnerabilities.append(result)
        
        if vulnerabilities:
            html += """
        <div class="vulnerability-list">
            <h3>🚨 Critical Vulnerabilities Found</h3>
"""
            for vuln in vulnerabilities:
                html += f"""
            <div class="vulnerability-item">
                <strong>{vuln['scenario']['id']}: {vuln['scenario']['name']}</strong><br>
                <strong>Severity:</strong> {vuln['scenario']['severity']}<br>
                <strong>Details:</strong> {vuln['details']}
            </div>
"""
            html += "</div>"
        
        # Add detailed results
        html += '<div class="results-section"><h2>Detailed Test Results</h2>'
        
        for category, category_results in results.items():
            html += f'<div class="category"><h3>{category.upper()} Attacks</h3>'
            
            for result in category_results:
                status_class = result['result'].lower()
                if result['result'] == 'SUCCESS' and result['scenario']['expected_result'] == 'BLOCKED':
                    status_class = 'vulnerable'
                
                html += f"""
                <div class="test-result {status_class}">
                    <div class="test-header">
                        <div class="test-title">{result['scenario']['id']}: {result['scenario']['name']}</div>
                        <div class="test-status status-{status_class}">{result['result']}</div>
                    </div>
                    <p><strong>Description:</strong> {result['scenario']['description']}</p>
                    <p><strong>Details:</strong> {result['details']}</p>
                    <p><strong>Severity:</strong> {result['scenario']['severity']}</p>
                </div>
"""
            html += '</div>'
        
        html += '</div>'
        
        # Add recommendations
        html += """
        <div class="recommendations">
            <h3>🔧 Recommendations</h3>
            <ul>
                <li><strong>Immediate Actions:</strong> Address all critical vulnerabilities found</li>
                <li><strong>Enhanced Validation:</strong> Implement comprehensive agent registration validation</li>
                <li><strong>Rate Limiting:</strong> Deploy rate limiting across all endpoints</li>
                <li><strong>Monitoring:</strong> Implement real-time security monitoring</li>
                <li><strong>Regular Testing:</strong> Schedule regular security assessments</li>
            </ul>
        </div>
"""
        
        # Add JavaScript for charts
        category_data = {}
        for category, category_results in results.items():
            category_data[category] = {
                'total': len(category_results),
                'vulnerable': len([r for r in category_results if r['result'] == 'SUCCESS' and r['scenario']['expected_result'] == 'BLOCKED']),
                'blocked': len([r for r in category_results if r['result'] == 'BLOCKED']),
                'errors': len([r for r in category_results if r['result'] == 'ERROR'])
            }
        
        html += f"""
    </div>
    
    <script>
        // Summary Chart
        const summaryCtx = document.getElementById('summaryChart').getContext('2d');
        new Chart(summaryCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['Vulnerabilities', 'Blocked Attacks', 'Errors'],
                datasets: [{{
                    data: [{summary['vulnerabilities']}, {summary['blocked_attacks']}, {summary['errors']}],
                    backgroundColor: ['#e74c3c', '#27ae60', '#f39c12']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Overall Security Assessment Results'
                    }}
                }}
            }}
        }});
        
        // Category Chart
        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        const categoryData = {json.dumps(category_data)};
        
        new Chart(categoryCtx, {{
            type: 'bar',
            data: {{
                labels: Object.keys(categoryData),
                datasets: [
                    {{
                        label: 'Vulnerabilities',
                        data: Object.values(categoryData).map(d => d.vulnerable),
                        backgroundColor: '#e74c3c'
                    }},
                    {{
                        label: 'Blocked',
                        data: Object.values(categoryData).map(d => d.blocked),
                        backgroundColor: '#27ae60'
                    }},
                    {{
                        label: 'Errors',
                        data: Object.values(categoryData).map(d => d.errors),
                        backgroundColor: '#f39c12'
                    }}
                ]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Results by Attack Category'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        
        return html
    
    def _generate_scenario_reports(self, results):
        """Generate individual reports for each attack scenario."""
        scenarios_dir = self.output_dir / "scenarios"
        scenarios_dir.mkdir(exist_ok=True)
        
        for category, category_results in results.items():
            for result in category_results:
                scenario_file = scenarios_dir / f"{result['scenario']['id']}_{result['scenario']['name'].replace(' ', '_').lower()}.json"
                with open(scenario_file, 'w') as f:
                    json.dump(result, f, indent=2)
        
        print(f"📁 Individual scenario reports: {scenarios_dir}")
    
    def _generate_executive_summary(self, results):
        """Generate executive summary for management."""
        
        # Calculate key metrics
        total_tests = sum(len(category_results) for category_results in results.values())
        critical_vulns = 0
        high_vulns = 0
        medium_vulns = 0
        
        for category, category_results in results.items():
            for result in category_results:
                if result["result"] == "SUCCESS" and result["scenario"]["expected_result"] == "BLOCKED":
                    severity = result["scenario"]["severity"]
                    if severity == "CRITICAL":
                        critical_vulns += 1
                    elif severity == "HIGH":
                        high_vulns += 1
                    elif severity == "MEDIUM":
                        medium_vulns += 1
        
        # Determine overall risk level
        if critical_vulns > 0:
            risk_level = "CRITICAL"
            risk_color = "🔴"
        elif high_vulns > 2:
            risk_level = "HIGH"
            risk_color = "🟠"
        elif high_vulns > 0 or medium_vulns > 3:
            risk_level = "MEDIUM"
            risk_color = "🟡"
        else:
            risk_level = "LOW"
            risk_color = "🟢"
        
        summary_content = f"""# Executive Summary - Agent Delegation Protocol Security Assessment

**Assessment Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Overall Risk Level:** {risk_color} {risk_level}  
**Total Tests Conducted:** {total_tests}  

## Key Findings

### Security Posture
- **Critical Vulnerabilities:** {critical_vulns}
- **High Risk Issues:** {high_vulns}
- **Medium Risk Issues:** {medium_vulns}
- **Overall Success Rate:** {((total_tests - critical_vulns - high_vulns - medium_vulns) / total_tests * 100):.1f}%

### Risk Assessment
{risk_color} **{risk_level} RISK** - {'Immediate action required' if risk_level in ['CRITICAL', 'HIGH'] else 'Monitoring and improvement recommended' if risk_level == 'MEDIUM' else 'Good security posture maintained'}

## Business Impact

### Immediate Concerns
{'- **CRITICAL**: System vulnerable to serious security breaches' if critical_vulns > 0 else ''}
{'- **HIGH**: Multiple high-risk vulnerabilities require urgent attention' if high_vulns > 2 else ''}
{'- **MEDIUM**: Some security improvements needed' if medium_vulns > 0 else ''}

### Recommendations

#### Immediate Actions (0-30 days)
1. Address all critical and high-severity vulnerabilities
2. Implement enhanced agent registration validation
3. Deploy comprehensive rate limiting
4. Establish security monitoring

#### Short-term Actions (30-90 days)
1. Implement comprehensive audit logging
2. Deploy behavioral monitoring for agents
3. Enhance token binding mechanisms
4. Establish incident response procedures

#### Long-term Actions (90+ days)
1. Implement zero-trust architecture
2. Deploy advanced threat detection
3. Regular security assessments
4. Security awareness training

## Compliance Status

The current implementation shows {'significant gaps' if risk_level in ['CRITICAL', 'HIGH'] else 'some gaps' if risk_level == 'MEDIUM' else 'good alignment'} with security best practices and industry standards.

## Next Steps

1. **Immediate**: Review and prioritize vulnerability remediation
2. **Week 1**: Implement critical security fixes
3. **Month 1**: Deploy enhanced security controls
4. **Ongoing**: Regular security monitoring and assessment

---
*This assessment was conducted using automated security testing tools and should be supplemented with manual security review and penetration testing.*
"""
        
        summary_file = self.output_dir / "executive_summary.md"
        with open(summary_file, 'w') as f:
            f.write(summary_content)
        
        print(f"📋 Executive summary: {summary_file}")
    
    def _generate_mitigation_report(self, results):
        """Generate specific mitigation recommendations based on findings."""
        
        vulnerabilities = []
        for category, category_results in results.items():
            for result in category_results:
                if result["result"] == "SUCCESS" and result["scenario"]["expected_result"] == "BLOCKED":
                    vulnerabilities.append(result)
        
        mitigation_content = f"""# Mitigation Action Plan - Agent Delegation Protocol

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Vulnerabilities Found:** {len(vulnerabilities)}  

## Priority Actions

"""
        
        if vulnerabilities:
            # Group by severity
            critical = [v for v in vulnerabilities if v['scenario']['severity'] == 'CRITICAL']
            high = [v for v in vulnerabilities if v['scenario']['severity'] == 'HIGH']
            medium = [v for v in vulnerabilities if v['scenario']['severity'] == 'MEDIUM']
            
            if critical:
                mitigation_content += "### 🚨 CRITICAL Priority (Fix Immediately)\n\n"
                for vuln in critical:
                    mitigation_content += f"#### {vuln['scenario']['id']}: {vuln['scenario']['name']}\n"
                    mitigation_content += f"**Issue:** {vuln['details']}\n"
                    mitigation_content += f"**Impact:** {self._get_impact_description(vuln['scenario']['id'])}\n"
                    mitigation_content += f"**Mitigation:** {self._get_mitigation_steps(vuln['scenario']['id'])}\n\n"
            
            if high:
                mitigation_content += "### ⚠️ HIGH Priority (Fix within 30 days)\n\n"
                for vuln in high:
                    mitigation_content += f"#### {vuln['scenario']['id']}: {vuln['scenario']['name']}\n"
                    mitigation_content += f"**Issue:** {vuln['details']}\n"
                    mitigation_content += f"**Mitigation:** {self._get_mitigation_steps(vuln['scenario']['id'])}\n\n"
            
            if medium:
                mitigation_content += "### 📋 MEDIUM Priority (Fix within 90 days)\n\n"
                for vuln in medium:
                    mitigation_content += f"#### {vuln['scenario']['id']}: {vuln['scenario']['name']}\n"
                    mitigation_content += f"**Issue:** {vuln['details']}\n"
                    mitigation_content += f"**Mitigation:** {self._get_mitigation_steps(vuln['scenario']['id'])}\n\n"
        else:
            mitigation_content += "✅ **No critical vulnerabilities found!**\n\nThe system demonstrates good security posture, but continue with regular security assessments and monitoring.\n\n"
        
        mitigation_content += """
## General Security Improvements

### Enhanced Monitoring
- Implement comprehensive audit logging
- Deploy real-time security monitoring
- Set up automated alerting for suspicious activities

### Access Controls
- Strengthen agent registration validation
- Implement behavioral monitoring
- Deploy advanced rate limiting

### Infrastructure Security
- Ensure HTTPS enforcement
- Implement security headers
- Regular security updates

## Testing and Validation

### Continuous Security Testing
- Schedule regular automated security scans
- Conduct periodic penetration testing
- Implement security regression testing

### Monitoring and Metrics
- Track security metrics and KPIs
- Monitor for new threat patterns
- Regular security posture assessments

---
*Implement these mitigations in priority order and retest to validate fixes.*
"""
        
        mitigation_file = self.output_dir / "mitigation_action_plan.md"
        with open(mitigation_file, 'w') as f:
            f.write(mitigation_content)
        
        print(f"🔧 Mitigation plan: {mitigation_file}")
    
    def _get_impact_description(self, scenario_id):
        """Get impact description for specific scenario."""
        impacts = {
            'A1': 'Unencrypted communication allows traffic interception and manipulation',
            'A2': 'Unauthorized access to protected resources without authentication',
            'A3': 'Extended access beyond intended timeframe, potential for abuse',
            'A4': 'Identity confusion and unauthorized actions on behalf of other agents',
            'A5': 'Token misuse across different agent contexts',
            'A6': 'Violation of access policies and unauthorized resource access',
            'A7': 'Uncontrolled agent proliferation and potential coordinated attacks',
            'C1': 'Malicious agents gaining legitimate access to the system',
            'C5': 'Multiple fake identities enabling coordinated attacks'
        }
        return impacts.get(scenario_id, 'Security control bypass with potential for system compromise')
    
    def _get_mitigation_steps(self, scenario_id):
        """Get specific mitigation steps for scenario."""
        mitigations = {
            'A1': 'Enforce HTTPS-only connections, implement HSTS headers, redirect HTTP to HTTPS',
            'A2': 'Ensure all endpoints require valid authentication tokens, implement proper authorization checks',
            'A3': 'Implement proper token expiration validation, use short-lived tokens with refresh mechanism',
            'A4': 'Strengthen JWT signature validation, implement token binding to agent identity',
            'A5': 'Implement cryptographic token binding, validate token-agent relationship',
            'A6': 'Implement comprehensive policy engine, validate all scope requests against policies',
            'A7': 'Implement human-in-the-loop verification for agent registration, detect cloning patterns',
            'C1': 'Enhanced agent validation pipeline, reputation system, manual approval for suspicious agents',
            'C5': 'Rate limiting for registrations, identity verification, behavioral analysis'
        }
        return mitigations.get(scenario_id, 'Review and strengthen the affected security control')


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Delegation Protocol Attack Simulation Runner")
    parser.add_argument("--auth-url", default="http://localhost:5000", help="Authorization server URL")
    parser.add_argument("--resource-url", default="http://localhost:6000", help="Resource server URL")
    parser.add_argument("--output-dir", help="Output directory for reports")
    
    args = parser.parse_args()
    
    runner = AttackSimulationRunner(args.auth_url, args.resource_url)
    
    if args.output_dir:
        runner.output_dir = Path(args.output_dir)
        runner.output_dir.mkdir(exist_ok=True)
    
    success = runner.run_comprehensive_simulation()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()