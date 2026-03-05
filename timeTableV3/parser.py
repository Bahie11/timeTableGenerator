import pandas as pd
from typing import Dict, List, Tuple, Any


def _read_df(path: str) -> pd.DataFrame:
    return pd.read_excel(path)


def parse_instructors(path: str) -> Dict[str, Dict[str, Any]]:
    df = _read_df(path)
    instructors = {}
    for _, row in df.fillna("").iterrows():
        iid = str(row.get('id') or row.get('ID') or row.get('InstructorID') or row.get('InstructorId') or row.get('Instructor'))
        instructors[iid] = {
            'id': iid,
            'name': row.get('name') or row.get('Name') or row.get('InstructorName') or '',
            'max_load': int(row.get('max_load') or row.get('maxLoad') or 0) if (row.get('max_load') not in (None, '') or row.get('maxLoad') not in (None, '')) else 0,
            'unavailable': [s.strip() for s in str(row.get('unavailable_slots') or row.get('PreferredSlots') or '').split(',') if s.strip()],
            'qualified': [s.strip() for s in str(row.get('QualifiedCourses') or row.get('qualifiedcourses') or row.get('qualified_courses') or row.get('qualified') or '').split(',') if s.strip()]
        }
    return instructors


def parse_rooms(path: str) -> Dict[str, Dict[str, Any]]:
    df = _read_df(path)
    rooms = {}
    for _, row in df.fillna("").iterrows():
        rid = str(row.get('id') or row.get('ID') or row.get('RoomID') or row.get('RoomId'))
        rooms[rid] = {
            'id': rid,
            'name': row.get('name') or row.get('Name') or row.get('RoomName') or '',
            'capacity': int(row.get('capacity') or 0),
            'type': (row.get('type') or row.get('Type') or row.get('room_type') or '').strip(),
            'features': [s.strip().lower() for s in str(row.get('features') or '').split(',') if s.strip()]
        }
    return rooms


def parse_timeslots(path: str) -> Dict[str, Dict[str, Any]]:
    df = _read_df(path)
    times = {}
    for _, row in df.fillna("").iterrows():
        tid = str(row.get('id') or row.get('ID') or row.get('TimeSlotID') or row.get('Id') or row.get('id'))
        times[tid] = {
            'id': tid,
            'day': row.get('day') or row.get('Day') or row.get('DayName') or '',
            'start': str(row.get('start') or row.get('StartTime') or ''),
            'end': str(row.get('end') or row.get('EndTime') or '')
        }
    return times


def parse_courses(path: str) -> Dict[str, Dict[str, Any]]:
    df = _read_df(path)
    courses = {}
    for _, row in df.fillna("").iterrows():
        cid = str(row.get('id') or row.get('ID') or row.get('CourseID') or row.get('CourseId'))
        courses[cid] = {
            'id': cid,
            'name': row.get('name') or row.get('Name') or row.get('CourseName') or '',
            'credits': int(row.get('credits') or 0) if row.get('credits') not in (None, '') else 0,
            'type': (row.get('type') or row.get('Type') or '').strip(),
            'students': int(row.get('students') or row.get('StudentCount') or 0),
            'required_features': [s.strip().lower() for s in str(row.get('required_features') or row.get('RequiredFeatures') or '').split(',') if s.strip()],
            'sessions_per_week': int(row.get('sessions_per_week') or row.get('SessionsPerWeek') or 1),
            'preferred_times': [s.strip() for s in str(row.get('preferred_times') or row.get('PreferredSlots') or '').split(',') if s.strip()]
        }
    return courses


def parse_sections(path: str) -> Dict[str, Dict[str, Any]]:
    # Sections are optional; if file missing or empty, callers can create default sections
    df = _read_df(path)
    sections = {}
    for _, row in df.fillna("").iterrows():
        sid = str(row.get('id') or row.get('ID') or row.get('SectionID') or row.get('Section'))
        sections[sid] = {
            'id': sid,
            'semester': row.get('Semester') or row.get('semester') or '',
            'student_count': int(row.get('StudentCount') or row.get('students') or 0)
        }
    return sections


def read_all(instructors_path, rooms_path, courses_path, timeslots_path, sections_path=None):
    instructors = parse_instructors(instructors_path)
    rooms = parse_rooms(rooms_path)
    courses = parse_courses(courses_path)
    timeslots = parse_timeslots(timeslots_path)
    sections = {}
    if sections_path:
        try:
            sections = parse_sections(sections_path)
        except Exception:
            sections = {}
    return instructors, rooms, courses, timeslots, sections

