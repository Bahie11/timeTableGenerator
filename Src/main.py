"""
Main entry point for the timetable generator.
Launches the GUI application.
"""
import sys
import logging
from pathlib import Path

# Ensure this file's directory is on sys.path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from gui import run_gui

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    run_gui()