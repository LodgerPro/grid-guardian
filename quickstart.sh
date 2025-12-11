#!/bin/bash

echo "===================================================================="
echo "          GRID GUARDIAN - Quick Start Script"
echo "===================================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

echo "[1/5] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo "[2/5] Activating virtual environment..."
source venv/bin/activate

echo "[3/5] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "[4/5] Running complete pipeline..."
python run_pipeline.py
if [ $? -ne 0 ]; then
    echo "ERROR: Pipeline execution failed"
    exit 1
fi

echo "[5/5] Launching dashboard..."
echo ""
echo "===================================================================="
echo "Dashboard will open at http://localhost:8501"
echo "Press Ctrl+C to stop the dashboard"
echo "===================================================================="
echo ""
streamlit run app/Home.py
