#!/bin/bash

venvName="env"

# Create virtual environment
echo -e "\n* Creating virtual environment '$venvName'..."
python3 -m venv "$venvName"

# Activate the virtual environment
echo -e "\n* Activating virtual environment..."
source "$venvName/bin/activate"

# Install dependencies
echo -e "\n* Installing project dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Deactivate virtual environment
echo -e "\n Deactivating virtual environment..."
deactivate

echo -e "\n* Process completed.\n"
