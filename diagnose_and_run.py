#!/usr/bin/env python3
"""
Diagnostic launcher for the Timetable Generator
This script checks the environment and dependencies before running the application
"""
import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("=" * 60)
print("TIMETABLE GENERATOR - DIAGNOSTIC CHECK")
print("=" * 60)
print()

# Check Python version
print(f"Python Version: {sys.version}")
print(f"Python Executable: {sys.executable}")
print()

# Check dependencies
print("Checking dependencies...")
dependencies_ok = True

# Check pandas
try:
    import pandas as pd
    print(f"  [OK] pandas {pd.__version__}")
except ImportError as e:
    print(f"  [MISSING] pandas")
    print(f"     Error: {e}")
    dependencies_ok = False

# Check openpyxl
try:
    import openpyxl
    print(f"  [OK] openpyxl {openpyxl.__version__}")
except ImportError as e:
    print(f"  [MISSING] openpyxl")
    print(f"     Error: {e}")
    dependencies_ok = False

# Check xlrd
try:
    import xlrd
    print(f"  [OK] xlrd {xlrd.__VERSION__}")
except ImportError as e:
    print(f"  [MISSING] xlrd")
    print(f"     Error: {e}")
    dependencies_ok = False

# Check tkinter
try:
    import tkinter
    print(f"  [OK] tkinter")
except ImportError as e:
    print(f"  [MISSING] tkinter")
    print(f"     Error: {e}")
    dependencies_ok = False

print()

if not dependencies_ok:
    print("=" * 60)
    print("MISSING DEPENDENCIES DETECTED!")
    print("=" * 60)
    print()
    print("Installing missing packages...")
    print()
    
    import subprocess
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "pandas", "openpyxl", "xlrd"
        ])
        print()
        print("[SUCCESS] Dependencies installed successfully!")
        print("  Please restart this script.")
        print()
    except Exception as e:
        print()
        print(f"[FAILED] Failed to install dependencies: {e}")
        print()
        print("Please install manually:")
        print(f"  {sys.executable} -m pip install pandas openpyxl xlrd")
        print()
    
    input("Press Enter to exit...")
    sys.exit(1)

print("=" * 60)
print("ALL DEPENDENCIES OK - Starting Application...")
print("=" * 60)
print()

# Add Src directory to path
src_dir = Path(__file__).parent / "Src"
sys.path.insert(0, str(src_dir))
os.chdir(str(src_dir))

# Import and run the GUI
try:
    from gui import run_gui
    run_gui()
except Exception as e:
    print()
    print("=" * 60)
    print("ERROR STARTING APPLICATION")
    print("=" * 60)
    print(f"Error: {e}")
    print()
    import traceback
    traceback.print_exc()
    print()
    input("Press Enter to exit...")
    sys.exit(1)

