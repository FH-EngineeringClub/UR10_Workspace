@echo off
setlocal enabledelayedexpansion

:: Enable script debugging
echo Script started.

:: Variables for install flags
set install_kinect_sdk=no

:: Install Chocolatey if not installed
choco -v >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Chocolatey...
    @powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
    echo Please close and reopen the Command Prompt, then run this script again to continue with the installation.
    pause
    exit /b
)

:: Ask if user wants to install Azure Kinect Sensor SDK
set /p kinect_choice="Do you want to install Azure Kinect Sensor SDK? (y/n): "
if /i "%kinect_choice%"=="y" (
    set install_kinect_sdk=yes
)

:: Check for Python 3.10 or higher
for /f "tokens=*" %%i in ('python --version 2^>nul') do set python_version=%%i
echo Detected Python version: !python_version!

echo !python_version! | findstr "3.10" >nul
if !errorlevel! neq 0 (
    echo Python 3.10 or higher not found. It will be installed.
    set install_python=yes
) else (
    echo Python 3.10 or higher is already installed.
)

:: Display summary
echo =======================================================
echo Installation Summary:
if defined install_python echo - Install Python 3.10
echo - Git
echo - Visual Studio Build Tools
echo - Visual Studio Code
echo - Stockfish
if !install_kinect_sdk!==yes echo - Azure Kinect Sensor SDK
echo =======================================================

:: Ask user if they want to proceed
set /p choice="Do you want to proceed with these changes? (y/n): "
if /i "!choice!" neq "y" (
    echo Installation aborted by user.
    pause
    exit /b
)

:: Install required packages
if defined install_python (
    echo Installing Python 3.10...
    choco install python --version=3.10.11 -y
)

echo Installing other required packages...
choco install git vscode visualstudio2019buildtools stockfish -y

:: Upgrade pip if Python was installed or upgraded
if defined install_python (
    echo Upgrading pip...
    python -m pip install --upgrade pip
)

:: Install Azure Kinect Sensor SDK if needed
if %install_kinect_sdk%==yes (
    echo Installing Azure Kinect Sensor SDK...
    
    :: Ensure C:\Temp exists
    if not exist "C:\Temp" mkdir "C:\Temp"

    :: Download the file using curl in a batch script
    curl -L -o "C:\Temp\AzureKinectSDK.exe" "https://download.microsoft.com/download/d/c/1/dc1f8a76-1ef2-4a1a-ac89-a7e22b3da491/Azure%%20Kinect%%20SDK%%201.4.2.exe"

    :: Run the installer
    start "" "C:\Temp\AzureKinectSDK.exe"


)


:: Installation complete
echo Installation complete.
pause
