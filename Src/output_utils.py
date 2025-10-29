"""
Output utilities for CSV, console, and HTML export.
"""
import csv
import time
from typing import Dict, List, Tuple

try:
    from .models import Assignment, Instructor, TimeSlot
except ImportError:
    from models import Assignment, Instructor, TimeSlot


def get_proper_sort_key(assignment_tuple, timeslots: List[TimeSlot]):
    """Create a proper sort key for schedule items to order by weekday and time"""
    instructor_id, (slot_index, room_id, course) = assignment_tuple
    ts = timeslots[slot_index]
    
    # Define weekday order for proper sorting
    weekday_order = {
        'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 
        'Thursday': 4, 'Friday': 5, 'Saturday': 6
    }
    
    day_order = weekday_order.get(ts.day, 999)  # Unknown days go last
    
    # Parse time for proper sorting (handle AM/PM and 24-hour formats)
    time_str = ts.start_time
    try:
        # Convert time to sortable format
        if 'AM' in time_str or 'PM' in time_str:
            # Handle 12-hour format
            time_part = time_str.replace(' AM', '').replace(' PM', '')
            hour, minute = map(int, time_part.split(':'))
            if 'PM' in time_str and hour != 12:
                hour += 12
            elif 'AM' in time_str and hour == 12:
                hour = 0
            time_sort = hour * 60 + minute
        else:
            # Handle 24-hour format
            hour, minute = map(int, time_str.split(':'))
            time_sort = hour * 60 + minute
    except:
        time_sort = 0
    
    return (day_order, time_sort, course, instructor_id)


def write_schedule_csv(
    output_path: str,
    solution: Dict[str, Assignment],
    instructors_by_id: Dict[str, Instructor],
    timeslots: List[TimeSlot],
):
    """Write schedule to CSV file with proper sorting."""
    fieldnames = [
        "InstructorID",
        "Name",
        "Day",
        "StartTime",
        "EndTime",
        "RoomID",
        "Course",
    ]
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for instructor_id, (slot_index, room_id, course) in sorted(solution.items(), key=lambda kv: get_proper_sort_key(kv, timeslots)):
                instructor = instructors_by_id[instructor_id]
                ts = timeslots[slot_index]
                writer.writerow(
                    {
                        "InstructorID": instructor.instructor_id,
                        "Name": instructor.name,
                        "Day": ts.day,
                        "StartTime": ts.start_time,
                        "EndTime": ts.end_time,
                        "RoomID": room_id,
                        "Course": course,
                    }
                )
    except PermissionError:
        # Try with a different filename if the original is locked
        import os
        base_name, ext = os.path.splitext(output_path)
        counter = 1
        while True:
            new_path = f"{base_name}_{counter}{ext}"
            try:
                with open(new_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for instructor_id, (slot_index, room_id, course) in sorted(solution.items(), key=lambda kv: get_proper_sort_key(kv, timeslots)):
                        instructor = instructors_by_id[instructor_id]
                        ts = timeslots[slot_index]
                        writer.writerow(
                            {
                                "InstructorID": instructor.instructor_id,
                                "Name": instructor.name,
                                "Day": ts.day,
                                "StartTime": ts.start_time,
                                "EndTime": ts.end_time,
                                "RoomID": room_id,
                                "Course": course,
                            }
                        )
                # Update the output_path to the new successful path
                output_path = new_path
                break
            except PermissionError:
                counter += 1
                if counter > 100:  # Prevent infinite loop
                    raise PermissionError(f"Cannot write to {output_path} - file may be open in another program")
    except Exception as e:
        raise Exception(f"Error writing CSV file: {str(e)}")


def print_schedule(solution: Dict[str, Assignment], instructors_by_id: Dict[str, Instructor], timeslots: List[TimeSlot]):
    """Print schedule to console with proper sorting and debug information."""
    rows: List[Tuple[str, str, str, str, str, str]] = []
    for instructor_id, (slot_index, room_id, course) in sorted(solution.items(), key=lambda kv: get_proper_sort_key(kv, timeslots)):
        instructor = instructors_by_id[instructor_id]
        ts = timeslots[slot_index]
        rows.append((instructor.name, instructor.instructor_id, ts.day, f"{ts.start_time}-{ts.end_time}", room_id, course))

    # Compute column widths for a simple console table
    headers = ("Instructor", "ID", "Day", "Time", "Room", "Course")
    table = [headers] + rows
    col_widths = [max(len(str(row[i])) for row in table) for i in range(len(headers))]

    def fmt(row: Tuple[str, ...]) -> str:
        return " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(headers)))

    sep = "-+-".join("-" * w for w in col_widths)
    print(fmt(headers))
    print(sep)
    for r in rows:
        print(fmt(r))
    
    # Print debug information
    print(f"\nDebug Information:")
    print(f"Total assignments: {len(solution)}")
    
    # Check for conflicts
    room_time_conflicts = {}
    for instructor_id, (slot_index, room_id, course) in solution.items():
        key = (slot_index, room_id)
        if key in room_time_conflicts:
            print(f"⚠️  CONFLICT: Room {room_id} at timeslot {slot_index} has multiple assignments!")
            print(f"   - {instructor_id}: {course}")
            print(f"   - {room_time_conflicts[key][0]}: {room_time_conflicts[key][1]}")
        else:
            room_time_conflicts[key] = (instructor_id, course)
    
    # Check day distribution
    day_distribution = {}
    for instructor_id, (slot_index, room_id, course) in solution.items():
        day = timeslots[slot_index].day
        day_distribution[day] = day_distribution.get(day, 0) + 1
    
    print(f"\nDay Distribution:")
    for day, count in sorted(day_distribution.items()):
        print(f"  {day}: {count} courses")
    
    if len(day_distribution) < 5:
        print("⚠️  WARNING: Not all weekdays are being used!")
