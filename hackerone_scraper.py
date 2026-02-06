#!/usr/bin/env python3
"""
HackerOne Report Scraper
Scrapes vulnerability reports from HackerOne for ethical hacking research and LLM training.
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class HackerOneReport:
    """Data structure for a HackerOne report"""
    report_id: str
    title: str
    url: str
    severity: Optional[str] = None
    weakness: Optional[str] = None
    reporter: Optional[str] = None
    bounty: Optional[str] = None
    disclosed_at: Optional[str] = None
    program: Optional[str] = None
    description: Optional[str] = None
    impact: Optional[str] = None
    timeline: Optional[List[str]] = None
    vulnerability_type: Optional[str] = None
    raw_html: Optional[str] = None
    scraped_at: str = None

    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = datetime.now().isoformat()


class HackerOneScraper:
    """Main scraper class for HackerOne reports"""
    
    def __init__(self, delay: float = 2.0, max_retries: int = 3):
        """
        Initialize the scraper
        
        Args:
            delay: Delay between requests in seconds (be respectful)
            max_retries: Maximum number of retries for failed requests
        """
        self.delay = delay
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a page with retry logic
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching: {url} (attempt {attempt + 1}/{self.max_retries})")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                time.sleep(self.delay)  # Be respectful to the server
                return response.text
            except requests.RequestException as e:
                logger.warning(f"Error fetching {url}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.delay * (attempt + 1))  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
                    return None
    
    def extract_report_links_from_github(self, github_url: str) -> List[str]:
        """
        Extract HackerOne report links from a GitHub markdown file
        
        Args:
            github_url: URL to the GitHub markdown file
            
        Returns:
            List of HackerOne report URLs
        """
        # Convert GitHub URL to raw URL if needed
        if 'github.com' in github_url and '/blob/' in github_url:
            github_url = github_url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
        
        html = self.fetch_page(github_url)
        if not html:
            return []
        
        # Extract all HackerOne report links
        hackerone_pattern = r'https://hackerone\.com/reports/\d+'
        links = list(set(re.findall(hackerone_pattern, html)))
        
        logger.info(f"Found {len(links)} unique HackerOne report links")
        return links
    
    def parse_report_page(self, url: str) -> Optional[HackerOneReport]:
        """
        Parse a HackerOne report page
        
        Args:
            url: URL of the report
            
        Returns:
            HackerOneReport object or None if parsing failed
        """
        html = self.fetch_page(url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract report ID from URL
        report_id = url.split('/')[-1]
        
        # Initialize report data
        report_data = {
            'report_id': report_id,
            'url': url,
            'raw_html': html[:5000]  # Store first 5000 chars for reference
        }
        
        # Extract title
        title_elem = soup.find('h1', class_='spec-heading')
        if not title_elem:
            title_elem = soup.find('h1')
        report_data['title'] = title_elem.get_text(strip=True) if title_elem else f"Report {report_id}"
        
        # Extract severity
        severity_elem = soup.find('span', string=re.compile(r'Severity', re.I))
        if severity_elem:
            severity_value = severity_elem.find_next('span')
            if severity_value:
                report_data['severity'] = severity_value.get_text(strip=True)
        
        # Extract weakness/vulnerability type
        weakness_elem = soup.find('span', string=re.compile(r'Weakness', re.I))
        if weakness_elem:
            weakness_value = weakness_elem.find_next('a') or weakness_elem.find_next('span')
            if weakness_value:
                report_data['weakness'] = weakness_value.get_text(strip=True)
        
        # Extract reporter
        reporter_elem = soup.find('a', href=re.compile(r'/[^/]+$'))
        if reporter_elem and 'reports' not in reporter_elem.get('href', ''):
            report_data['reporter'] = reporter_elem.get_text(strip=True)
        
        # Extract bounty
        bounty_elem = soup.find('span', string=re.compile(r'Bounty', re.I))
        if bounty_elem:
            bounty_value = bounty_elem.find_next('span')
            if bounty_value:
                report_data['bounty'] = bounty_value.get_text(strip=True)
        
        # Extract disclosed date
        disclosed_elem = soup.find('time')
        if disclosed_elem:
            report_data['disclosed_at'] = disclosed_elem.get('datetime') or disclosed_elem.get_text(strip=True)
        
        # Extract program name
        program_elem = soup.find('a', href=re.compile(r'/[^/]+$'))
        if program_elem:
            report_data['program'] = program_elem.get_text(strip=True)
        
        # Extract description
        description_elem = soup.find('div', class_='formatted-text')
        if description_elem:
            report_data['description'] = description_elem.get_text(separator='\n', strip=True)[:2000]
        
        # Extract impact
        impact_heading = soup.find(['h2', 'h3'], string=re.compile(r'Impact', re.I))
        if impact_heading:
            impact_content = impact_heading.find_next(['p', 'div'])
            if impact_content:
                report_data['impact'] = impact_content.get_text(strip=True)[:1000]
        
        # Extract timeline events
        timeline = []
        timeline_items = soup.find_all('div', class_=re.compile(r'timeline|activity'))
        for item in timeline_items[:10]:  # Limit to first 10 events
            text = item.get_text(strip=True)
            if text:
                timeline.append(text[:200])
        report_data['timeline'] = timeline if timeline else None
        
        # Determine vulnerability type from weakness or title
        vuln_type = self._determine_vuln_type(report_data.get('weakness', ''), report_data['title'])
        report_data['vulnerability_type'] = vuln_type
        
        return HackerOneReport(**report_data)
    
    def _determine_vuln_type(self, weakness: str, title: str) -> str:
        """
        Determine the general vulnerability type
        
        Args:
            weakness: Weakness field from report
            title: Report title
            
        Returns:
            General vulnerability category
        """
        combined = f"{weakness} {title}".lower()
        
        vuln_types = {
            'xss': ['xss', 'cross-site scripting', 'cross site scripting'],
            'sqli': ['sql injection', 'sqli'],
            'rce': ['remote code execution', 'rce', 'code execution'],
            'ssrf': ['ssrf', 'server-side request forgery'],
            'csrf': ['csrf', 'cross-site request forgery'],
            'idor': ['idor', 'insecure direct object reference'],
            'auth_bypass': ['authentication bypass', 'auth bypass', 'authorization'],
            'subdomain_takeover': ['subdomain takeover', 'subdomain', 'takeover'],
            'file_upload': ['file upload', 'arbitrary file upload'],
            'path_traversal': ['path traversal', 'directory traversal', 'lfi'],
            'xxe': ['xxe', 'xml external entity'],
            'deserialization': ['deserialization', 'insecure deserialization'],
            'information_disclosure': ['information disclosure', 'sensitive data'],
            'open_redirect': ['open redirect', 'url redirection'],
        }
        
        for vuln_type, keywords in vuln_types.items():
            if any(keyword in combined for keyword in keywords):
                return vuln_type
        
        return 'other'
    
    def scrape_reports(self, report_urls: List[str], max_reports: Optional[int] = None) -> List[HackerOneReport]:
        """
        Scrape multiple reports
        
        Args:
            report_urls: List of report URLs to scrape
            max_reports: Maximum number of reports to scrape (None for all)
            
        Returns:
            List of HackerOneReport objects
        """
        reports = []
        urls_to_process = report_urls[:max_reports] if max_reports else report_urls
        
        logger.info(f"Starting to scrape {len(urls_to_process)} reports")
        
        for i, url in enumerate(urls_to_process, 1):
            logger.info(f"Processing report {i}/{len(urls_to_process)}: {url}")
            
            report = self.parse_report_page(url)
            if report:
                reports.append(report)
                logger.info(f"Successfully scraped: {report.title}")
            else:
                logger.warning(f"Failed to scrape: {url}")
        
        logger.info(f"Successfully scraped {len(reports)}/{len(urls_to_process)} reports")
        return reports


class DatasetGenerator:
    """Generate datasets in various formats for LLM training"""
    
    @staticmethod
    def save_json(reports: List[HackerOneReport], filename: str):
        """Save reports as JSON"""
        data = [asdict(report) for report in reports]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(reports)} reports to {filename}")
    
    @staticmethod
    def save_csv(reports: List[HackerOneReport], filename: str):
        """Save reports as CSV"""
        if not reports:
            return
        
        # Convert to dict and flatten
        data = []
        for report in reports:
            report_dict = asdict(report)
            # Convert lists to strings
            if report_dict['timeline']:
                report_dict['timeline'] = ' | '.join(report_dict['timeline'])
            data.append(report_dict)
        
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        logger.info(f"Saved {len(reports)} reports to {filename}")
    
    @staticmethod
    def save_llm_training_format(reports: List[HackerOneReport], filename: str):
        """
        Save in a format suitable for LLM fine-tuning (JSONL with prompt/completion pairs)
        """
        with open(filename, 'w', encoding='utf-8') as f:
            for report in reports:
                # Create a training example
                prompt = f"Analyze this security vulnerability report:\n\nTitle: {report.title}\nType: {report.vulnerability_type}\nSeverity: {report.severity}\n\nDescription:\n{report.description[:500] if report.description else 'N/A'}"
                
                completion = f"Vulnerability Analysis:\n\n"
                completion += f"Report ID: {report.report_id}\n"
                completion += f"Classification: {report.vulnerability_type}\n"
                completion += f"Severity Level: {report.severity}\n"
                completion += f"Weakness: {report.weakness}\n"
                if report.impact:
                    completion += f"\nImpact:\n{report.impact}\n"
                if report.bounty:
                    completion += f"\nBounty Awarded: {report.bounty}\n"
                completion += f"\nProgram: {report.program}\n"
                completion += f"Reporter: {report.reporter}\n"
                
                training_pair = {
                    "prompt": prompt,
                    "completion": completion,
                    "metadata": {
                        "report_id": report.report_id,
                        "url": report.url,
                        "vulnerability_type": report.vulnerability_type
                    }
                }
                
                f.write(json.dumps(training_pair, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved {len(reports)} training examples to {filename}")
    
    @staticmethod
    def generate_summary(reports: List[HackerOneReport]) -> Dict:
        """Generate a summary of the scraped data"""
        if not reports:
            return {}
        
        summary = {
            'total_reports': len(reports),
            'vulnerability_types': {},
            'severity_distribution': {},
            'programs': {},
            'reporters': {},
            'total_bounty': 0,
            'scrape_date': datetime.now().isoformat()
        }
        
        for report in reports:
            # Count vulnerability types
            vtype = report.vulnerability_type or 'unknown'
            summary['vulnerability_types'][vtype] = summary['vulnerability_types'].get(vtype, 0) + 1
            
            # Count severities
            sev = report.severity or 'unknown'
            summary['severity_distribution'][sev] = summary['severity_distribution'].get(sev, 0) + 1
            
            # Count programs
            prog = report.program or 'unknown'
            summary['programs'][prog] = summary['programs'].get(prog, 0) + 1
            
            # Count reporters
            rep = report.reporter or 'unknown'
            summary['reporters'][rep] = summary['reporters'].get(rep, 0) + 1
            
            # Sum bounties (attempt to parse)
            if report.bounty:
                try:
                    bounty_amount = float(re.sub(r'[^\d.]', '', report.bounty))
                    summary['total_bounty'] += bounty_amount
                except:
                    pass
        
        return summary


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Scrape HackerOne reports for security research')
    parser.add_argument('--url', type=str, 
                       default='https://github.com/reddelexc/hackerone-reports/blob/master/tops_by_bug_type/TOPSUBDOMAINTAKEOVER.md',
                       help='GitHub URL containing HackerOne report links')
    parser.add_argument('--max-reports', type=int, default=None,
                       help='Maximum number of reports to scrape (default: all)')
    parser.add_argument('--delay', type=float, default=2.0,
                       help='Delay between requests in seconds (default: 2.0)')
    parser.add_argument('--output-dir', type=str, default='/mnt/user-data/outputs',
                       help='Output directory for datasets')
    
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = HackerOneScraper(delay=args.delay)
    
    # Extract report links from GitHub
    logger.info(f"Extracting report links from: {args.url}")
    report_urls = scraper.extract_report_links_from_github(args.url)
    
    if not report_urls:
        logger.error("No report URLs found!")
        return
    
    # Scrape reports
    reports = scraper.scrape_reports(report_urls, max_reports=args.max_reports)
    
    if not reports:
        logger.error("No reports successfully scraped!")
        return
    
    # Generate datasets
    dataset_gen = DatasetGenerator()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save in multiple formats
    dataset_gen.save_json(reports, f'{args.output_dir}/hackerone_reports_{timestamp}.json')
    dataset_gen.save_csv(reports, f'{args.output_dir}/hackerone_reports_{timestamp}.csv')
    dataset_gen.save_llm_training_format(reports, f'{args.output_dir}/hackerone_training_{timestamp}.jsonl')
    
    # Generate and save summary
    summary = dataset_gen.generate_summary(reports)
    with open(f'{args.output_dir}/scrape_summary_{timestamp}.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info("Scraping completed successfully!")
    logger.info(f"Summary: {summary}")


if __name__ == '__main__':
    main()
