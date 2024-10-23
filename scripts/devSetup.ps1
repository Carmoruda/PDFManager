$venvName = "venv"

# Create virtual environment
Write-Host "`n* Creating virtual environment '$venvName'..."
python -m venv $venvName

# Activate the virtual environment
Write-Host "`n* Activating virtual environment..."
& ".\$venvName\Scripts\Activate.ps1"

# Install dependencies
Write-Host "`n* Installing project dependencies..."
python.exe -m pip install --upgrade pip
pip install -r requirements.txt

# Deactivate virtual environment
Write-Host "`n* Deactivating virtual environment..."
deactivate

Write-Host "`n* Process completed.`n"
