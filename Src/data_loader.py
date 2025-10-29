"""
Data loading utilities for CSV and Excel files.
"""
import csv
import os
from pathlib import Path
from typing import List, Optional
import datetime

from models import TimeSlot, Room, Instructor, Course


def _ensure_pandas():
    try:
        import pandas as pd  # type: ignore
        import openpyxl  # Verify openpyxl is also available
        return pd
    except ImportError as e:
        # More specific error message showing what's actually missing
        raise ImportError(f"Excel import requires pandas and openpyxl.\n\nError: {str(e)}\n\nInstall via: pip install pandas openpyxl") from e
    except Exception as e:
        # Unexpected error during import
        raise ImportError(f"Failed to import pandas/openpyxl: {str(e)}\n\nTry reinstalling: pip install --force-reinstall pandas openpyxl") from e


def _resolve_path(path: str) -> str:
    if not path:
        raise FileNotFoundError("No path provided")
    p = Path(os.path.expanduser(str(path))).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {p}")
    return str(p)


def _read_excel_sheet(path: str, sheet_name: Optional[str] = None):
    pd = _ensure_pandas()
    
    # Determine engine based on file extension
    file_ext = Path(path).suffix.lower()
    engine = None
    
    if file_ext == '.xlsx':
        engine = 'openpyxl'
    elif file_ext == '.xls':
        # For older Excel files, try xlrd or let pandas choose
        try:
            import xlrd
            engine = 'xlrd'
        except ImportError:
            # If xlrd is not available, let pandas auto-detect
            engine = None
    
    try:
        if engine:
            df = pd.read_excel(path, sheet_name=sheet_name, engine=engine)
        else:
            df = pd.read_excel(path, sheet_name=sheet_name)
    except Exception as e:
        # Provide helpful error message
        if "zip file" in str(e).lower():
            raise ValueError(f"Cannot read Excel file: '{Path(path).name}' appears to be in an unsupported format. "
                           f"Please save it as .xlsx (Excel 2007+) format and try again.") from e
        raise
    
    if isinstance(df, dict):
        if sheet_name and sheet_name in df:
            return df[sheet_name]
        # deterministic first sheet
        first_key = next(iter(df))
        return df[first_key]
    return df


def load_timeslots(csv_path: str) -> List[TimeSlot]:
    resolved = _resolve_path(csv_path)
    timeslots: List[TimeSlot] = []
    with open(resolved, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            st = row.get("StartTime")
            et = row.get("EndTime")
            # try parse times if strings like "09:00"
            def _parse_time(v):
                if v is None or v == "":
                    return None
                if isinstance(v, datetime.time):
                    return v
                try:
                    return datetime.datetime.strptime(str(v).strip(), "%H:%M").time()
                except Exception:
                    try:
                        return datetime.datetime.strptime(str(v).strip(), "%I:%M %p").time()
                    except Exception:
                        return None
            timeslots.append(TimeSlot(day=(row.get("Day") or "").strip(), start_time=_parse_time(st), end_time=_parse_time(et)))
    return timeslots


def load_rooms(csv_path: str) -> List[Room]:
    resolved = _resolve_path(csv_path)
    rooms: List[Room] = []
    with open(resolved, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cap = None
            try:
                cap = int(str(row.get("Capacity") or 0).strip())
            except Exception:
                cap = None
            rooms.append(Room(room_id=str(row.get("RoomID") or "").strip(), room_type=str(row.get("Type") or "").strip(), capacity=cap))
    return rooms


def load_instructors(csv_path: str) -> List[Instructor]:
    resolved = _resolve_path(csv_path)
    instructors: List[Instructor] = []
    with open(resolved, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pref = (row.get("PreferredSlots") or "").strip()
            qc = (row.get("QualifiedCourses") or "").strip()
            # QualifiedCourses may be single code or semicolon/comma separated
            qlist = [c.strip() for c in (qc.split(";") if ";" in qc else qc.split(",") ) if c.strip()] if qc else []
            instructors.append(Instructor(instructor_id=str(row.get("InstructorID") or "").strip(), name=str(row.get("Name") or "").strip(), unavailable_day=pref, qualified_courses=qlist))
    return instructors


def load_courses(csv_path: str) -> List[Course]:
    resolved = _resolve_path(csv_path)
    courses: List[Course] = []
    with open(resolved, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            credits = None
            try:
                if row.get("Credits") not in (None, ""):
                    credits = int(str(row.get("Credits")).strip())
            except Exception:
                credits = None
            courses.append(Course(course_id=str(row.get("CourseID") or "").strip(), course_name=str(row.get("CourseName") or "").strip(), course_type=str(row.get("Type") or "").strip(), credits=credits))
    return courses


def load_timeslots_excel(path: str, sheet_name: Optional[str] = None) -> List[TimeSlot]:
    df = _read_excel_sheet(_resolve_path(path), sheet_name)
    res: List[TimeSlot] = []
    for _, row in df.iterrows():
        st = row.get("StartTime")
        et = row.get("EndTime")
        if isinstance(st, str):
            try:
                st = datetime.datetime.strptime(st.strip(), "%H:%M").time()
            except Exception:
                st = None
        if isinstance(et, str):
            try:
                et = datetime.datetime.strptime(et.strip(), "%H:%M").time()
            except Exception:
                et = None
        res.append(TimeSlot(day=str(row.get("Day") or "").strip(), start_time=st, end_time=et))
    return res


def load_rooms_excel(path: str, sheet_name: Optional[str] = None) -> List[Room]:
    df = _read_excel_sheet(_resolve_path(path), sheet_name)
    res: List[Room] = []
    for _, row in df.iterrows():
        cap = None
        try:
            cap = int(row.get("Capacity")) if not (row.get("Capacity") is None) else None
        except Exception:
            cap = None
        res.append(Room(room_id=str(row.get("RoomID") or "").strip(), room_type=str(row.get("Type") or "").strip(), capacity=cap))
    return res


def load_instructors_excel(path: str, sheet_name: Optional[str] = None) -> List[Instructor]:
    df = _read_excel_sheet(_resolve_path(path), sheet_name)
    res: List[Instructor] = []
    for _, row in df.iterrows():
        pref = (row.get("PreferredSlots") or "").strip()
        qc = (row.get("QualifiedCourses") or "").strip()
        qlist = [c.strip() for c in (qc.split(";") if ";" in qc else qc.split(",") ) if c.strip()] if qc else []
        res.append(Instructor(instructor_id=str(row.get("InstructorID") or "").strip(), name=str(row.get("Name") or "").strip(), unavailable_day=pref, qualified_courses=qlist))
    return res


def load_courses_excel(path: str, sheet_name: Optional[str] = None) -> List[Course]:
    df = _read_excel_sheet(_resolve_path(path), sheet_name)
    res: List[Course] = []
    for _, row in df.iterrows():
        credits = None
        try:
            if row.get("Credits") not in (None, ""):
                credits = int(row.get("Credits"))
        except Exception:
            credits = None
        res.append(Course(course_id=str(row.get("CourseID") or "").strip(), course_name=str(row.get("CourseName") or "").strip(), course_type=str(row.get("Type") or "").strip(), credits=credits))
    return res
