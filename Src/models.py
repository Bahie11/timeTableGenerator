"""
Data models for the timetable generator.
"""
from dataclasses import dataclass, field
from typing import List, Optional
import datetime


@dataclass(frozen=True)
class TimeSlot:
    day: str
    start_time: Optional[datetime.time] = None
    end_time: Optional[datetime.time] = None

    def label(self) -> str:
        return f"{self.day} {self.start_time}-{self.end_time}"


@dataclass(frozen=True)
class Room:
    room_id: str
    room_type: Optional[str] = None
    capacity: Optional[int] = None


@dataclass
class Instructor:
    instructor_id: str
    name: Optional[str] = None
    unavailable_day: Optional[str] = None  # e.g. "Tuesday" or "Not on Tuesday"
    qualified_courses: List[str] = field(default_factory=list)


@dataclass
class Course:
    course_id: str
    course_name: Optional[str] = None
    course_type: Optional[str] = None
    credits: Optional[int] = None


# Type alias for assignments (timeslot index, room id, course id)
Assignment = tuple[int, str, str]
