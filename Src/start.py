"""
Safe startup script for the timetable generator
Checks dependencies and provides helpful error messages
"""
import sys
import os

def check_and_install_dependencies():
    """Check if required packages are installed, offer to install if missing"""
    missing = []
    
    # Check pandas
    try:
        import pandas
    except ImportError:
        missing.append('pandas')
    
    # Check openpyxl
    try:
        import openpyxl
    except ImportError:
        missing.append('openpyxl')
    
    # Check xlrd
    try:
        import xlrd
    except ImportError:
        missing.append('xlrd')
    
    if missing:
        print("=" * 70)
        print("MISSING DEPENDENCIES DETECTED")
        print("=" * 70)
        print()
        print(f"Python: {sys.executable}")
        print(f"Version: {sys.version}")
        print()
        print("Missing packages:", ", ".join(missing))
        print()
        print("Installing missing packages...")
        print()
        
        import subprocess
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "--upgrade", "pandas", "openpyxl", "xlrd"
            ])
            print()
            print("=" * 70)
            print("INSTALLATION SUCCESSFUL!")
            print("=" * 70)
            print()
            print("Please restart the application.")
            print()
            input("Press Enter to exit...")
            sys.exit(0)
        except Exception as e:
            print()
            print("=" * 70)
            print("INSTALLATION FAILED")
            print("=" * 70)
            print()
            print(f"Error: {e}")
            print()
            print("Please install manually by running:")
            print(f"  {sys.executable} -m pip install pandas openpyxl xlrd")
            print()
            input("Press Enter to exit...")
            sys.exit(1)

if __name__ == "__main__":
    # Check dependencies first
    check_and_install_dependencies()
    
    # If we get here, all dependencies are available
    print("Starting Timetable Generator...")
    print()
    
    # Import and run the main application
    try:
        from gui import run_gui
        run_gui()
    except Exception as e:
        print()
        print("=" * 70)
        print("ERROR")
        print("=" * 70)
        print(f"Failed to start application: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        input("Press Enter to exit...")
        sys.exit(1)


