"""
Main entry point for the timetable generator.
This file imports and runs the GUI application from the modular structure.
"""
try:
    from .gui import run_gui
except ImportError:
    from gui import run_gui

if __name__ == "__main__":
    run_gui()