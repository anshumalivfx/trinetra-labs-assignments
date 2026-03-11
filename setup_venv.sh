#!/bin/bash
# Setup script to create Python 3.12 virtual environment

cd /Users/anshumalikarna/Desktop/Assignment

# Remove old venv
rm -rf .venv

# Create new venv with Python 3.12
/opt/anaconda3/bin/python3.12 -m venv .venv

# Activate and verify
source .venv/bin/activate
python --version
pip --version

echo "Virtual environment created successfully with Python 3.12"
