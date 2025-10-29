"""
FIXED CSP solver - Supports multiple classes per instructor
Each instructor can teach multiple courses at different times
"""
import time
import logging
import copy
import os
from threading import Event
from typing import Dict, List, Optional, Tuple, Callable
from collections import defaultdict

from models import Instructor, TimeSlot, Room, Course, Assignment

_log_path = os.path.join(os.path.dirname(__file__), "timetable.log")
logging.basicConfig(filename=_log_path, level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s")

def _room_type_matches_course(room_type: Optional[str], course_type: Optional[str]) -> bool:
    if not room_type or not course_type:
        return True
    rt = room_type.lower()
    ct = course_type.lower()
    if "lab" in ct:
        return ("lab" in rt) or ("computer" in rt)
    if "lecture" in ct:
        return ("classroom" in rt) or ("lecture" in rt) or ("hall" in rt) or ("theater" in rt)
    return True


def build_course_assignments(
    instructors: List[Instructor],
    timeslots: List[TimeSlot],
    rooms: List[Room],
    courses: Optional[List[Course]] = None
) -> List[Tuple[str, str, List[Assignment]]]:
    """
    Build assignments where each (instructor, course) pair needs a slot.
    
    Returns:
        List of (instructor_id, course_id, possible_assignments)
    """
    course_lookup = {c.course_id: c for c in (courses or [])}
    assignments_to_make = []
    
    for inst in instructors:
        # Parse unavailability
        unavailable = None
        if inst.unavailable_day:
            t = inst.unavailable_day.strip()
            if t.lower().startswith("not on"):
                unavailable = t[6:].strip().lower()
            else:
                unavailable = t.lower()
        
        # Get qualified courses
        quals = [c.strip() for c in (inst.qualified_courses or []) if c and c.strip()]
        
        for course_code in quals:
            # Build domain for this (instructor, course) pair
            domain = []
            
            for ti, ts in enumerate(timeslots):
                # Skip unavailable days
                if unavailable and ((ts.day or "").strip().lower() == unavailable):
                    continue
                
                for room in rooms:
                    # Check room-course compatibility
                    course_meta = course_lookup.get(course_code)
                    course_type = course_meta.course_type if course_meta else None
                    
                    if not _room_type_matches_course(room.room_type, course_type):
                        continue
                    
                    domain.append((ti, room.room_id, course_code))
            
            if domain:  # Only add if there are valid options
                assignments_to_make.append((inst.instructor_id, course_code, domain))
    
    return assignments_to_make


def greedy_search_multi(
    instructors: List[Instructor],
    timeslots: List[TimeSlot],
    rooms: List[Room],
    courses: Optional[List[Course]] = None,
    stop_event: Optional[Event] = None,
    progress_callback: Optional[Callable[[int], None]] = None
) -> Optional[List[Tuple[str, int, str, str]]]:
    """
    Fast greedy algorithm that assigns MULTIPLE classes per instructor.
    
    Returns:
        List of (instructor_id, timeslot_idx, room_id, course_id) assignments
    """
    import random
    
    if stop_event is None:
        stop_event = Event()
    
    # Build all (instructor, course) pairs that need scheduling
    assignments_to_make = build_course_assignments(instructors, timeslots, rooms, courses)
    
    logging.info(f"Greedy search: {len(assignments_to_make)} (instructor, course) pairs to schedule")
    
    # Track what's been assigned
    result = []
    used_slots = set()  # (time_idx, room_id) pairs already used
    instructor_times = defaultdict(set)  # instructor_id -> set of time_idx used
    nodes = 0
    
    # Sort by domain size (most constrained first)
    assignments_to_make.sort(key=lambda x: len(x[2]))
    
    for instructor_id, course_id, domain in assignments_to_make:
        if stop_event.is_set():
            return None
        
        nodes += 1
        if progress_callback and nodes % 10 == 0:
            try:
                progress_callback(nodes)
            except Exception:
                pass
        
        # Shuffle domain for variety
        available = list(domain)
        random.shuffle(available)
        
        # Try to find a valid slot
        found = False
        for time_idx, room_id, course_code in available:
            slot_key = (time_idx, room_id)
            
            # Check conflicts:
            # 1. Room-time conflict (room already used at this time)
            if slot_key in used_slots:
                continue
            
            # 2. Instructor-time conflict (instructor already teaching at this time)
            if time_idx in instructor_times[instructor_id]:
                continue
            
            # Valid assignment found!
            result.append((instructor_id, time_idx, room_id, course_code))
            used_slots.add(slot_key)
            instructor_times[instructor_id].add(time_idx)
            found = True
            break
        
        if not found:
            logging.warning(f"Could not schedule {instructor_id} for course {course_id}")
    
    logging.info(f"Greedy search completed: {len(result)} classes scheduled from {len(assignments_to_make)} needed")
    
    if progress_callback:
        try:
            progress_callback(nodes)
        except Exception:
            pass
    
    return result if result else None


def generate_schedule_fixed(
    instructors: List[Instructor],
    rooms: List[Room],
    timeslots: List[TimeSlot],
    courses: Optional[List[Course]] = None,
    stop_event: Optional[Event] = None,
    progress_callback: Optional[Callable[[int], None]] = None
) -> Tuple[List[Tuple[str, int, str, str]], Dict[str, Instructor], List[TimeSlot]]:
    """
    Generate timetable with FIXED algorithm that supports multiple classes per instructor.
    
    Returns:
        Tuple of (assignments list, instructors by ID, timeslots)
        where assignments is List of (instructor_id, timeslot_idx, room_id, course_id)
    """
    logging.info(f"Fixed scheduler starting: {len(instructors)} instructors, {len(rooms)} rooms, {len(timeslots)} timeslots")
    
    instructors_by_id = {inst.instructor_id: inst for inst in instructors}
    
    # Run the fixed greedy search
    result = greedy_search_multi(
        instructors,
        timeslots,
        rooms,
        courses=courses,
        stop_event=stop_event,
        progress_callback=progress_callback
    )
    
    if result:
        logging.info(f"✅ Successfully scheduled {len(result)} classes")
        
        # Count classes per instructor
        classes_per_instructor = defaultdict(int)
        for instructor_id, _, _, _ in result:
            classes_per_instructor[instructor_id] += 1
        
        logging.info(f"Classes per instructor: {dict(classes_per_instructor)}")
    else:
        logging.warning("❌ No solution found")
    
    return result or [], instructors_by_id, timeslots

