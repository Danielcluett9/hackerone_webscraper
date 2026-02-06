#!/usr/bin/env python3
"""
Dataset Analyzer - Analyze scraped HackerOne reports
"""

import json
import argparse
from collections import Counter
from typing import Dict, List
import matplotlib.pyplot as plt
from datetime import datetime


class DatasetAnalyzer:
    """Analyze scraped vulnerability reports"""
    
    def __init__(self, json_file: str):
        """Load dataset from JSON file"""
        with open(json_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        print(f"Loaded {len(self.data)} reports")
    
    def analyze_vulnerability_types(self) -> Dict:
        """Analyze distribution of vulnerability types"""
        vuln_types = [report.get('vulnerability_type', 'unknown') for report in self.data]
        return dict(Counter(vuln_types))
    
    def analyze_severity(self) -> Dict:
        """Analyze severity distribution"""
        severities = [report.get('severity', 'unknown') for report in self.data]
        return dict(Counter(severities))
    
    def analyze_programs(self, top_n: int = 10) -> Dict:
        """Get top N programs by report count"""
        programs = [report.get('program', 'unknown') for report in self.data]
        counter = Counter(programs)
        return dict(counter.most_common(top_n))
    
    def analyze_reporters(self, top_n: int = 10) -> Dict:
        """Get top N reporters by report count"""
        reporters = [report.get('reporter', 'unknown') for report in self.data]
        counter = Counter(reporters)
        return dict(counter.most_common(top_n))
    
    def analyze_bounties(self) -> Dict:
        """Analyze bounty statistics"""
        bounties = []
        for report in self.data:
            bounty = report.get('bounty')
            if bounty and bounty != 'N/A':
                # Try to extract numeric value
                import re
                match = re.search(r'[\d,]+\.?\d*', bounty)
                if match:
                    try:
                        amount = float(match.group().replace(',', ''))
                        bounties.append(amount)
                    except:
                        pass
        
        if not bounties:
            return {'error': 'No bounty data available'}
        
        return {
            'total': sum(bounties),
            'average': sum(bounties) / len(bounties),
            'min': min(bounties),
            'max': max(bounties),
            'count': len(bounties)
        }
    
    def generate_report(self) -> str:
        """Generate a comprehensive analysis report"""
        report = []
        report.append("=" * 70)
        report.append("HackerOne Dataset Analysis Report")
        report.append("=" * 70)
        report.append(f"\nTotal Reports: {len(self.data)}")
        report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Vulnerability Types
        report.append("\n" + "-" * 70)
        report.append("VULNERABILITY TYPE DISTRIBUTION")
        report.append("-" * 70)
        vuln_types = self.analyze_vulnerability_types()
        for vtype, count in sorted(vuln_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(self.data)) * 100
            report.append(f"  {vtype:30s}: {count:4d} ({percentage:5.2f}%)")
        
        # Severity Distribution
        report.append("\n" + "-" * 70)
        report.append("SEVERITY DISTRIBUTION")
        report.append("-" * 70)
        severities = self.analyze_severity()
        severity_order = ['Critical', 'High', 'Medium', 'Low', 'None', 'unknown']
        for severity in severity_order:
            if severity in severities:
                count = severities[severity]
                percentage = (count / len(self.data)) * 100
                report.append(f"  {severity:15s}: {count:4d} ({percentage:5.2f}%)")
        
        # Top Programs
        report.append("\n" + "-" * 70)
        report.append("TOP 10 PROGRAMS")
        report.append("-" * 70)
        programs = self.analyze_programs(10)
        for i, (program, count) in enumerate(programs.items(), 1):
            report.append(f"  {i:2d}. {program:40s}: {count:4d} reports")
        
        # Top Reporters
        report.append("\n" + "-" * 70)
        report.append("TOP 10 REPORTERS")
        report.append("-" * 70)
        reporters = self.analyze_reporters(10)
        for i, (reporter, count) in enumerate(reporters.items(), 1):
            report.append(f"  {i:2d}. {reporter:30s}: {count:4d} reports")
        
        # Bounty Statistics
        report.append("\n" + "-" * 70)
        report.append("BOUNTY STATISTICS")
        report.append("-" * 70)
        bounties = self.analyze_bounties()
        if 'error' not in bounties:
            report.append(f"  Total Bounties Paid: ${bounties['total']:,.2f}")
            report.append(f"  Average Bounty: ${bounties['average']:,.2f}")
            report.append(f"  Minimum Bounty: ${bounties['min']:,.2f}")
            report.append(f"  Maximum Bounty: ${bounties['max']:,.2f}")
            report.append(f"  Reports with Bounty: {bounties['count']}")
        else:
            report.append(f"  {bounties['error']}")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)
    
    def save_report(self, filename: str):
        """Save analysis report to file"""
        report = self.generate_report()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report saved to {filename}")
    
    def create_visualizations(self, output_prefix: str):
        """Create visualization charts (requires matplotlib)"""
        try:
            import matplotlib.pyplot as plt
            
            # Vulnerability types pie chart
            vuln_types = self.analyze_vulnerability_types()
            if vuln_types:
                plt.figure(figsize=(10, 8))
                plt.pie(vuln_types.values(), labels=vuln_types.keys(), autopct='%1.1f%%')
                plt.title('Vulnerability Type Distribution')
                plt.savefig(f'{output_prefix}_vulntypes.png')
                plt.close()
                print(f"Saved vulnerability types chart to {output_prefix}_vulntypes.png")
            
            # Severity bar chart
            severities = self.analyze_severity()
            if severities:
                plt.figure(figsize=(10, 6))
                plt.bar(severities.keys(), severities.values())
                plt.xlabel('Severity')
                plt.ylabel('Count')
                plt.title('Severity Distribution')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(f'{output_prefix}_severity.png')
                plt.close()
                print(f"Saved severity chart to {output_prefix}_severity.png")
            
        except ImportError:
            print("Matplotlib not available - skipping visualizations")


def main():
    parser = argparse.ArgumentParser(description='Analyze HackerOne dataset')
    parser.add_argument('json_file', help='Path to JSON dataset file')
    parser.add_argument('--output', '-o', default='/mnt/user-data/outputs/analysis_report.txt',
                       help='Output file for analysis report')
    parser.add_argument('--visualize', '-v', action='store_true',
                       help='Create visualization charts')
    
    args = parser.parse_args()
    
    analyzer = DatasetAnalyzer(args.json_file)
    
    # Print to console
    print(analyzer.generate_report())
    
    # Save to file
    analyzer.save_report(args.output)
    
    # Create visualizations if requested
    if args.visualize:
        output_prefix = args.output.replace('.txt', '')
        analyzer.create_visualizations(output_prefix)


if __name__ == '__main__':
    main()
