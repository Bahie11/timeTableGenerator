"""
Data models for the timetable generator.
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class TimeSlot:
    day: str
    start_time: str
    end_time: str

    def label(self) -> str:
        return f"{self.day} {self.start_time}-{self.end_time}"


@dataclass(frozen=True)
class Room:
    room_id: str
    room_type: str  # "Lecture" or "Lab"
    capacity: int


@dataclass
class Instructor:
    instructor_id: str
    name: str
    role: str
    unavailable_day: Optional[str]  # e.g. "Monday" from "Not on Monday"
    qualified_courses: List[str]


@dataclass
class Course:
    course_id: str
    course_name: str
    course_type: str  # Lecture or Lab
    credits: Optional[int] = None


# Type alias for assignments
Assignment = tuple[int, str, str]  # (timeslot_index, room_id, course_code)
