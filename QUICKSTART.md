# HackerOne Report Scraper - Quick Start Guide

## 🚀 Quick Start (60 seconds)

### 1. Install Dependencies
```bash
pip install beautifulsoup4 requests lxml
```

### 2. Run Your First Scrape (10 reports for testing)
```bash
python enhanced_scraper.py --max-reports 10
```

### 3. Check Your Data
```bash
ls -lh /mnt/user-data/outputs/
```

You'll get 4 files:
- `hackerone_reports_*.json` - Full dataset
- `hackerone_reports_*.csv` - Spreadsheet format
- `hackerone_training_*.jsonl` - LLM training format
- `scrape_summary_*.json` - Statistics

## 📊 Common Use Cases

### Scrape 100 Reports for Analysis
```bash
python enhanced_scraper.py --max-reports 100 --delay 2.0
```

### Scrape All XSS Vulnerabilities
```bash
python enhanced_scraper.py \
  --url "https://github.com/reddelexc/hackerone-reports/blob/master/tops_by_bug_type/TOPXSS.md" \
  --delay 3.0
```

### Scrape Multiple Vulnerability Types (Batch Mode)
```bash
./batch_scrape.sh
```
This will scrape: XSS, SSRF, SQLi, RCE, Subdomain Takeover, IDOR, and Open Redirect

### Analyze Your Dataset
```bash
python dataset_analyzer.py /mnt/user-data/outputs/hackerone_reports_*.json
```

## 🎯 What You Get

### JSON Dataset Example
```json
{
  "report_id": "123456",
  "title": "Subdomain Takeover on api.example.com",
  "url": "https://hackerone.com/reports/123456",
  "program": "Example Corp",
  "severity": "High",
  "description": "Found dangling CNAME record...",
  "vulnerability_type": "subdomain_takeover"
}
```

### LLM Training Format Example
```json
{
  "prompt": "Analyze this security vulnerability report:\n\nTitle: Subdomain Takeover...",
  "completion": "Vulnerability Analysis:\n\nClassification: subdomain_takeover...",
  "metadata": {"report_id": "123456", "vulnerability_type": "subdomain_takeover"}
}
```

## 📈 Dataset Statistics

After scraping, you get:
- **Vulnerability types** (XSS, SQLi, RCE, etc.)
- **Severity distribution** (Critical, High, Medium, Low)
- **Top programs** (which companies have most reports)
- **Top reporters** (most active security researchers)
- **Bounty statistics** (total paid, average, min, max)

## ⚡ Performance Tips

### Fast Scraping (Small Dataset)
```bash
python enhanced_scraper.py --max-reports 20 --delay 1.5
```

### Respectful Scraping (Large Dataset)
```bash
python enhanced_scraper.py --delay 5.0
```

### Scrape Overnight (All Reports)
```bash
nohup python enhanced_scraper.py --delay 3.0 > scraper.log 2>&1 &
```

## 🔧 Troubleshooting

### Problem: "No reports scraped"
**Solution**: Check if GitHub URL is correct
```bash
curl https://raw.githubusercontent.com/reddelexc/hackerone-reports/master/tops_by_bug_type/TOPSUBDOMAINTAKEOVER.md | grep hackerone
```

### Problem: "Rate limited"
**Solution**: Increase delay
```bash
python enhanced_scraper.py --delay 10.0
```

### Problem: "Missing data fields"
**Solution**: This is normal! The enhanced scraper extracts what's available from meta tags when full page access is restricted.

## 📁 File Structure

```
hackerone_scraper/
├── enhanced_scraper.py          # Main scraper (recommended)
├── hackerone_scraper.py         # Base scraper
├── dataset_analyzer.py          # Analysis tool
├── batch_scrape.sh             # Batch processing script
├── requirements.txt            # Dependencies
├── README.md                   # Full documentation
└── outputs/                    # Generated datasets
    ├── hackerone_reports_*.json
    ├── hackerone_reports_*.csv
    ├── hackerone_training_*.jsonl
    └── scrape_summary_*.json
```

## 🎓 Using Data for LLM Training

### 1. Filter by Vulnerability Type
```python
import json

with open('hackerone_reports_*.json') as f:
    data = json.load(f)

xss_reports = [r for r in data if r['vulnerability_type'] == 'xss']
print(f"Found {len(xss_reports)} XSS reports")
```

### 2. Create Training/Validation Split
```python
import random

random.shuffle(data)
split = int(len(data) * 0.8)
train = data[:split]
val = data[split:]
```

### 3. Load JSONL Training Data
```python
import json

examples = []
with open('hackerone_training_*.jsonl') as f:
    for line in f:
        examples.append(json.loads(line))

print(f"Loaded {len(examples)} training examples")
```

## 🌟 Best Practices

1. **Start Small**: Test with `--max-reports 10` first
2. **Be Respectful**: Use `--delay 3.0` or higher
3. **Monitor Logs**: Check `scraper.log` for errors
4. **Save Results**: Datasets are timestamped and won't overwrite
5. **Analyze First**: Use `dataset_analyzer.py` before training

## 📚 Next Steps

1. **Scrape your first dataset**
   ```bash
   python enhanced_scraper.py --max-reports 50
   ```

2. **Analyze the results**
   ```bash
   python dataset_analyzer.py /mnt/user-data/outputs/hackerone_reports_*.json
   ```

3. **Prepare for LLM training**
   - Use the JSONL file for fine-tuning
   - Filter by vulnerability type if needed
   - Create train/validation splits

4. **Explore more vulnerability types**
   ```bash
   ./batch_scrape.sh
   ```

## 🔗 Useful Links

- [HackerOne](https://hackerone.com/)
- [HackerOne Reports GitHub](https://github.com/reddelexc/hackerone-reports)
- [CWE Database](https://cwe.mitre.org/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## ⚖️ Legal & Ethical Use

✅ **Allowed**:
- Security research and education
- Training AI models on public data
- Analyzing vulnerability trends
- Learning about common weaknesses

❌ **Not Allowed**:
- Attacking systems without authorization
- Exploiting vulnerabilities
- Any illegal activities

All data scraped is **publicly disclosed** on HackerOne.

---

**Happy (ethical) hacking!** 🔒

For full documentation, see README.md
