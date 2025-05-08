#!/bin/bash

venvName="env"
scriptName="src/app.py"

# Activate the virtual environment
echo -e "\n* Activating virtual environment..."
source "$venvName/bin/activate"

# Execute the script
echo -e "\n* Running Python script $scriptName.."
python3 $scriptName

# Deactivate virtual environment
echo -e "\n Deactivating virtual environment..."
deactivate

echo -e "\n* Process completed.\n"
