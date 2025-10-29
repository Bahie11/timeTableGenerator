# Timetable Generator (CSP)

A modular timetable generator using Constraint Satisfaction Problem (CSP) approach with a modern GUI interface.

## Project Structure

The project has been organized into a clean, modular folder structure:

```
timetable/
├── Src/                    # Source code package
│   ├── __init__.py        # Package initialization
│   ├── main.py            # Main entry point
│   ├── gui.py             # GUI application
│   ├── models.py          # Data models
│   ├── csp.py             # CSP solver
│   ├── data_loader.py     # Data loading utilities
│   ├── output_utils.py    # Output utilities
│   ├── htmlexport.py      # HTML export
│   └── test_imports.py    # Import testing
├── Data/                   # Data files
│   ├── Instructor.csv     # Instructor data
│   ├── Rooms.csv          # Room data  
│   ├── Courses.csv         # Course data
│   ├── TimeSlots.csv      # Time slot data
│   └── csitTmeTable.xlsx  # Excel data
├── README.md              # Documentation
└── [other files]         # Generated outputs
```

### Source Code (Src/)

- **`main.py`** - Main entry point that runs the GUI application
- **`gui.py`** - Complete GUI application with modern styling and animations
- **`models.py`** - Data models and type definitions
- **`csp.py`** - Constraint Satisfaction Problem solver
- **`data_loader.py`** - CSV and Excel data loading utilities
- **`output_utils.py`** - CSV and console output utilities
- **`htmlexport.py`** - HTML export functionality
- **`test_imports.py`** - Import testing script

### Data Files (Data/)

- **`Instructor.csv`** - Instructor data
- **`Rooms.csv`** - Room data  
- **`Courses.csv`** - Course data
- **`TimeSlots.csv`** - Time slot data
- **`csitTmeTable.xlsx`** - Excel data file

## Features

### 🎨 Modern GUI
- Beautiful color scheme with animations
- Responsive design with hover effects
- Loading animations and progress bars
- Modern button styles and transitions

### 📊 Data Management
- Add/Edit/Delete instructors, rooms, and courses
- Import from CSV or Excel files
- Export to CSV format
- Real-time data validation

### 🧠 Smart Scheduling
- Constraint Satisfaction Problem (CSP) algorithm
- Backtracking search with heuristics
- Conflict detection and resolution
- Optimal room and time allocation

### 📄 Multiple Export Formats
- **CSV Export** - Structured data for analysis
- **HTML Export** - Complete schedule with modern styling
- **Grid HTML** - Weekly grid format (Sunday-Thursday)
- **Instructor HTML** - Personal timetables
- **PDF Export** - Professional reports (optional)

### 🔧 Advanced Features
- Proper weekday and time sorting
- Room conflict detection
- Day distribution optimization
- Instructor availability handling
- Course qualification matching

## Usage

### Quick Start
```bash
# Navigate to the project directory
cd timetable

# Run the application
python Src/main.py
```

### Data Requirements
1. **Instructors**: ID, Name, Role, Availability, Qualified Courses
2. **Rooms**: ID, Type (Lecture/Lab), Capacity
3. **Courses**: ID, Name, Type, Credits
4. **Time Slots**: Day, Start Time, End Time

### Import Data
- Use the GUI to import CSV or Excel files
- Or manually add data through the interface
- Supports both CSV and Excel formats

### Generate Schedule
1. Load all required data (instructors, rooms, courses, timeslots)
2. Click "🚀 Generate Timetable"
3. View results in the table
4. Export in your preferred format

## Algorithm Details

### CSP Approach
The timetable generator uses a Constraint Satisfaction Problem approach:

1. **Variables**: Instructors (each needs one assignment)
2. **Domains**: All valid (timeslot, room, course) combinations
3. **Constraints**: 
   - No room-time conflicts
   - No same-course conflicts
   - Instructor availability respected
   - Course qualifications matched

### Search Strategy
- **Backtracking Search**: Systematic exploration of solution space
- **Minimum Remaining Values**: Selects variables with fewest options
- **Domain Ordering**: Prioritizes day diversity for better distribution
- **Consistency Checking**: Validates assignments against constraints

### Optimization Features
- **Day Distribution**: Spreads courses across all weekdays
- **Conflict Prevention**: Prevents double-booking of rooms
- **Availability Respect**: Honors instructor preferences
- **Course Matching**: Ensures qualified instructors for courses

## Export Options

### 1. CSV Export
- Structured data format
- Sorted by weekday and time
- Includes all schedule details
- Compatible with Excel and other tools

### 2. HTML Complete Schedule
- Modern web-based display
- Day-by-day organization
- Statistics and summaries
- Professional styling

### 3. HTML Grid Format
- Weekly grid layout
- Days as columns, times as rows
- Visual course placement
- Easy to read format

### 4. HTML Instructor Timetables
- Personal schedules for each instructor
- Individual HTML files
- Instructor details and statistics
- Clean, professional layout

## Technical Requirements

### Required Dependencies
- Python 3.7+
- tkinter (included with Python)
- csv (included with Python)

### Optional Dependencies
- **pandas + openpyxl**: For Excel import/export
- **reportlab**: For PDF generation

### Installation
```bash
# Basic requirements (usually already installed)
# No additional packages needed for basic functionality

# For Excel support
pip install pandas openpyxl

# For PDF generation
pip install reportlab
```

## File Organization

```
timetable/
├── Src/                    # Source code package
│   ├── __init__.py        # Package initialization
│   ├── main.py            # Entry point
│   ├── gui.py             # GUI application
│   ├── models.py          # Data models
│   ├── csp.py             # CSP solver
│   ├── data_loader.py     # Data loading
│   ├── output_utils.py    # Output utilities
│   ├── htmlexport.py      # HTML export
│   └── test_imports.py    # Import testing
├── Data/                   # Data files
│   ├── Instructor.csv     # Instructor data
│   ├── Rooms.csv          # Room data
│   ├── Courses.csv         # Course data
│   ├── TimeSlots.csv      # Time slot data
│   └── csitTmeTable.xlsx  # Excel data
├── README.md              # Documentation
└── [generated files]      # Output files
```

## Benefits of Modular Structure

### 🧩 Separation of Concerns
- **GUI**: User interface and interactions
- **CSP**: Algorithm logic and solving
- **Models**: Data structures and types
- **Data**: Loading and parsing utilities
- **Output**: Export and formatting

### 🔧 Maintainability
- Easy to modify individual components
- Clear responsibility boundaries
- Reduced code duplication
- Better error handling

### 🚀 Extensibility
- Add new export formats easily
- Implement different algorithms
- Enhance GUI features
- Add new data sources

### 🧪 Testability
- Test individual modules
- Mock dependencies easily
- Isolate functionality
- Better debugging

## Future Enhancements

- **Advanced Constraints**: More complex scheduling rules
- **Optimization**: Genetic algorithms for better solutions
- **Real-time Updates**: Live schedule modifications
- **Database Integration**: Persistent data storage
- **API Support**: RESTful interface for external systems
- **Mobile Interface**: Responsive web-based GUI

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all files are in the same directory
2. **Data Format**: Check CSV headers match expected format
3. **Memory Issues**: Large datasets may require optimization
4. **Export Errors**: Check file permissions and paths

### Performance Tips
- Use smaller datasets for testing
- Close other applications during generation
- Ensure sufficient disk space for exports
- Check system memory availability

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

---

**Generated by Timetable Generator (CSP) | 2024**
