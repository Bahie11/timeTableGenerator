"""
Enhanced CSP solver with improved scheduling strategies.
Incorporates randomization, room distribution, and smarter assignment logic.
"""
import time
import logging
import random
from threading import Event
from typing import Dict, List, Optional, Tuple, Callable
from collections import defaultdict

from models import Instructor, TimeSlot, Room, Course, Assignment

logger = logging.getLogger(__name__)


def _room_type_matches_course(room_type: Optional[str], course_type: Optional[str]) -> bool:
    """Check if room type is compatible with course type"""
    if not room_type or not course_type:
        return True
    rt = room_type.lower()
    ct = course_type.lower()
    if "lab" in ct:
        return ("lab" in rt) or ("computer" in rt)
    if "lecture" in ct:
        return ("classroom" in rt) or ("lecture" in rt) or ("hall" in rt) or ("theater" in rt)
    return True


def _is_large_lecture_room(room: Room) -> bool:
    """Check if room is a large lecture hall"""
    if room.capacity and room.capacity >= 75:
        room_type_lower = (room.room_type or "").lower()
        if "lab" not in room_type_lower:
            return True
    return False


def _is_premium_room(room: Room) -> bool:
    """Check if room is a premium space (Hall, Theater) that should be used sparingly"""
    room_id_lower = room.room_id.lower()
    room_type_lower = (room.room_type or "").lower()
    return "hall" in room_id_lower or "theater" in room_type_lower or "auditorium" in room_type_lower


def build_enhanced_domains(
    instructors: List[Instructor],
    timeslots: List[TimeSlot],
    rooms: List[Room],
    courses: Optional[List[Course]] = None
) -> Dict[str, List[Assignment]]:
    """
    Build domains with enhanced logic:
    - Respects instructor availability
    - Matches room types to course types
    - Creates multiple options per instructor
    """
    domains: Dict[str, List[Assignment]] = {}
    course_lookup = {c.course_id: c for c in (courses or [])}
    
    for inst in instructors:
        dom: List[Assignment] = []
        
        # Parse unavailability
        unavailable_day = None
        if inst.unavailable_day:
            t = inst.unavailable_day.strip()
            if t.lower().startswith("not on"):
                unavailable_day = t[6:].strip().lower()
            else:
                unavailable_day = t.lower()
        
        # Get qualified courses
        quals = [c.strip() for c in (inst.qualified_courses or []) if c and c.strip()]
        if not quals:
            domains[inst.instructor_id] = dom
            continue
        
        # Build all possible assignments for this instructor
        for ti, ts in enumerate(timeslots):
            # Skip unavailable days
            if unavailable_day and ((ts.day or "").strip().lower() == unavailable_day):
                continue
            
            for room in rooms:
                for course_code in quals:
                    # Check room-course compatibility
                    course_meta = course_lookup.get(course_code)
                    course_type = course_meta.course_type if course_meta else None
                    
                    if not _room_type_matches_course(room.room_type, course_type):
                        continue
                    
                    dom.append((ti, room.room_id, course_code))
        
        domains[inst.instructor_id] = dom
    
    return domains


def balanced_greedy_search(
    domains: Dict[str, List[Assignment]],
    instructors_by_id: Dict[str, Instructor],
    timeslots: List[TimeSlot],
    rooms_by_id: Dict[str, Room],
    stop_event: Optional[Event] = None,
    progress_callback: Optional[Callable[[int], None]] = None,
    randomize: bool = True
) -> Optional[Dict[str, Assignment]]:
    """
    Enhanced greedy algorithm with balanced room and day distribution.
    
    Features:
    - Randomizes assignment order for fairness
    - Tracks room usage to distribute load
    - Avoids overusing premium rooms (Hall, Theater)
    - Spreads classes across days
    - Prioritizes hard-to-schedule instructors
    """
    if stop_event is None:
        stop_event = Event()
    
    assignment = {}
    used_slots = set()  # (time_idx, room_id) pairs already used
    room_usage = defaultdict(int)  # Track how often each room is used
    day_usage = defaultdict(int)  # Track classes per day
    nodes = 0
    
    # Sort instructors by domain size (smallest first - most constrained)
    instructors_list = list(domains.keys())
    instructors_list.sort(key=lambda x: len(domains[x]))
    
    logger.info(f"Starting balanced greedy search for {len(instructors_list)} instructors")
    
    for instructor_id in instructors_list:
        if stop_event.is_set():
            logger.info("Search cancelled by user")
            return None
        
        nodes += 1
        if progress_callback and nodes % 10 == 0:
            try:
                progress_callback(nodes)
            except Exception:
                pass
        
        # Get available assignments for this instructor
        available = list(domains[instructor_id])
        
        if not available:
            logger.warning(f"No available slots for instructor {instructor_id}")
            continue
        
        # Shuffle for randomness and fairness
        if randomize:
            random.shuffle(available)
        
        # Sort by preference (avoid premium rooms, balance days)
        def assignment_score(assignment_tuple):
            """Lower score = better assignment"""
            time_idx, room_id, course = assignment_tuple
            slot_key = (time_idx, room_id)
            
            # Skip if slot already used
            if slot_key in used_slots:
                return 999999
            
            room = rooms_by_id.get(room_id)
            ts = timeslots[time_idx]
            
            score = 0
            
            # Penalize premium rooms heavily to save them
            if room and _is_premium_room(room):
                score += 50
            
            # Prefer less-used rooms
            score += room_usage[room_id] * 3
            
            # Prefer less-busy days
            day = ts.day if ts else ""
            score += day_usage[day] * 2
            
            # Add some randomness for variety
            if randomize:
                score += random.uniform(0, 5)
            
            return score
        
        # Sort available assignments by score
        available.sort(key=assignment_score)
        
        # Try to assign the best available slot
        found = False
        for time_idx, room_id, course in available:
            slot_key = (time_idx, room_id)
            
            # Check if this slot is already used
            if slot_key not in used_slots:
                # Assign it!
                assignment[instructor_id] = (time_idx, room_id, course)
                used_slots.add(slot_key)
                
                # Update usage tracking
                room_usage[room_id] += 1
                ts = timeslots[time_idx]
                if ts:
                    day_usage[ts.day] += 1
                
                found = True
                logger.debug(f"Assigned instructor {instructor_id} to {room_id} at slot {time_idx}")
                break
        
        if not found:
            logger.warning(f"Could not schedule instructor {instructor_id} - all slots occupied")
    
    logger.info(f"Balanced greedy search completed: {len(assignment)}/{len(domains)} instructors scheduled")
    logger.info(f"Room usage distribution: {dict(sorted(room_usage.items(), key=lambda x: x[1], reverse=True)[:10])}")
    logger.info(f"Day distribution: {dict(day_usage)}")
    
    if progress_callback:
        try:
            progress_callback(nodes)
        except Exception:
            pass
    
    return assignment if assignment else None


def smart_backtracking_search(
    domains: Dict[str, List[Assignment]],
    instructors_by_id: Dict[str, Instructor],
    timeslots: List[TimeSlot],
    rooms_by_id: Dict[str, Room],
    max_nodes: int = 200_000,
    timeout: Optional[float] = 30.0,
    stop_event: Optional[Event] = None,
    progress_callback: Optional[Callable[[int], None]] = None
) -> Optional[Dict[str, Assignment]]:
    """
    Enhanced backtracking with forward checking and intelligent heuristics.
    More thorough than greedy but slower.
    """
    start_time = time.time()
    nodes = 0
    if stop_event is None:
        stop_event = Event()
    
    room_usage = defaultdict(int)
    day_usage = defaultdict(int)
    
    def consistent(current_assignment: Dict[str, Assignment], var: str, value: Assignment) -> bool:
        """Check if assignment is consistent with current state"""
        time_idx, room_id, course = value
        for other_var, other_value in current_assignment.items():
            ot, oroom, ocourse = other_value
            # Room conflict at same time
            if ot == time_idx and oroom == room_id:
                return False
            # Instructor already assigned at this time (shouldn't happen with our domain model)
            if var == other_var and ot == time_idx:
                return False
        return True
    
    def select_variable(curr_domains, assigned):
        """Select most constrained variable (MRV heuristic)"""
        unassigned = [v for v in curr_domains if v not in assigned]
        if not unassigned:
            return None
        return min(unassigned, key=lambda v: len(curr_domains[v]))
    
    def order_values(var, curr_assignment):
        """Order values by least constraining"""
        values = list(domains[var])
        
        # Filter out inconsistent values
        values = [v for v in values if consistent(curr_assignment, var, v)]
        
        def value_score(val):
            """Lower = better"""
            time_idx, room_id, course = val
            room = rooms_by_id.get(room_id)
            ts = timeslots[time_idx]
            
            score = 0
            # Avoid premium rooms
            if room and _is_premium_room(room):
                score += 30
            # Balance room usage
            score += room_usage[room_id] * 2
            # Balance day usage
            if ts:
                score += day_usage[ts.day]
            
            return score
        
        values.sort(key=value_score)
        return values
    
    def recurse(curr_assignment):
        nonlocal nodes
        
        if stop_event.is_set():
            return None
        
        nodes += 1
        if progress_callback and nodes % 500 == 0:
            try:
                progress_callback(nodes)
            except Exception:
                pass
        
        # Check limits
        if timeout and (time.time() - start_time) > timeout:
            logger.warning(f"Search timed out after {time.time() - start_time:.2f}s, nodes={nodes}")
            return None
        
        if nodes > max_nodes:
            logger.warning(f"Node limit reached: {nodes}")
            return None
        
        # Check if complete
        if len(curr_assignment) == len(domains):
            logger.info(f"Solution found! nodes={nodes}, time={time.time() - start_time:.2f}s")
            return curr_assignment.copy()
        
        # Select next variable
        var = select_variable(domains, curr_assignment)
        if var is None:
            return curr_assignment.copy() if curr_assignment else None
        
        # Try each value
        for value in order_values(var, curr_assignment):
            if stop_event.is_set():
                return None
            
            if not consistent(curr_assignment, var, value):
                continue
            
            # Make assignment
            time_idx, room_id, course = value
            curr_assignment[var] = value
            
            # Update tracking
            room_usage[room_id] += 1
            ts = timeslots[time_idx]
            if ts:
                day_usage[ts.day] += 1
            
            # Recurse
            result = recurse(curr_assignment)
            if result:
                return result
            
            # Backtrack
            del curr_assignment[var]
            room_usage[room_id] -= 1
            if ts:
                day_usage[ts.day] -= 1
        
        return None
    
    logger.info(f"Starting smart backtracking (max_nodes={max_nodes}, timeout={timeout})")
    solution = recurse({})
    logger.info(f"Search finished: nodes={nodes}, time={time.time() - start_time:.2f}s, result={'FOUND' if solution else 'NONE'}")
    
    if progress_callback:
        try:
            progress_callback(nodes)
        except Exception:
            pass
    
    return solution


def generate_schedule_enhanced(
    instructors: List[Instructor],
    rooms: List[Room],
    timeslots: List[TimeSlot],
    courses: Optional[List[Course]] = None,
    stop_event: Optional[Event] = None,
    progress_callback: Optional[Callable[[int], None]] = None,
    use_fast_mode: bool = True,
    randomize: bool = True
) -> Tuple[Dict[str, Assignment], Dict[str, Instructor], List[TimeSlot]]:
    """
    Generate timetable with enhanced CSP algorithm.
    
    Args:
        instructors: List of instructors
        rooms: List of rooms
        timeslots: List of time slots
        courses: Optional list of courses for metadata
        stop_event: Event to signal cancellation
        progress_callback: Callback for progress updates
        use_fast_mode: If True, uses balanced greedy (fast). If False, uses smart backtracking (slow but thorough)
        randomize: Add randomization for better distribution
    
    Returns:
        Tuple of (solution dict, instructors by ID, timeslots)
    """
    logger.info(f"Enhanced scheduler starting: {len(instructors)} instructors, {len(rooms)} rooms, {len(timeslots)} timeslots")
    logger.info(f"Mode: {'FAST (Balanced Greedy)' if use_fast_mode else 'THOROUGH (Smart Backtracking)'}")
    
    # Build domains
    domains = build_enhanced_domains(instructors, timeslots, rooms, courses=courses)
    
    # Check for empty domains
    empty = [v for v, dom in domains.items() if not dom]
    if empty:
        logger.warning(f"{len(empty)} instructors have no available slots and will be skipped")
        logger.debug(f"Instructors with empty domains: {empty}")
    
    # Build lookup dictionaries
    instructors_by_id = {inst.instructor_id: inst for inst in instructors}
    rooms_by_id = {room.room_id: room for room in rooms}
    
    # Run appropriate algorithm
    if use_fast_mode:
        logger.info("Using BALANCED GREEDY algorithm (fast, good distribution)")
        result = balanced_greedy_search(
            domains,
            instructors_by_id,
            timeslots,
            rooms_by_id,
            stop_event=stop_event,
            progress_callback=progress_callback,
            randomize=randomize
        )
    else:
        logger.info("Using SMART BACKTRACKING algorithm (slower, more thorough)")
        result = smart_backtracking_search(
            domains,
            instructors_by_id,
            timeslots,
            rooms_by_id,
            stop_event=stop_event,
            progress_callback=progress_callback
        )
    
    if result:
        logger.info(f"✅ Successfully scheduled {len(result)}/{len(instructors)} instructors")
    else:
        logger.warning("❌ No solution found")
    
    return result or {}, instructors_by_id, timeslots

