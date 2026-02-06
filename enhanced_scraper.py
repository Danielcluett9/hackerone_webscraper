#!/usr/bin/env python3
"""
Enhanced HackerOne Report Scraper - Extracts data from meta tags when full page is not accessible
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from hackerone_scraper import HackerOneScraper, HackerOneReport, DatasetGenerator
from bs4 import BeautifulSoup
import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EnhancedHackerOneScraper(HackerOneScraper):
    """Enhanced scraper that extracts from meta tags"""
    
    def parse_report_page(self, url: str) -> Optional[HackerOneReport]:
        """
        Parse a HackerOne report page, falling back to meta tag extraction if needed
        
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
            'raw_html': html[:5000]
        }
        
        # Try to extract from meta tags (works even when logged out)
        title_meta = soup.find('meta', property='og:title')
        if title_meta and title_meta.get('content'):
            full_title = title_meta.get('content')
            # Extract program name and title
            # Format: "Program disclosed on HackerOne: Title..."
            match = re.match(r'([^d]+?)\s+disclosed on HackerOne:\s+(.+)', full_title)
            if match:
                report_data['program'] = match.group(1).strip()
                report_data['title'] = match.group(2).strip()
            else:
                report_data['title'] = full_title
        
        # Extract description from meta tags
        desc_meta = soup.find('meta', {'name': 'og:description'}) or soup.find('meta', {'name': 'description'})
        if desc_meta and desc_meta.get('content'):
            report_data['description'] = desc_meta.get('content')[:2000]
        
        # Try to extract severity from description
        if report_data.get('description'):
            desc = report_data['description'].lower()
            if 'critical' in desc:
                report_data['severity'] = 'Critical'
            elif 'high' in desc:
                report_data['severity'] = 'High'
            elif 'medium' in desc:
                report_data['severity'] = 'Medium'
            elif 'low' in desc:
                report_data['severity'] = 'Low'
        
        # Now try to parse the full page content if available
        # Check if we have access to the actual report content
        if 'signed-out' not in html and 'sign in or sign up' not in html.lower():
            # We have access to the full page
            report_data.update(self._parse_full_page(soup, report_data))
        
        # Determine vulnerability type
        combined_text = f"{report_data.get('title', '')} {report_data.get('description', '')} {report_data.get('weakness', '')}"
        vuln_type = self._determine_vuln_type(report_data.get('weakness', ''), combined_text)
        report_data['vulnerability_type'] = vuln_type
        
        # Fill in defaults
        for key in ['severity', 'weakness', 'reporter', 'bounty', 'disclosed_at', 'program', 'description', 'impact', 'timeline']:
            if key not in report_data or report_data[key] is None:
                report_data[key] = None if key != 'timeline' else None
        
        return HackerOneReport(**report_data)
    
    def _parse_full_page(self, soup: BeautifulSoup, report_data: dict) -> dict:
        """
        Parse additional data from full page content
        
        Args:
            soup: BeautifulSoup object
            report_data: Existing report data dict
            
        Returns:
            Updated report data dict
        """
        updates = {}
        
        # Extract severity from full page
        severity_elem = soup.find('span', string=re.compile(r'Severity', re.I))
        if severity_elem:
            severity_value = severity_elem.find_next('span')
            if severity_value:
                updates['severity'] = severity_value.get_text(strip=True)
        
        # Extract weakness
        weakness_elem = soup.find('span', string=re.compile(r'Weakness', re.I))
        if weakness_elem:
            weakness_value = weakness_elem.find_next('a') or weakness_elem.find_next('span')
            if weakness_value:
                updates['weakness'] = weakness_value.get_text(strip=True)
        
        # Extract reporter
        reporter_elem = soup.find('a', href=re.compile(r'^/[^/]+$'))
        if reporter_elem and 'reports' not in reporter_elem.get('href', ''):
            updates['reporter'] = reporter_elem.get_text(strip=True)
        
        # Extract bounty
        bounty_elem = soup.find('span', string=re.compile(r'Bounty', re.I))
        if bounty_elem:
            bounty_value = bounty_elem.find_next('span')
            if bounty_value:
                updates['bounty'] = bounty_value.get_text(strip=True)
        
        # Extract disclosed date
        disclosed_elem = soup.find('time')
        if disclosed_elem:
            updates['disclosed_at'] = disclosed_elem.get('datetime') or disclosed_elem.get_text(strip=True)
        
        # Extract full description if available
        description_elem = soup.find('div', class_='formatted-text')
        if description_elem:
            updates['description'] = description_elem.get_text(separator='\n', strip=True)[:2000]
        
        # Extract impact
        impact_heading = soup.find(['h2', 'h3'], string=re.compile(r'Impact', re.I))
        if impact_heading:
            impact_content = impact_heading.find_next(['p', 'div'])
            if impact_content:
                updates['impact'] = impact_content.get_text(strip=True)[:1000]
        
        # Extract timeline
        timeline = []
        timeline_items = soup.find_all('div', class_=re.compile(r'timeline|activity'))
        for item in timeline_items[:10]:
            text = item.get_text(strip=True)
            if text:
                timeline.append(text[:200])
        if timeline:
            updates['timeline'] = timeline
        
        return updates


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced HackerOne report scraper')
    parser.add_argument('--url', type=str,
                       default='https://github.com/reddelexc/hackerone-reports/blob/master/tops_by_bug_type/TOPSUBDOMAINTAKEOVER.md',
                       help='GitHub URL containing HackerOne report links')
    parser.add_argument('--max-reports', type=int, default=None,
                       help='Maximum number of reports to scrape')
    parser.add_argument('--delay', type=float, default=2.0,
                       help='Delay between requests in seconds')
    parser.add_argument('--output-dir', type=str, default='/mnt/user-data/outputs',
                       help='Output directory for datasets')
    
    args = parser.parse_args()
    
    # Use enhanced scraper
    scraper = EnhancedHackerOneScraper(delay=args.delay)
    
    # Extract report links
    logger.info(f"Extracting report links from: {args.url}")
    report_urls = scraper.extract_report_links_from_github(args.url)
    
    if not report_urls:
        logger.error("No report URLs found!")
        sys.exit(1)
    
    # Scrape reports
    reports = scraper.scrape_reports(report_urls, max_reports=args.max_reports)
    
    if not reports:
        logger.error("No reports successfully scraped!")
        sys.exit(1)
    
    # Generate datasets
    dataset_gen = DatasetGenerator()
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save in multiple formats
    dataset_gen.save_json(reports, f'{args.output_dir}/hackerone_reports_{timestamp}.json')
    dataset_gen.save_csv(reports, f'{args.output_dir}/hackerone_reports_{timestamp}.csv')
    dataset_gen.save_llm_training_format(reports, f'{args.output_dir}/hackerone_training_{timestamp}.jsonl')
    
    # Generate and save summary
    import json
    summary = dataset_gen.generate_summary(reports)
    with open(f'{args.output_dir}/scrape_summary_{timestamp}.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info("Scraping completed successfully!")
    logger.info(f"Summary: {summary}")
