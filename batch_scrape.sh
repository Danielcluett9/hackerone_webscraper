#!/bin/bash
# Batch HackerOne Scraper - Scrape multiple vulnerability categories
# Usage: ./batch_scrape.sh

echo "========================================"
echo "HackerOne Batch Scraper"
echo "========================================"
echo ""

# Configuration
DELAY=3.0  # Seconds between requests
MAX_REPORTS_PER_TYPE=50  # Limit per category (set to empty for all)
OUTPUT_DIR="/mnt/user-data/outputs"
PAUSE_BETWEEN_TYPES=60  # Seconds to pause between different vulnerability types

# Vulnerability type URLs
declare -A VULN_URLS=(
    ["XSS"]="https://github.com/reddelexc/hackerone-reports/blob/master/tops_by_bug_type/TOPXSS.md"
    ["SSRF"]="https://github.com/reddelexc/hackerone-reports/blob/master/tops_by_bug_type/TOPSSRF.md"
    ["SQLi"]="https://github.com/reddelexc/hackerone-reports/blob/master/tops_by_bug_type/TOPSQLI.md"
    ["RCE"]="https://github.com/reddelexc/hackerone-reports/blob/master/tops_by_bug_type/TOPRCE.md"
    ["SUBDOMAIN_TAKEOVER"]="https://github.com/reddelexc/hackerone-reports/blob/master/tops_by_bug_type/TOPSUBDOMAINTAKEOVER.md"
    ["IDOR"]="https://github.com/reddelexc/hackerone-reports/blob/master/tops_by_bug_type/TOPIDOR.md"
    ["OPEN_REDIRECT"]="https://github.com/reddelexc/hackerone-reports/blob/master/tops_by_bug_type/TOPOPENREDIRECT.md"
)

# Create output directories
mkdir -p "$OUTPUT_DIR/by_type"

# Counter for total reports
TOTAL_SCRAPED=0

# Scrape each vulnerability type
for TYPE in "${!VULN_URLS[@]}"; do
    echo "----------------------------------------"
    echo "Scraping: $TYPE"
    echo "----------------------------------------"
    
    TYPE_DIR="$OUTPUT_DIR/by_type/$TYPE"
    mkdir -p "$TYPE_DIR"
    
    # Build command
    CMD="python3 /home/claude/enhanced_scraper.py"
    CMD="$CMD --url \"${VULN_URLS[$TYPE]}\""
    CMD="$CMD --delay $DELAY"
    CMD="$CMD --output-dir \"$TYPE_DIR\""
    
    if [ -n "$MAX_REPORTS_PER_TYPE" ]; then
        CMD="$CMD --max-reports $MAX_REPORTS_PER_TYPE"
    fi
    
    # Execute scraper
    eval $CMD
    
    if [ $? -eq 0 ]; then
        echo "✓ Successfully scraped $TYPE"
        
        # Count scraped reports
        REPORT_COUNT=$(find "$TYPE_DIR" -name "hackerone_reports_*.json" -exec cat {} \; | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "0")
        TOTAL_SCRAPED=$((TOTAL_SCRAPED + REPORT_COUNT))
        
        echo "  Reports scraped: $REPORT_COUNT"
    else
        echo "✗ Failed to scrape $TYPE"
    fi
    
    echo ""
    echo "Pausing for $PAUSE_BETWEEN_TYPES seconds before next type..."
    sleep $PAUSE_BETWEEN_TYPES
done

echo "========================================"
echo "Batch Scraping Complete!"
echo "========================================"
echo "Total reports scraped: $TOTAL_SCRAPED"
echo "Output directory: $OUTPUT_DIR/by_type"
echo ""
echo "To analyze a dataset:"
echo "  python3 dataset_analyzer.py <json_file>"
echo ""
