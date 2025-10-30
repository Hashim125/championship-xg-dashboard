#!/bin/bash

# Championship xG Analysis Dashboard Launcher
# This script starts the Streamlit dashboard

echo "Starting Championship xG Analysis Dashboard..."
echo "Loading data from Snowflake..."
echo ""

streamlit run app.py

echo ""
echo "Dashboard stopped."
