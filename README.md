# HackerOne Report Scraper

A comprehensive web scraping tool designed to extract vulnerability reports from HackerOne for ethical hacking research and LLM training datasets.

## Features

- ✅ Scrapes HackerOne vulnerability reports from GitHub markdown files
- ✅ Extracts detailed report information (severity, weakness, bounty, timeline, etc.)
- ✅ Handles rate limiting and retry logic
- ✅ Exports data in multiple formats (JSON, CSV, JSONL)
- ✅ Generates LLM-ready training data with prompt/completion pairs
- ✅ Includes dataset analysis and visualization tools
- ✅ Comprehensive logging and error handling
- ✅ Configurable scraping parameters

## Ethical Use Notice

⚠️ **IMPORTANT**: This tool is designed for:
- Security research and education
- Training AI models on vulnerability patterns
- Learning about common security weaknesses
- Analyzing public disclosure trends

**DO NOT USE** for:
- Attacking systems without authorization
- Exploiting vulnerabilities
- Any illegal activities

All scraped data comes from **publicly disclosed reports** on HackerOne.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Dependencies

- `beautifulsoup4` - HTML parsing
- `requests` - HTTP requests
- `lxml` - XML/HTML parsing backend

## Usage

### Basic Usage

Scrape all reports from the default GitHub URL:

```bash
python hackerone_scraper.py
```

### Advanced Usage

#### Scrape from custom URL

```bash
python hackerone_scraper.py --url "https://github.com/reddelexc/hackerone-reports/blob/master/tops_by_bug_type/TOPXSS.md"
```

#### Limit number of reports

```bash
python hackerone_scraper.py --max-reports 50
```

#### Adjust request delay (be respectful!)

```bash
python hackerone_scraper.py --delay 3.0
```

#### Custom output directory

```bash
python hackerone_scraper.py --output-dir ./my_data
```

#### Combined example

```bash
python hackerone_scraper.py \
  --url "https://github.com/reddelexc/hackerone-reports/blob/master/tops_by_bug_type/TOPSSRF.md" \
  --max-reports 100 \
  --delay 2.5 \
  --output-dir ./ssrf_dataset
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--url` | GitHub URL containing HackerOne report links | TOPSUBDOMAINTAKEOVER.md |
| `--max-reports` | Maximum number of reports to scrape | None (all) |
| `--delay` | Delay between requests in seconds | 2.0 |
| `--output-dir` | Output directory for datasets | /mnt/user-data/outputs |

## Output Files

The scraper generates four files per run:

### 1. JSON Dataset (`hackerone_reports_TIMESTAMP.json`)
Complete structured data with all fields:

```json
[
  {
    "report_id": "123456",
    "title": "Subdomain Takeover on example.com",
    "url": "https://hackerone.com/reports/123456",
    "severity": "High",
    "weakness": "Subdomain Takeover",
    "reporter": "security_researcher",
    "bounty": "$500",
    "disclosed_at": "2024-01-15",
    "program": "Example Program",
    "description": "...",
    "impact": "...",
    "timeline": ["..."],
    "vulnerability_type": "subdomain_takeover",
    "scraped_at": "2024-01-20T10:30:00"
  }
]
```

### 2. CSV Dataset (`hackerone_reports_TIMESTAMP.csv`)
Tabular format suitable for spreadsheet analysis

### 3. LLM Training Format (`hackerone_training_TIMESTAMP.jsonl`)
JSONL format with prompt/completion pairs for fine-tuning:

```json
{"prompt": "Analyze this security vulnerability report:\n\nTitle: ...", "completion": "Vulnerability Analysis:\n\nReport ID: ...", "metadata": {...}}
```

### 4. Scrape Summary (`scrape_summary_TIMESTAMP.json`)
Statistics and overview:

```json
{
  "total_reports": 100,
  "vulnerability_types": {
    "subdomain_takeover": 45,
    "xss": 30,
    "ssrf": 25
  },
  "severity_distribution": {
    "Critical": 10,
    "High": 40,
    "Medium": 35,
    "Low": 15
  },
  "programs": {...},
  "reporters": {...},
  "total_bounty": 50000,
  "scrape_date": "2024-01-20T10:30:00"
}
```

## Dataset Analyzer

Analyze scraped datasets to get insights:

### Basic Analysis

```bash
python dataset_analyzer.py hackerone_reports_20240120_103000.json
```

### Save Report to File

```bash
python dataset_analyzer.py hackerone_reports_20240120_103000.json \
  --output analysis_report.txt
```

### Generate Visualizations

```bash
python dataset_analyzer.py hackerone_reports_20240120_103000.json \
  --visualize
```

This creates:
- `analysis_report_vulntypes.png` - Pie chart of vulnerability types
- `analysis_report_severity.png` - Bar chart of severity distribution

## Data Structure

Each scraped report contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `report_id` | str | Unique HackerOne report ID |
| `title` | str | Report title |
| `url` | str | Full URL to the report |
| `severity` | str | Severity level (Critical, High, Medium, Low) |
| `weakness` | str | CWE or vulnerability classification |
| `reporter` | str | Username of the security researcher |
| `bounty` | str | Bounty amount awarded |
| `disclosed_at` | str | Date of public disclosure |
| `program` | str | Target program/company name |
| `description` | str | Vulnerability description (truncated) |
| `impact` | str | Impact statement (truncated) |
| `timeline` | list | Timeline events from the report |
| `vulnerability_type` | str | Categorized vulnerability type |
| `raw_html` | str | First 5000 chars of HTML for reference |
| `scraped_at` | str | ISO timestamp of scraping |

## Vulnerability Type Categories

The scraper automatically categorizes reports into these types:

- `xss` - Cross-Site Scripting
- `sqli` - SQL Injection
- `rce` - Remote Code Execution
- `ssrf` - Server-Side Request Forgery
- `csrf` - Cross-Site Request Forgery
- `idor` - Insecure Direct Object Reference
- `auth_bypass` - Authentication/Authorization Bypass
- `subdomain_takeover` - Subdomain Takeover
- `file_upload` - Arbitrary File Upload
- `path_traversal` - Path/Directory Traversal
- `xxe` - XML External Entity
- `deserialization` - Insecure Deserialization
- `information_disclosure` - Information Disclosure
- `open_redirect` - Open Redirect
- `other` - Other/Unclassified

## Using the Dataset for LLM Training

### Format

The JSONL file contains training examples with:

**Prompt**: Context about the vulnerability
```
Analyze this security vulnerability report:

Title: Subdomain Takeover on api.example.com
Type: subdomain_takeover
Severity: High

Description:
The subdomain api.example.com is pointing to...
```

**Completion**: Structured analysis
```
Vulnerability Analysis:

Report ID: 123456
Classification: subdomain_takeover
Severity Level: High
Weakness: Subdomain Takeover
...
```

### Training Tips

1. **Preprocessing**: Filter by severity or vulnerability type
2. **Augmentation**: Create variations of prompts
3. **Validation Split**: Hold out 10-20% for testing
4. **Fine-tuning**: Use with GPT-3.5/4, Claude, or other LLMs
5. **Evaluation**: Test on unseen reports

### Example Fine-Tuning Command (OpenAI)

```bash
openai api fine_tunes.create \
  -t hackerone_training_20240120_103000.jsonl \
  -m gpt-3.5-turbo \
  --suffix "hackerone-analyzer"
```

## Rate Limiting & Best Practices

### Respectful Scraping

- **Default delay**: 2 seconds between requests
- **Exponential backoff**: Automatic retry with increasing delays
- **Max retries**: 3 attempts per request
- **User-Agent**: Identifies as a legitimate browser

### Recommendations

1. **Start small**: Test with `--max-reports 10` first
2. **Increase delay**: Use `--delay 3.0` or higher for large scrapes
3. **Scrape during off-peak hours**: Reduce server load
4. **Monitor logs**: Check `scraper.log` for errors
5. **Cache data**: Don't re-scrape the same reports

### Avoiding Blocks

```bash
# Conservative scraping
python hackerone_scraper.py --delay 5.0 --max-reports 50

# Very conservative (for large batches)
python hackerone_scraper.py --delay 10.0
```

## Error Handling

The scraper includes comprehensive error handling:

- **Network errors**: Automatic retry with backoff
- **Parsing errors**: Logged and skipped, scraping continues
- **Rate limiting**: Respects delays between requests
- **Invalid URLs**: Validated and logged
- **Missing data**: Gracefully handled with None values

Check `scraper.log` for detailed error information.

## Logging

All activities are logged to both console and `scraper.log`:

```
2024-01-20 10:30:00 - INFO - Extracting report links from: https://...
2024-01-20 10:30:02 - INFO - Found 150 unique HackerOne report links
2024-01-20 10:30:02 - INFO - Starting to scrape 150 reports
2024-01-20 10:30:04 - INFO - Fetching: https://hackerone.com/reports/123456
2024-01-20 10:30:06 - INFO - Successfully scraped: Subdomain Takeover on api.example.com
```

## Scraping Multiple Bug Types

Script to scrape different vulnerability categories:

```bash
#!/bin/bash

TYPES=("TOPXSS" "TOPSSRF" "TOPSQLI" "TOPRCE" "TOPSUBDOMAINTAKEOVER")

for TYPE in "${TYPES[@]}"; do
  echo "Scraping $TYPE..."
  python hackerone_scraper.py \
    --url "https://github.com/reddelexc/hackerone-reports/blob/master/tops_by_bug_type/${TYPE}.md" \
    --output-dir "./datasets/${TYPE}" \
    --delay 3.0
  
  echo "Sleeping 60 seconds before next category..."
  sleep 60
done

echo "All categories scraped!"
```

## Troubleshooting

### Problem: No reports found

**Solution**: Check if the GitHub URL is correct and contains HackerOne links

```bash
curl https://raw.githubusercontent.com/reddelexc/hackerone-reports/master/tops_by_bug_type/TOPSUBDOMAINTAKEOVER.md | grep "hackerone.com/reports"
```

### Problem: Scraping is too slow

**Solution**: Reduce delay (but be respectful!)

```bash
python hackerone_scraper.py --delay 1.5
```

### Problem: Getting blocked/rate limited

**Solution**: Increase delay and reduce batch size

```bash
python hackerone_scraper.py --delay 5.0 --max-reports 25
```

### Problem: Missing data in reports

**Solution**: HackerOne's HTML structure may have changed. Check logs and update parser selectors.

## Project Structure

```
.
├── hackerone_scraper.py      # Main scraper script
├── dataset_analyzer.py        # Analysis tool
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── scraper.log               # Log file (auto-generated)
└── /mnt/user-data/outputs/   # Output datasets (auto-generated)
    ├── hackerone_reports_TIMESTAMP.json
    ├── hackerone_reports_TIMESTAMP.csv
    ├── hackerone_training_TIMESTAMP.jsonl
    └── scrape_summary_TIMESTAMP.json
```

## Future Enhancements

Possible improvements:

- [ ] Database storage (SQLite/PostgreSQL)
- [ ] Incremental updates (track already scraped reports)
- [ ] Multi-threaded scraping (with care for rate limits)
- [ ] Web dashboard for browsing reports
- [ ] API endpoint for querying scraped data
- [ ] Automated categorization using ML
- [ ] Support for other bug bounty platforms
- [ ] Integration with vulnerability databases (NVD, CVE)

## Contributing

Suggestions for improvement:

1. More robust HTML parsing for different report formats
2. Additional export formats (XML, Parquet, etc.)
3. Better error recovery
4. Performance optimizations
5. Additional analysis features

## License

This tool is for educational and research purposes only. Respect HackerOne's terms of service and rate limits. All scraped data is publicly available information.

## Disclaimer

This tool accesses publicly disclosed vulnerability reports. The authors are not responsible for misuse of this tool or the data it collects. Always follow ethical hacking principles and responsible disclosure practices.

## Resources

- [HackerOne](https://hackerone.com/)
- [HackerOne Reports GitHub](https://github.com/reddelexc/hackerone-reports)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Database](https://cwe.mitre.org/)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review `scraper.log` for errors
3. Verify your Python version (3.8+)
4. Ensure all dependencies are installed

---

**Happy (ethical) hacking! 🔒**
