#!/bin/bash
# Auto-push to GitHub script
# Usage: ./push_to_github.sh YOUR_GITHUB_USERNAME YOUR_REPO_NAME

set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <github_username> <repo_name>"
    echo "Example: $0 johndoe hackerone-scraper"
    exit 1
fi

GITHUB_USER=$1
REPO_NAME=$2
CURRENT_DIR=$(pwd)

echo "========================================"
echo "Pushing to GitHub"
echo "========================================"
echo "GitHub User: $GITHUB_USER"
echo "Repository: $REPO_NAME"
echo "Directory: $CURRENT_DIR"
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    git branch -M main
fi

# Configure git (you can change these)
read -p "Enter your name for git commits: " GIT_NAME
read -p "Enter your email for git commits: " GIT_EMAIL

git config user.name "$GIT_NAME"
git config user.email "$GIT_EMAIL"

# Add files
echo "Adding files..."
git add .

# Commit
echo "Creating commit..."
git commit -m "Initial commit: HackerOne vulnerability report scraper

- Enhanced scraper with meta tag extraction
- Dataset analyzer with statistics
- Batch processing for multiple vulnerability types
- LLM training format (JSONL) output
- Comprehensive documentation" || echo "Nothing to commit or already committed"

# Check if remote exists
if git remote | grep -q origin; then
    echo "Remote 'origin' already exists, removing..."
    git remote remove origin
fi

# Add remote
echo "Adding GitHub remote..."
REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"
git remote add origin "$REPO_URL"

# Push
echo ""
echo "Ready to push to: $REPO_URL"
echo ""
echo "You will be prompted for your GitHub credentials."
echo "Note: Use a Personal Access Token as password (not your GitHub password)"
echo "Get token from: https://github.com/settings/tokens"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

git push -u origin main

echo ""
echo "========================================"
echo "Successfully pushed to GitHub!"
echo "========================================"
echo "View at: https://github.com/$GITHUB_USER/$REPO_NAME"
echo ""
