"""
CSP solver adjusted for the specific data structure from Excel files.
"""
import time
import logging
import copy
import os
from threading import Event
from typing import Dict, List, Optional, Tuple, Callable

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
        return ("classroom" in rt) or ("lecture" in rt)
    return True

def build_domains(instructors: List[Instructor], timeslots: List[TimeSlot], rooms: List[Room], courses: Optional[List[Course]] = None) -> Dict[str, List[Assignment]]:
    domains: Dict[str, List[Assignment]] = {}
    # build course lookup if provided (some code expects course metadata)
    course_lookup = {c.course_id: c for c in (courses or [])}
    for inst in instructors:
        dom: List[Assignment] = []
        # parse preferred like "Not on Tuesday"
        unavailable = None
        if inst.unavailable_day:
            t = inst.unavailable_day.strip()
            if t.lower().startswith("not on"):
                unavailable = t[6:].strip().lower()
            else:
                unavailable = t.lower()
        # qualified courses list is in inst.qualified_courses (list of codes)
        quals = [c.strip() for c in (inst.qualified_courses or []) if c and c.strip()]
        if not quals:
            # no qualified courses -> leave domain empty
            domains[inst.instructor_id] = dom
            continue
        for ti, ts in enumerate(timeslots):
            if unavailable and ((ts.day or "").strip().lower() == unavailable):
                continue
            for room in rooms:
                for course_code in quals:
                    # if we have course metadata check room type compatibility
                    course_meta = course_lookup.get(course_code)
                    course_type = course_meta.course_type if course_meta else None
                    if not _room_type_matches_course(room.room_type, course_type):
                        continue
                    dom.append((ti, room.room_id, course_code))
        domains[inst.instructor_id] = dom
    return domains

def greedy_search(
    domains: Dict[str, List[Assignment]],
    instructors_by_id: Dict[str, Instructor],
    timeslots: List[TimeSlot],
    stop_event: Optional[Event] = None,
    progress_callback: Optional[Callable[[int], None]] = None
) -> Optional[Dict[str, Assignment]]:
    """Fast greedy algorithm - assigns instructors quickly, accepts good-enough solutions"""
    import random
    
    if stop_event is None:
        stop_event = Event()
    
    assignment = {}
    used_slots = set()  # (time_idx, room_id) pairs already used
    nodes = 0
    
    # Sort instructors by domain size (smallest first - easier to place)
    instructors = sorted(domains.keys(), key=lambda x: len(domains[x]))
    
    for instructor_id in instructors:
        if stop_event.is_set():
            return None
            
        nodes += 1
        if progress_callback and nodes % 10 == 0:
            try:
                progress_callback(nodes)
            except Exception:
                pass
        
        # Try to find a valid assignment for this instructor
        available = domains[instructor_id]
        random.shuffle(available)  # Add some randomness for variety
        
        found = False
        for time_idx, room_id, course in available:
            slot_key = (time_idx, room_id)
            
            # Check if this slot is already used
            if slot_key not in used_slots:
                # Assign it!
                assignment[instructor_id] = (time_idx, room_id, course)
                used_slots.add(slot_key)
                found = True
                break
        
        if not found:
            # Can't place this instructor - that's okay, just skip them
            logging.warning(f"Could not schedule instructor {instructor_id}")
    
    logging.info(f"Greedy search completed: {len(assignment)}/{len(domains)} instructors scheduled")
    if progress_callback:
        try:
            progress_callback(nodes)
        except Exception:
            pass
    
    return assignment if assignment else None

def backtracking_search(
    domains: Dict[str, List[Assignment]],
    instructors_by_id: Dict[str, Instructor],
    timeslots: List[TimeSlot],
    max_nodes: int = 200_000,
    timeout: Optional[float] = 30.0,
    stop_event: Optional[Event] = None,
    progress_callback: Optional[Callable[[int], None]] = None
) -> Optional[Dict[str, Assignment]]:
    start_time = time.time()
    nodes = 0
    if stop_event is None:
        stop_event = Event()

    def consistent(assignment: Dict[str, Assignment], var: str, value: Assignment) -> bool:
        time_idx, room_id, course = value
        for other_var, other_value in assignment.items():
            ot, oroom, ocourse = other_value
            if ot == time_idx and oroom == room_id:
                return False
            if var == other_var and ot == time_idx:
                return False
        return True

    def select_mrv(curr_domains, assigned):
        unassigned = [v for v in curr_domains if v not in assigned]
        return min(unassigned, key=lambda v: len(curr_domains[v]))

    def order_values(var, curr_domains):
        def conflicts_count(val):
            t_idx, r_id, c = val
            cnt = 0
            for other, dom in curr_domains.items():
                if other == var: continue
                for v2 in dom:
                    if v2[0] == t_idx and v2[1] == r_id:
                        cnt += 1
            return cnt
        return sorted(curr_domains[var], key=conflicts_count)

    def forward_check(domains_local, var, val):
        new = copy.deepcopy(domains_local)
        t_idx, r_id, course_code = val
        new[var] = [val]
        for other in list(new.keys()):
            if other == var:
                continue
            reduced = []
            for v in new[other]:
                ot, oroom, ocourse = v
                if ot == t_idx and oroom == r_id:
                    continue
                reduced.append(v)
            if not reduced:
                return None
            new[other] = reduced
        return new

    def recurse(curr_domains, assignment):
        nonlocal nodes
        if stop_event.is_set():
            return None
        nodes += 1
        if progress_callback and nodes % 500 == 0:
            try:
                progress_callback(nodes)
            except Exception:
                pass
        if timeout and (time.time() - start_time) > timeout:
            logging.warning("Search timed out after %.2fs nodes=%d", time.time() - start_time, nodes)
            return None
        if nodes > max_nodes:
            logging.warning("Node limit reached nodes=%d", nodes)
            return None
        if len(assignment) == len(curr_domains):
            logging.info("Solution found nodes=%d time=%.2fs", nodes, time.time() - start_time)
            return assignment.copy()

        var = select_mrv(curr_domains, assignment)
        for value in order_values(var, curr_domains):
            if stop_event.is_set():
                return None
            if not consistent(assignment, var, value):
                continue
            reduced = forward_check(curr_domains, var, value)
            if reduced is None:
                continue
            assignment[var] = value
            res = recurse(reduced, assignment)
            if res:
                return res
            del assignment[var]
        return None

    logging.info("Starting backtracking_search (max_nodes=%d timeout=%s)", max_nodes, str(timeout))
    solution = recurse(domains, {})
    logging.info("Search finished nodes=%d elapsed=%.2fs result=%s", nodes, time.time() - start_time, "FOUND" if solution else "NONE")
    if progress_callback:
        try:
            progress_callback(nodes)
        except Exception:
            pass
    return solution

def generate_schedule_from_memory(
    instructors: List[Instructor],
    rooms: List[Room],
    timeslots: List[TimeSlot],
    courses: Optional[List[Course]] = None,
    stop_event: Optional[Event] = None,
    progress_callback: Optional[Callable[[int], None]] = None,
    use_fast_mode: bool = True
) -> Tuple[Dict[str, Assignment], Dict[str, Instructor], List[TimeSlot]]:
    """
    Generate timetable schedule.
    
    Args:
        use_fast_mode: If True, uses fast greedy algorithm (default).
                      If False, uses slower but more thorough backtracking.
    """
    logging.info("generate_schedule_from_memory start: instructors=%d rooms=%d timeslots=%d (fast_mode=%s)",
                 len(instructors), len(rooms), len(timeslots), use_fast_mode)
    domains = build_domains(instructors, timeslots, rooms, courses=courses)
    sizes = {v: len(dom) for v, dom in domains.items()}
    empty = [v for v, dom in domains.items() if not dom]
    
    # Just warn about empty domains, don't stop
    if empty:
        logging.warning("Instructors with no available slots: %s", empty)
        logging.warning("These %d instructor(s) will be skipped in the schedule", len(empty))
    
    instructors_by_id = {inst.instructor_id: inst for inst in instructors}
    
    if use_fast_mode:
        # Use fast greedy algorithm - completes in seconds
        logging.info("Using FAST GREEDY mode for quick scheduling")
        result = greedy_search(domains, instructors_by_id, timeslots, stop_event=stop_event, progress_callback=progress_callback)
    else:
        # Use slow but thorough backtracking - may take minutes
        logging.info("Using THOROUGH BACKTRACKING mode (slower)")
        result = backtracking_search(domains, instructors_by_id, timeslots, stop_event=stop_event, progress_callback=progress_callback)
    
    return result or {}, instructors_by_id, timeslots
