#!/bin/bash
echo "Installing required libraries..."
pip3 install -r requirements.txt
echo "Starting Prompt Engineering Studio..."
streamlit run app.py
