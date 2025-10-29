"""
Constraint Satisfaction Problem (CSP) solver for timetable generation.
"""
from typing import Dict, List, Optional

try:
    from .models import Instructor, TimeSlot, Room, Assignment
except ImportError:
    from models import Instructor, TimeSlot, Room, Assignment


def build_domains(
    instructors: List[Instructor], timeslots: List[TimeSlot], rooms: List[Room]
) -> Dict[str, List[Assignment]]:
    """Build domains for CSP variables (instructors) with their possible assignments."""
    # Domain: all (timeslot, room, course) options that respect instructor availability
    lecture_rooms = [r for r in rooms if r.room_type.lower() == "lecture"]
    domains: Dict[str, List[Assignment]] = {}
    
    # Group timeslots by day for better distribution
    timeslots_by_day = {}
    for idx, ts in enumerate(timeslots):
        day = ts.day.lower()
        if day not in timeslots_by_day:
            timeslots_by_day[day] = []
        timeslots_by_day[day].append(idx)
    
    for instructor in instructors:
        allowed_slots: List[int] = []
        for idx, ts in enumerate(timeslots):
            if instructor.unavailable_day and ts.day.lower() == instructor.unavailable_day.lower():
                continue
            allowed_slots.append(idx)

        # Choose at least a placeholder course if none specified
        courses = instructor.qualified_courses or ["GEN101"]

        options: List[Assignment] = []
        
        # Ensure we have options from different days
        for day, day_slots in timeslots_by_day.items():
            # Filter day slots by instructor availability
            available_day_slots = [s for s in day_slots if s in allowed_slots]
            if available_day_slots:
                # Take a few slots from each day to ensure distribution
                for slot_index in available_day_slots[:3]:  # Limit to 3 slots per day
                    for room in lecture_rooms:
                        for course_code in courses:
                            options.append((slot_index, room.room_id, course_code))
        
        # If no day-specific options, fall back to all available slots
        if not options:
            for slot_index in allowed_slots:
                for room in lecture_rooms:
                    for course_code in courses:
                        options.append((slot_index, room.room_id, course_code))
        
        domains[instructor.instructor_id] = options
    return domains


def is_consistent(
    partial_assignment: Dict[str, Assignment],
    new_instructor_id: str,
    new_value: Assignment,
) -> bool:
    """Check if a new assignment is consistent with existing assignments."""
    # Hard constraints:
    # 1) No professor teaches more than one class at the same time (trivial here: one per instructor)
    # 2) No room hosts more than one class at the same time
    # 3) Instructor availability respected (enforced in domain construction)
    (new_slot, new_room, new_course) = new_value
    
    for other_instructor_id, (slot, room, course) in partial_assignment.items():
        # Room-time conflict: same room at same time
        if slot == new_slot and room == new_room:
            return False
        # Same course conflict: same course at same time (different instructors)
        if slot == new_slot and course == new_course:
            return False
    return True


def select_unassigned_variable(
    variables: List[str],
    assignment: Dict[str, Assignment],
    domains: Dict[str, List[Assignment]],
) -> str:
    """Select the next variable to assign using Minimum Remaining Values heuristic."""
    # Minimum Remaining Values heuristic to speed up backtracking
    unassigned = [v for v in variables if v not in assignment]
    return min(unassigned, key=lambda v: len(domains[v]))


def order_domain_values(var: str, domains: Dict[str, List[Assignment]]) -> List[Assignment]:
    """Order domain values for a variable to improve search efficiency."""
    # Order by day diversity to spread courses across all days
    assignments = domains[var]
    
    # Group by day to ensure diversity
    day_groups = {}
    for assignment in assignments:
        slot_index, room_id, course = assignment
        # We need to get the day from the timeslot, but we don't have access to timeslots here
        # So we'll use a simple round-robin approach
        day_groups.setdefault(slot_index % 5, []).append(assignment)
    
    # Interleave assignments from different days
    result = []
    max_len = max(len(group) for group in day_groups.values()) if day_groups else 0
    
    for i in range(max_len):
        for day_group in day_groups.values():
            if i < len(day_group):
                result.append(day_group[i])
    
    return result


def backtracking_search(domains: Dict[str, List[Assignment]]) -> Optional[Dict[str, Assignment]]:
    """Solve the CSP using backtracking search."""
    variables = list(domains.keys())

    def backtrack(current: Dict[str, Assignment]) -> Optional[Dict[str, Assignment]]:
        if len(current) == len(variables):
            return current

        var = select_unassigned_variable(variables, current, domains)
        for value in order_domain_values(var, domains):
            if is_consistent(current, var, value):
                current[var] = value
                result = backtrack(current)
                if result is not None:
                    return result
                del current[var]
        return None

    return backtrack({})


def generate_schedule_from_memory(
    instructors: List[Instructor], rooms: List[Room], timeslots: List[TimeSlot]
) -> tuple[Dict[str, Assignment], Dict[str, Instructor], List[TimeSlot]]:
    """Generate a schedule from in-memory data."""
    if not instructors:
        raise ValueError("No instructors available")
    if not rooms:
        raise ValueError("No rooms available")
    if not timeslots:
        raise ValueError("No timeslots available")

    domains = build_domains(instructors, timeslots, rooms)
    solution = backtracking_search(domains)
    if solution is None:
        raise RuntimeError("No feasible schedule found with current constraints.")

    instructors_by_id: Dict[str, Instructor] = {i.instructor_id: i for i in instructors}
    return solution, instructors_by_id, timeslots
