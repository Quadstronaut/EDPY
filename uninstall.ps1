<#
.SYNOPSIS
    Uninstalls the EDMCAutoHonk plugin for Elite Dangerous Market Connector.

.DESCRIPTION
    This script is designed to safely remove the AutoHonk plugin by deleting
    the entire plugin folder from your EDMarketConnector directory.

.NOTES
    Why we do this:
    Automating the uninstallation process ensures that all plugin files are
    removed cleanly and completely. This prevents orphaned files and potential
    conflicts with future plugin versions or other plugins.

    How it works:
    1. It first determines the correct destination folder using the built-in
       Windows environment variable '$env:LOCALAPPDATA'.
    2. It then checks if the 'AutoHonk' folder exists.
    3. If the folder is found, it uses the '-Recurse' and '-Force' parameters
       to delete the entire directory and all its contents, ensuring a
       thorough and complete removal.
#>
$Destination = "$env:LOCALAPPDATA\EDMarketConnector\plugins\AutoHonk\"
Write-Host "Uninstalling AutoHonk plugin..."

if (Test-Path $Destination) {
    try {
        Remove-Item -Path $Destination -Recurse -Verbose -Force -ForegroundColor Yellow
        Write-Host "AutoHonk plugin uninstalled successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "An error occurred while uninstalling: $_" -ForegroundColor Red
    }
}
else {
    Write-Host "The AutoHonk plugin folder was not found. Nothing to uninstall." -ForegroundColor Yellow
}