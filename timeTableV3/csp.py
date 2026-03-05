from typing import Dict, Tuple, List, Any, Optional
import copy

# Variable key: (course_id, section_id, session_index)
Assignment = Dict[Tuple[str, str, int], Tuple[str, str, str]]  # -> (timeslot_id, room_id, instructor_id)


def feasible(assignment: Assignment, var: Tuple[str, str, int], value: Tuple[str, str, str], data) -> bool:
    timeslot, room, instr = value
    course_id, section_id, _ = var
    course = data['courses'][course_id]
    # room exists
    if room not in data['rooms']:
        return False
    room_obj = data['rooms'][room]
    # room capacity
    if course.get('students', 0) > room_obj.get('capacity', 0):
        return False
    # room type matches course type (hard constraint)
    if course.get('type') and room_obj.get('type') and course['type'].lower() not in room_obj.get('type', '').lower():
        return False
    # instructor must be qualified for the course if qualifications provided
    if instr:
        instr_obj = data['instructors'].get(instr)
        if instr_obj and instr_obj.get('qualified'):
            quals = instr_obj.get('qualified')
            if course_id not in quals and course.get('name') not in quals:
                # not qualified
                return False
        # instructor availability
        if instr_obj and timeslot in instr_obj.get('unavailable', []):
            return False
    # no double-booking for room or instructor at same timeslot
    for ov, oval in assignment.items():
        ot, oroom, oinstr = oval
        if ot == timeslot:
            if oroom == room:
                return False
            if instr and oinstr == instr:
                return False
    return True


def domain_for(var: Tuple[str, str, int], data) -> List[Tuple[str, str, str]]:
    course_id, section_id, _ = var
    course = data['courses'][course_id]
    domains = []
    for t in data['timeslots'].keys():
        for r in data['rooms'].keys():
            # try all instructors that are either explicitly assigned (course may have instructor) or any qualified
            if course.get('instructor'):
                instrs = [course.get('instructor')]
            else:
                instrs = []
                for iid, iobj in data['instructors'].items():
                    quals = iobj.get('qualified')
                    if not quals or course_id in quals or course.get('name') in quals:
                        instrs.append(iid)
            for instr in instrs:
                domains.append((t, r, instr))
    return domains


def select_unassigned_var(vars_list: List[Tuple[str, str, int]], assignment: Assignment, data) -> Optional[Tuple[str, str, int]]:
    best = None
    best_domain_size = None
    for v in vars_list:
        if v in assignment:
            continue
        domain = [val for val in domain_for(v, data) if feasible(assignment, v, val, data)]
        size = len(domain)
        if best is None or (size < best_domain_size):
            best = v
            best_domain_size = size
    return best


def order_domain_values(var, assignment, data) -> List[Tuple[str, str, str]]:
    domain = domain_for(var, data)
    course = data['courses'][var[0]]

    def score(val):
        _, r, _ = val
        # prefer rooms that fit closely
        return data['rooms'][r]['capacity'] - course.get('students', 0)

    domain = [d for d in domain if feasible(assignment, var, d, data)]
    return sorted(domain, key=score)


def backtrack(assignment: Assignment, vars_list: List[Tuple[str, str, int]], data, best: Optional[Assignment] = None, nodes=[0]) -> Optional[Assignment]:
    nodes[0] += 1
    if len(assignment) == len(vars_list):
        return copy.deepcopy(assignment)
    var = select_unassigned_var(vars_list, assignment, data)
    if var is None:
        return None
    for value in order_domain_values(var, assignment, data):
        if feasible(assignment, var, value, data):
            assignment[var] = value
            result = backtrack(assignment, vars_list, data, best, nodes)
            if result is not None:
                return result
            del assignment[var]
    return None


def generate_vars(data) -> List[Tuple[str, str, int]]:
    vars = []
    # if sections provided, create variables per (course, section), else use a default section 'S1'
    sections = data.get('sections') or {'S1': {'id': 'S1'}}
    for cid, c in data['courses'].items():
        sessions = c.get('sessions_per_week', 1)
        for sid in sections.keys():
            for i in range(sessions):
                vars.append((cid, sid, i))
    return vars


def solve(data, timeout_seconds: Optional[int] = None) -> Optional[Assignment]:
    vars_list = generate_vars(data)
    assignment: Assignment = {}
    nodes = [0]
    sol = backtrack(assignment, vars_list, data, None, nodes)
    return sol