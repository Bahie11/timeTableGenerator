@echo off
REM Timetable Generator Launcher
REM This ensures the application runs with the correct Python environment

echo ========================================
echo Timetable Generator - Starting...
echo ========================================
echo.

REM Check Python version
python --version
echo.

REM Check dependencies
echo Checking dependencies...
python -c "import pandas; print('  [OK] Pandas', pandas.__version__)"
if errorlevel 1 (
    echo   [ERROR] Pandas not found!
    echo   Installing pandas...
    python -m pip install pandas openpyxl xlrd
)

python -c "import openpyxl; print('  [OK] Openpyxl', openpyxl.__version__)"
if errorlevel 1 (
    echo   [ERROR] Openpyxl not found!
    echo   Installing openpyxl...
    python -m pip install openpyxl
)

echo.
echo Starting Timetable Generator GUI...
echo.

REM Run the application
cd Src
python main.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo ========================================
    echo Error occurred! Check the message above.
    echo ========================================
    pause
)


