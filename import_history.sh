#!/bin/bash

# Script to import historical NFL Fantasy data
# This will scrape data from 2017-2024 and import it into the dashboard

echo "🏈 NFL Fantasy Historical Data Importer"
echo "========================================"
echo ""
echo "This will scrape historical matchup data from 2017-2024"
echo "This may take 10-20 minutes depending on network speed"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

cd "$(dirname "$0")"
cd backend

python3 import_historical.py

echo ""
echo "✅ Import complete!"
echo "You can now view head-to-head statistics in the dashboard"

