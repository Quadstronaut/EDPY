<#
.SYNOPSIS
    Installs the EDMCAutoHonk plugin for Elite Dangerous Market Connector.

.DESCRIPTION
    This script is designed to automate the installation of the AutoHonk plugin.
    It copies the required 'load.py' file to the correct plugins directory
    for EDMarketConnector.

.NOTES
    Why we do this:
    Manually copying files can be tedious and prone to error. This script
    ensures the plugin is always installed in the right place, making the
    process simple and reliable. It also handles the creation of the
    'AutoHonk' folder if it doesn't already exist.

    How it works:
    1. It first determines the correct destination folder using the built-in
       Windows environment variable '$env:LOCALAPPDATA'.
    2. It then checks if the destination folder exists. If not, it creates it
       for you.
    3. Finally, it copies the 'load.py' file from the current location to the
       destination folder, overwriting any existing file to ensure you're always
       running the latest version.
#>
$Destination = "$env:LOCALAPPDATA\EDMarketConnector\plugins\AutoHonk\"
$Path = ".\load.py" # Assumes load.py is in the same directory as the script

# Check if the source file exists
if (-not (Test-Path $Path)) {
    Write-Host "Error: The source file $Path was not found." -ForegroundColor Red
    return # Exit the script
}

# Check if the destination folder exists; if not, create it
if (-not (Test-Path $Destination)) {
    Write-Host "Creating plugin directory..."
    New-Item -Path $Destination -ItemType Directory | Out-Null
}

# Copy the file
try {
    Write-Host "Copying load.py to the plugin`'s directory..."
    Copy-Item -Path $Path -Destination $Destination -Force -Verbose -ForegroundColor Yellow
    Write-Host "AutoHonk plugin installed successfully!" -ForegroundColor Green
}
catch {
    Write-Host "An error occurred while copying the file: $_" -ForegroundColor Red
}