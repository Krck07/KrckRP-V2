#!/bin/bash

# KrckRP Project Scaffolding Script
# Run this script to set up the basic project structure

echo "Setting up KrckRP project structure..."

# Create main directories
mkdir -p app/models
mkdir -p app/engine  
mkdir -p app/llm
mkdir -p app/memory
mkdir -p tests

# Create base files
touch app/__init__.py
touch app/models/__init__.py
touch app/engine/__init__.py
touch app/llm/__init__.py
touch app/memory/__init__.py

echo "Project structure created successfully!"
echo ""
echo "Created directories:"
echo "- app/models/"
echo "- app/engine/" 
echo "- app/llm/"
echo "- app/memory/"
echo "- tests/"
echo ""
echo "Files created:"
echo "- app/__init__.py"
echo "- app/models/__init__.py"
echo "- app/engine/__init__.py"
echo "- app/llm/__init__.py"  
echo "- app/memory/__init__.py"

echo ""
echo "Foundation documents created:"
echo "- RULES.md"
echo "- API_CONTRACT.md"
echo "- KOBOLD_CHEAT_SHEET.md"