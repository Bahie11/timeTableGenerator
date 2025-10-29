"""
Data loading utilities for CSV and Excel files.
"""
import csv
from typing import List, Optional

try:
    from .models import TimeSlot, Room, Instructor, Course
except ImportError:
    from models import TimeSlot, Room, Instructor, Course


def load_timeslots(csv_path: str) -> List[TimeSlot]:
    timeslots: List[TimeSlot] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            timeslots.append(
                TimeSlot(day=row["Day"].strip(), start_time=row["StartTime"].strip(), end_time=row["EndTime"].strip())
            )
    return timeslots


def load_rooms(csv_path: str) -> List[Room]:
    rooms: List[Room] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            capacity_value = 0
            try:
                capacity_value = int(str(row["Capacity"]).strip())
            except Exception:
                capacity_value = 0
            rooms.append(
                Room(
                    room_id=row["RoomID"].strip(),
                    room_type=row["Type"].strip(),
                    capacity=capacity_value,
                )
            )
    return rooms


def load_instructors(csv_path: str) -> List[Instructor]:
    instructors: List[Instructor] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            instructors.append(
                Instructor(
                    instructor_id=row["InstructorID"].strip(),
                    name=row["Name"].strip(),
                    role=row["Role"].strip(),
                    unavailable_day=parse_unavailable_day(row.get("PreferredSlots", "")),
                    qualified_courses=parse_qualified_courses(row.get("QualifiedCourses", "")),
                )
            )
    return instructors


def load_courses(csv_path: str) -> List[Course]:
    courses: List[Course] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            credits: Optional[int] = None
            if row.get("Credits"):
                try:
                    credits = int(str(row["Credits"]).strip())
                except Exception:
                    credits = None
            courses.append(
                Course(
                    course_id=row.get("CourseID", "").strip(),
                    course_name=row.get("CourseName", "").strip(),
                    course_type=(row.get("Type", "Lecture") or "Lecture").strip(),
                    credits=credits,
                )
            )
    return courses


def parse_unavailable_day(preferred_slots_value: str) -> Optional[str]:
    value = (preferred_slots_value or "").strip()
    # Expected like: "Not on Monday"
    if value.lower().startswith("not on "):
        return value.split(" ", 2)[-1].strip()
    return None


def parse_qualified_courses(csv_value: str) -> List[str]:
    if not csv_value:
        return []
    # Split by comma and strip whitespace
    parts = [p.strip() for p in str(csv_value).split(",")]
    return [p for p in parts if p]


# ---------- Optional Excel import (requires pandas + openpyxl) ----------
def _ensure_pandas():
    try:
        import pandas as _pd  # type: ignore
        return _pd
    except Exception as exc:
        raise ImportError(
            "Excel import requires pandas (and openpyxl). Install via: pip install pandas openpyxl"
        ) from exc


def load_instructors_excel(path: str, sheet_name: Optional[str] = None) -> List[Instructor]:
    pd = _ensure_pandas()
    df = pd.read_excel(path, sheet_name=sheet_name)
    # Normalize columns
    cols = {c.lower().strip(): c for c in df.columns}
    def col(name: str) -> str:
        return cols.get(name.lower(), name)
    result: List[Instructor] = []
    for _, row in df.iterrows():
        pref = str(row.get(col("PreferredSlots"), "") or "")
        result.append(
            Instructor(
                instructor_id=str(row.get(col("InstructorID"), "")).strip(),
                name=str(row.get(col("Name"), "")).strip(),
                role=str(row.get(col("Role"), "Professor") or "Professor").strip(),
                unavailable_day=parse_unavailable_day(pref),
                qualified_courses=parse_qualified_courses(str(row.get(col("QualifiedCourses"), "") or "")),
            )
        )
    return [i for i in result if i.instructor_id]


def load_rooms_excel(path: str, sheet_name: Optional[str] = None) -> List[Room]:
    pd = _ensure_pandas()
    df = pd.read_excel(path, sheet_name=sheet_name)
    cols = {c.lower().strip(): c for c in df.columns}
    def col(name: str) -> str:
        return cols.get(name.lower(), name)
    result: List[Room] = []
    for _, row in df.iterrows():
        cap = row.get(col("Capacity"))
        try:
            cap_int = int(cap) if not (cap is None or (isinstance(cap, float) and pd.isna(cap))) else 0
        except Exception:
            cap_int = 0
        result.append(
            Room(
                room_id=str(row.get(col("RoomID"), "")).strip(),
                room_type=str(row.get(col("Type"), "Lecture") or "Lecture").strip(),
                capacity=cap_int,
            )
        )
    return [r for r in result if r.room_id]


def load_courses_excel(path: str, sheet_name: Optional[str] = None) -> List[Course]:
    pd = _ensure_pandas()
    df = pd.read_excel(path, sheet_name=sheet_name)
    cols = {c.lower().strip(): c for c in df.columns}
    def col(name: str) -> str:
        return cols.get(name.lower(), name)
    result: List[Course] = []
    for _, row in df.iterrows():
        credits = row.get(col("Credits"))
        try:
            credits_int: Optional[int] = int(credits) if str(credits).strip() != "" else None
        except Exception:
            credits_int = None
        result.append(
            Course(
                course_id=str(row.get(col("CourseID"), "")).strip(),
                course_name=str(row.get(col("CourseName"), "")).strip(),
                course_type=str(row.get(col("Type"), "Lecture") or "Lecture").strip(),
                credits=credits_int,
            )
        )
    return [c for c in result if c.course_id]


def load_timeslots_excel(path: str, sheet_name: Optional[str] = None) -> List[TimeSlot]:
    pd = _ensure_pandas()
    df = pd.read_excel(path, sheet_name=sheet_name)
    cols = {c.lower().strip(): c for c in df.columns}
    def col(name: str) -> str:
        return cols.get(name.lower(), name)
    timeslots: List[TimeSlot] = []
    for _, row in df.iterrows():
        day = str(row.get(col("Day"), "")).strip()
        start_time = str(row.get(col("StartTime"), "")).strip()
        end_time = str(row.get(col("EndTime"), "")).strip()
        if day and start_time and end_time:
            timeslots.append(TimeSlot(day=day, start_time=start_time, end_time=end_time))
    return timeslots
