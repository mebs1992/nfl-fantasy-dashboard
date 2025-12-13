#!/bin/bash

# Script to push code to GitHub
cd /Users/marcus/Downloads/nfl-fantasy-dashboard

# Set up remote
git remote set-url origin https://github.com/mebs1992/nfl-fantasy-dashboard.git

# Push with token embedded in URL (one-time use)
echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "If it asks for credentials:"
echo "  Username: mebs1992"
echo "  Password: [Use your GitHub Personal Access Token]"

