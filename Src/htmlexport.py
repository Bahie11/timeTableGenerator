"""
HTML export functionality for timetables.
"""
import time
from typing import Dict, List
from models import Instructor, TimeSlot, Assignment
from output_utils import get_proper_sort_key


def export_schedule_html(solution: Dict[str, Assignment], instructors_by_id: Dict[str, Instructor], timeslots: List[TimeSlot], path: str):
    """Export the complete schedule to HTML format"""
    if not solution or not timeslots:
        raise ValueError("No schedule data available")
    
    # Sort schedule by day and time
    sorted_assignments = sorted(solution.items(), key=lambda kv: get_proper_sort_key(kv, timeslots))
    
    # Group by day
    schedule_by_day = {}
    for key, value in sorted_assignments:
        # Handle both old format (3 values) and new format (4 values)
        if len(value) == 4:
            slot_index, room_id, course, instructor_id = value
        else:
            slot_index, room_id, course = value
            instructor_id = key
            
        ts = timeslots[slot_index]
        day = ts.day
        if day not in schedule_by_day:
            schedule_by_day[day] = []
        instructor = instructors_by_id.get(instructor_id)
        if not instructor:
            continue
        schedule_by_day[day].append({
            'instructor_name': instructor.name,
            'instructor_id': instructor.instructor_id,
            'time': f"{ts.start_time}-{ts.end_time}",
            'room': room_id,
            'course': course
        })
    
    # Generate HTML content
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>University Timetable</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .content {{
            padding: 30px;
        }}
        .day-section {{
            margin-bottom: 40px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        .day-header {{
            background: linear-gradient(135deg, #F18F01 0%, #FF9800 100%);
            color: white;
            padding: 20px;
            font-size: 1.5em;
            font-weight: bold;
            text-align: center;
        }}
        .schedule-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}
        .schedule-table th {{
            background: #f8f9fa;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #e9ecef;
        }}
        .schedule-table td {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
            vertical-align: top;
        }}
        .schedule-table tr:hover {{
            background: #f8f9fa;
        }}
        .time-cell {{
            font-weight: 600;
            color: #2E86AB;
            width: 120px;
        }}
        .instructor-cell {{
            font-weight: 500;
        }}
        .course-cell {{
            background: #e3f2fd;
            color: #1976d2;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: 600;
            display: inline-block;
        }}
        .room-cell {{
            background: #f3e5f5;
            color: #7b1fa2;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: 600;
            display: inline-block;
        }}
        .stats {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .stats h3 {{
            margin: 0 0 15px 0;
            color: #333;
        }}
        .stat-item {{
            display: inline-block;
            margin: 0 20px;
            padding: 10px 20px;
            background: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 1.5em;
            font-weight: bold;
            color: #2E86AB;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e9ecef;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 University Timetable</h1>
            <p>Generated on {time.strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="content">
            <div class="stats">
                <h3>📊 Schedule Statistics</h3>
                <div class="stat-item">
                    <div class="stat-number">{len(solution)}</div>
                    <div class="stat-label">Total Classes</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{len(schedule_by_day)}</div>
                    <div class="stat-label">Days Scheduled</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{len(set(assignment[1][1] for assignment in solution.values()))}</div>
                    <div class="stat-label">Rooms Used</div>
                </div>
            </div>
"""
    
    # Add each day's schedule
    weekday_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    for day in weekday_order:
        if day in schedule_by_day:
            html_content += f"""
            <div class="day-section">
                <div class="day-header">
                    📅 {day}
                </div>
                <table class="schedule-table">
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Instructor</th>
                            <th>Course</th>
                            <th>Room</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            for item in schedule_by_day[day]:
                html_content += f"""
                        <tr>
                            <td class="time-cell">{item['time']}</td>
                            <td class="instructor-cell">{item['instructor_name']}<br><small>({item['instructor_id']})</small></td>
                            <td><span class="course-cell">{item['course']}</span></td>
                            <td><span class="room-cell">{item['room']}</span></td>
                        </tr>
"""
            html_content += """
                    </tbody>
                </table>
            </div>
"""
    
    html_content += f"""
        </div>
        
        <div class="footer">
            <p>Generated by Timetable Generator (CSP) | {time.strftime('%Y')}</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Write HTML file
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def export_instructor_html(instructor_id: str, solution: Dict[str, Assignment], instructors_by_id: Dict[str, Instructor], timeslots: List[TimeSlot], path: str):
    """Export individual instructor timetable to HTML format"""
    if not solution or not timeslots:
        raise ValueError("No schedule data available")
    
    instructor = instructors_by_id.get(instructor_id)
    if not instructor:
        raise ValueError(f"Instructor {instructor_id} not found in instructors list")
    
    # Get all assignments for this instructor (in case they have multiple)
    instructor_assignments = []
    for key, value in solution.items():
        # Handle both old format (3 values) and new format (4 values)
        if len(value) == 4:
            slot_idx, room, course_code, iid = value
        else:
            slot_idx, room, course_code = value
            iid = key
            
        if iid == instructor_id:
            ts_obj = timeslots[slot_idx]
            instructor_assignments.append({
                'day': ts_obj.day,
                'time': f"{ts_obj.start_time}-{ts_obj.end_time}",
                'room': room,
                'course': course_code
            })
    
    # Check if we found any assignments for this instructor
    if not instructor_assignments:
        raise ValueError(f"No schedule found for instructor {instructor_id}")
    
    # Sort by day and time using proper weekday order
    weekday_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
    def instructor_sort_key(assignment):
        day_order = weekday_order.index(assignment['day']) if assignment['day'] in weekday_order else 999
        # Parse time for proper sorting
        time_str = assignment['time'].split('-')[0]  # Get start time
        try:
            if 'AM' in time_str or 'PM' in time_str:
                time_part = time_str.replace(' AM', '').replace(' PM', '')
                hour, minute = map(int, time_part.split(':'))
                if 'PM' in time_str and hour != 12:
                    hour += 12
                elif 'AM' in time_str and hour == 12:
                    hour = 0
                time_sort = hour * 60 + minute
            else:
                hour, minute = map(int, time_str.split(':'))
                time_sort = hour * 60 + minute
        except:
            time_sort = 0
        return (day_order, time_sort, assignment['course'])
    
    instructor_assignments.sort(key=instructor_sort_key)
    
    # Generate HTML content
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{instructor.name} - Personal Timetable</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.2em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .instructor-info {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .info-item {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .info-label {{
            font-weight: 600;
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }}
        .info-value {{
            font-size: 1.1em;
            color: #333;
        }}
        .content {{
            padding: 30px;
        }}
        .schedule-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        .schedule-table th {{
            background: linear-gradient(135deg, #F18F01 0%, #FF9800 100%);
            color: white;
            padding: 20px;
            text-align: left;
            font-weight: 600;
            font-size: 1.1em;
        }}
        .schedule-table td {{
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
            vertical-align: top;
        }}
        .schedule-table tr:hover {{
            background: #f8f9fa;
        }}
        .time-cell {{
            font-weight: 600;
            color: #2E86AB;
            width: 150px;
            font-size: 1.1em;
        }}
        .day-cell {{
            font-weight: 600;
            color: #333;
            width: 120px;
        }}
        .course-cell {{
            background: #e3f2fd;
            color: #1976d2;
            padding: 8px 15px;
            border-radius: 8px;
            font-weight: 600;
            display: inline-block;
            font-size: 1.1em;
        }}
        .room-cell {{
            background: #f3e5f5;
            color: #7b1fa2;
            padding: 8px 15px;
            border-radius: 8px;
            font-weight: 600;
            display: inline-block;
            font-size: 1.1em;
        }}
        .no-classes {{
            text-align: center;
            padding: 40px;
            color: #666;
            font-style: italic;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e9ecef;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👨‍🏫 Personal Timetable</h1>
            <p>Generated on {time.strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="instructor-info">
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Instructor Name</div>
                    <div class="info-value">{instructor.name}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Instructor ID</div>
                    <div class="info-value">{instructor.instructor_id}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Total Classes</div>
                    <div class="info-value">{len(instructor_assignments)}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Unavailable</div>
                    <div class="info-value">{instructor.unavailable_day or 'N/A'}</div>
                </div>
            </div>
        </div>
        
        <div class="content">
"""
    
    if instructor_assignments:
        html_content += """
            <table class="schedule-table">
                <thead>
                    <tr>
                        <th>Day</th>
                        <th>Time</th>
                        <th>Course</th>
                        <th>Room</th>
                    </tr>
                </thead>
                <tbody>
"""
        for assignment in instructor_assignments:
            html_content += f"""
                    <tr>
                        <td class="day-cell">{assignment['day']}</td>
                        <td class="time-cell">{assignment['time']}</td>
                        <td><span class="course-cell">{assignment['course']}</span></td>
                        <td><span class="room-cell">{assignment['room']}</span></td>
                    </tr>
"""
        html_content += """
                </tbody>
            </table>
"""
    else:
        html_content += """
            <div class="no-classes">
                <h3>No classes scheduled</h3>
                <p>This instructor has no classes in the current schedule.</p>
            </div>
"""
    
    html_content += f"""
        </div>
        
        <div class="footer">
            <p>Generated by Timetable Generator (CSP) | {time.strftime('%Y')}</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Write HTML file
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def export_grid_html(solution: Dict[str, Assignment], instructors_by_id: Dict[str, Instructor], timeslots: List[TimeSlot], path: str):
    """Export timetable as a weekly grid format"""
    if not solution or not timeslots:
        raise ValueError("No schedule data available")
    
    # Create a grid structure (Sunday through Thursday only)
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']
    
    # Get all unique time slots and sort them
    unique_times = []
    for ts in timeslots:
        time_key = f"{ts.start_time}-{ts.end_time}"
        if time_key not in unique_times:
            unique_times.append(time_key)
    
    # Sort time slots properly
    def time_sort_key(time_str):
        start_time = time_str.split('-')[0]
        try:
            if 'AM' in start_time or 'PM' in start_time:
                time_part = start_time.replace(' AM', '').replace(' PM', '')
                hour, minute = map(int, time_part.split(':'))
                if 'PM' in start_time and hour != 12:
                    hour += 12
                elif 'AM' in start_time and hour == 12:
                    hour = 0
                return hour * 60 + minute
            else:
                hour, minute = map(int, start_time.split(':'))
                return hour * 60 + minute
        except:
            return 0
    
    unique_times.sort(key=time_sort_key)
    
    # Create grid data structure
    grid_data = {}
    for day in days:
        grid_data[day] = {}
        for time_slot in unique_times:
            grid_data[day][time_slot] = []
    
    # Populate grid with schedule data
    for key, value in solution.items():
        # Handle both old format (3 values) and new format (4 values)
        if len(value) == 4:
            slot_index, room_id, course, instructor_id = value
        else:
            slot_index, room_id, course = value
            instructor_id = key
            
        ts = timeslots[slot_index]
        instructor = instructors_by_id.get(instructor_id)
        if not instructor:
            continue
        time_key = f"{ts.start_time}-{ts.end_time}"
        
        if ts.day in grid_data and time_key in grid_data[ts.day]:
            grid_data[ts.day][time_key].append({
                'instructor': instructor.name,
                'instructor_id': instructor.instructor_id,
                'course': course,
                'room': room_id,
                'course_type': 'LEC'  # Default, could be enhanced
            })
    
    # Generate HTML content
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weekly Timetable Grid</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .timetable-grid {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}
        .timetable-grid th {{
            background: linear-gradient(135deg, #F18F01 0%, #FF9800 100%);
            color: white;
            padding: 15px 10px;
            text-align: center;
            font-weight: 600;
            font-size: 1.1em;
            border: 1px solid #ddd;
        }}
        .timetable-grid td {{
            padding: 8px;
            border: 1px solid #ddd;
            vertical-align: top;
            min-height: 60px;
            position: relative;
        }}
        .time-cell {{
            background: #f8f9fa;
            font-weight: 600;
            color: #2E86AB;
            text-align: center;
            width: 120px;
            font-size: 0.9em;
        }}
        .day-header {{
            background: linear-gradient(135deg, #4CAF50 0%, #45A049 100%);
            color: white;
            font-weight: bold;
            text-align: center;
        }}
        .course-entry {{
            background: #e3f2fd;
            border: 1px solid #1976d2;
            border-radius: 5px;
            padding: 8px;
            margin: 2px 0;
            font-size: 0.85em;
            line-height: 1.3;
        }}
        .course-name {{
            font-weight: 600;
            color: #1976d2;
            margin-bottom: 3px;
        }}
        .course-details {{
            color: #666;
            font-size: 0.8em;
        }}
        .instructor-name {{
            color: #333;
            font-weight: 500;
        }}
        .room-info {{
            color: #7b1fa2;
            font-weight: 600;
        }}
        .empty-cell {{
            text-align: center;
            color: #999;
            font-style: italic;
        }}
        .grid-container {{
            overflow-x: auto;
            padding: 20px;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e9ecef;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📅 Weekly Timetable Grid</h1>
            <p>Generated on {time.strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="grid-container">
            <table class="timetable-grid">
                <thead>
                    <tr>
                        <th class="time-cell">Time</th>
"""
    
    # Add day headers
    for day in days:
        html_content += f'                        <th class="day-header">{day}</th>\n'
    
    html_content += """                    </tr>
                </thead>
                <tbody>
"""
    
    # Add time rows
    for time_slot in unique_times:
        html_content += f"""                    <tr>
                        <td class="time-cell">{time_slot}</td>
"""
        for day in days:
            if grid_data[day][time_slot]:
                html_content += f"""                        <td>
"""
                for entry in grid_data[day][time_slot]:
                    html_content += f"""                            <div class="course-entry">
                                <div class="course-name">{entry['course']}</div>
                                <div class="course-details">
                                    <div class="instructor-name">{entry['instructor']}</div>
                                    <div class="room-info">Room: {entry['room']}</div>
                                </div>
                            </div>
"""
                html_content += """                        </td>
"""
            else:
                html_content += """                        <td class="empty-cell">-</td>
"""
        html_content += """                    </tr>
"""
    
    html_content += f"""                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Generated by Timetable Generator (CSP) | {time.strftime('%Y')}</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Write HTML file
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html_content)
