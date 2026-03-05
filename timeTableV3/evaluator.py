from typing import Dict, Tuple, Any
import statistics

def parse_time_str(t: str):
    # try to extract hour as integer from formats like '09:00' or '9:00 AM'
    if not isinstance(t, str):
        return None
    t = t.strip()
    if t == '':
        return None
    try:
        if 'AM' in t.upper() or 'PM' in t.upper():
            parts = t.split()
            hhmm = parts[0]
        else:
            hhmm = t
        hh = int(hhmm.split(':')[0])
        return hh
    except Exception:
        return None


def evaluate(assignment: Dict[Tuple[str,str,int], Tuple[str,str,str]], data) -> Dict[str,Any]:
    # returns metrics and soft-constraint penalties
    metrics = {}
    metrics['num_assigned'] = len(assignment)
    # early/late penalty
    early_late = 0
    # instructor consecutive different room penalty
    instr_penalty = 0
    # distribution penalty per course
    course_days = {}

    # build per-instructor schedule
    instr_sched = {}
    for var, val in assignment.items():
        cid, sid, sess = var
        tid, rid, iid = val
        timeslot = data['timeslots'].get(tid, {})
        day = timeslot.get('day','')
        start = timeslot.get('start','')
        hh = parse_time_str(start)
        if hh is not None and (hh < 9 or hh > 17):
            early_late += 1
        course_days.setdefault(cid, []).append(day)
        instr_sched.setdefault(iid, []).append((day, start, rid))

    # instructor consecutive room penalty: for each instructor, sort by day/start and penalize when consecutive assignments have different room
    for iid, slots in instr_sched.items():
        # naive sorting
        slots_sorted = sorted(slots, key=lambda x: (x[0], x[1]))
        for a,b in zip(slots_sorted, slots_sorted[1:]):
            # if same day and start times adjacent-ish (not rigorous), penalize if rooms differ
            if a[0] == b[0] and a[2] != b[2]:
                instr_penalty += 1

    distrib_penalty = 0
    for cid, days in course_days.items():
        # penalize if all sessions are on the same day
        if len(set(days)) <= 1 and len(days) > 1:
            distrib_penalty += 1

    total_soft = early_late + instr_penalty + distrib_penalty
    metrics['soft_early_late'] = early_late
    metrics['soft_instructor_consecutive_room'] = instr_penalty
    metrics['soft_distribution'] = distrib_penalty
    metrics['soft_total'] = total_soft
    return metrics
