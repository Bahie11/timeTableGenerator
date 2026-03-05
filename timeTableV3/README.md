# Timetable CSP generator

This project provides a simple constraint-satisfaction based timetable generator.

Files:
- `main.py` - CLI to run the solver.
- `parser.py` - reads Excel files for instructors, rooms, courses, and timeslots.
- `csp.py` - basic backtracking CSP solver with MRV and forward checking.
- `sample_inputs/generate_samples.py` - creates sample Excel input files.

Requirements:
- Python 3.8+
- Install with `pip install -r requirements.txt`.

Quickstart:
1. Generate sample inputs:
   python sample_inputs/generate_samples.py
2. Run solver (example paths):
   python main.py --instructors sample_inputs/instructors.xlsx --rooms sample_inputs/rooms.xlsx --courses sample_inputs/courses.xlsx --timeslots sample_inputs/timeslots.xlsx --out result.xlsx
