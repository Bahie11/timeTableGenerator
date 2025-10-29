"""
Output utilities for CSV, console, and HTML export.
"""
import csv
import time
from typing import Dict, List, Tuple
import logging

from models import Assignment, Instructor, TimeSlot

def get_proper_sort_key(assignment_tuple, timeslots: List[TimeSlot]):
    try:
        instructor_id, (slot_index, room_id, course) = assignment_tuple
    except Exception:
        return (999, 99999, "", "")
    weekday_order = {
        'sunday': 0, 'monday': 1, 'tuesday': 2, 'wednesday': 3,
        'thursday': 4, 'friday': 5, 'saturday': 6
    }
    try:
        ts = timeslots[slot_index]
        day = (getattr(ts, "day", "") or "").strip().lower()
        st = getattr(ts, "start_time", None)
        if hasattr(st, "hour"):
            time_sort = st.hour * 60 + getattr(st, "minute", 0)
        else:
            try:
                parts = str(st or "").split(":")
                time_sort = int(parts[0]) * 60 + (int(parts[1]) if len(parts) > 1 else 0)
            except Exception:
                time_sort = 0
    except Exception:
        logging.exception("Failed to build sort key")
        return (999, 99999, course or "", instructor_id or "")
    day_order = weekday_order.get(day, 999)
    return (day_order, time_sort, course or "", instructor_id or "")


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
            for key, value in sorted(solution.items(), key=lambda kv: get_proper_sort_key(kv, timeslots)):
                # Handle both old format (3 values) and new format (4 values)
                if len(value) == 4:
                    slot_index, room_id, course, instructor_id = value
                else:
                    slot_index, room_id, course = value
                    instructor_id = key
                    
                instructor = instructors_by_id.get(instructor_id)
                if not instructor:
                    continue
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
                    for key, value in sorted(solution.items(), key=lambda kv: get_proper_sort_key(kv, timeslots)):
                        # Handle both old format (3 values) and new format (4 values)
                        if len(value) == 4:
                            slot_index, room_id, course, instructor_id = value
                        else:
                            slot_index, room_id, course = value
                            instructor_id = key
                            
                        instructor = instructors_by_id.get(instructor_id)
                        if not instructor:
                            continue
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
    for key, value in sorted(solution.items(), key=lambda kv: get_proper_sort_key(kv, timeslots)):
        # Handle both old format (3 values) and new format (4 values)
        if len(value) == 4:
            slot_index, room_id, course, instructor_id = value
        else:
            slot_index, room_id, course = value
            instructor_id = key
            
        instructor = instructors_by_id.get(instructor_id)
        if not instructor:
            continue
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
    for sol_key, value in solution.items():
        # Handle both formats
        if len(value) == 4:
            slot_index, room_id, course, instructor_id = value
        else:
            slot_index, room_id, course = value
            instructor_id = sol_key
            
        conflict_key = (slot_index, room_id)
        if conflict_key in room_time_conflicts:
            print(f"⚠️  CONFLICT: Room {room_id} at timeslot {slot_index} has multiple assignments!")
            print(f"   - {instructor_id}: {course}")
            print(f"   - {room_time_conflicts[conflict_key][0]}: {room_time_conflicts[conflict_key][1]}")
        else:
            room_time_conflicts[conflict_key] = (instructor_id, course)
    
    # Check day distribution
    day_distribution = {}
    for sol_key, value in solution.items():
        # Handle both formats
        if len(value) == 4:
            slot_index = value[0]
        else:
            slot_index = value[0]
        day = timeslots[slot_index].day
        day_distribution[day] = day_distribution.get(day, 0) + 1
    
    print(f"\nDay Distribution:")
    for day, count in sorted(day_distribution.items()):
        print(f"  {day}: {count} courses")
    
    if len(day_distribution) < 5:
        print("⚠️  WARNING: Not all weekdays are being used!")
