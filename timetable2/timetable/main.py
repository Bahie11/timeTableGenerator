import csv
import argparse
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


# -----------------------------
# Data models
# -----------------------------


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
class Section:
    section_id: str
    semester: int
    student_count: int

@dataclass
class Course:
    course_id: str
    course_name: str
    course_type: str  # Lecture or Lab
    credits: int  # Required for lecture count per week
    sections: List[Section] = field(default_factory=list)


# -----------------------------
# CSV loading utilities
# -----------------------------


def load_timeslots(csv_path: str) -> List[TimeSlot]:
    timeslots: List[TimeSlot] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            day_raw = row.get("Day", "").strip()
            day = normalize_day(day_raw)
            timeslots.append(
                TimeSlot(day=day, start_time=row["StartTime"].strip(), end_time=row["EndTime"].strip())
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


# ---------- Optional Excel import (requires pandas + openpyxl) ----------
def _ensure_pandas():
    try:
        import pandas as pd  # Correctly import Pandas
        return pd
    except Exception as exc:
        raise ImportError(
            "Excel import requires pandas (and openpyxl). Install via: pip install pandas openpyxl"
        ) from exc


def load_instructors_excel(path: str, sheet_name: Optional[str] = None) -> List[Instructor]:
    pd = _ensure_pandas()
    try:
        df = pd.read_excel(path, sheet_name=sheet_name)  # Ensure this reads an Excel file into a DataFrame
        print(f"Loaded data type: {type(df)}")  # Debugging statement
        if not isinstance(df, pd.DataFrame):  # Validate the type
            raise ValueError(f"Expected a Pandas DataFrame, but got {type(df)}. Check the file format.")
    except Exception as e:
        raise ValueError(f"Error loading Excel file: {str(e)}. Ensure the file is a valid Excel format.")
    
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
        day_raw = str(row.get(col("Day"), "")).strip()
        day = normalize_day(day_raw)
        start_time = str(row.get(col("StartTime"), "")).strip()
        end_time = str(row.get(col("EndTime"), "")).strip()
        if day and start_time and end_time:
            timeslots.append(TimeSlot(day=day, start_time=start_time, end_time=end_time))
    return timeslots


def parse_unavailable_day(preferred_slots_value: str) -> Optional[str]:
    value = (preferred_slots_value or "").strip()
    # Expected like: "Not on Monday" or "Not on Mon"
    if value.lower().startswith("not on "):
        day_part = value.split(" ", 2)[-1].strip()
        return normalize_day(day_part) if day_part else None
    return None


def parse_qualified_courses(csv_value: str) -> List[str]:
    if not csv_value:
        return []
    # Split by comma and strip whitespace
    parts = [p.strip() for p in str(csv_value).split(",")]
    return [p for p in parts if p]


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


# -----------------------------
# CSP Model (simple)
# -----------------------------


Assignment = Tuple[int, str, str]  # (timeslot_index, room_id, course_code)


def is_consistent(
    partial_assignment: Dict[str, Assignment],
    new_instructor_id: str,
    new_value: Assignment,
) -> bool:
    """Check if assignment satisfies hard constraints."""
    (new_slot, new_room, new_course) = new_value
    
    # Hard Constraints:
    for other_id, (slot, room, course) in partial_assignment.items():
        # 1. No professor teaches more than one class at same time
        if slot == new_slot and other_id == new_instructor_id:
            return False
            
        # 2. No room hosts more than one class at same time
        if slot == new_slot and room == new_room:
            return False
            
        # 3. Room type must match course type
        if not is_room_type_compatible(room, new_course):
            return False
            
    return True

def is_room_type_compatible(room_id: str, course_id: str) -> bool:
    """Check if room type matches course type (lab/lecture)."""
    room = next((r for r in rooms if r.room_id == room_id), None)
    course = next((c for c in courses if c.course_id == course_id), None)
    
    if not room or not course:
        return False
        
    # Lab courses must be in lab rooms
    if course.course_type.lower() == "lab":
        return room.room_type.lower() == "lab"
    
    # Lectures can be in lecture rooms
    return room.room_type.lower() == "lecture"

def build_domains(
    instructors: List[Instructor],
    timeslots: List[TimeSlot],
    rooms: List[Room],
    sections: List[Section]
) -> Dict[str, List[Assignment]]:
    """Build domain values considering sections and room types."""
    domains: Dict[str, List[Assignment]] = {}
    
    for instructor in instructors:
        allowed_slots: List[int] = []
        for idx, ts in enumerate(timeslots):
            # Skip instructor's unavailable day
            if instructor.unavailable_day and ts.day.lower() == instructor.unavailable_day.lower():
                continue
                
            # Soft constraint: Avoid early morning/late evening
            hour = int(ts.start_time.split(":")[0])
            if 8 <= hour <= 17:  # 8 AM to 5 PM preferred
                allowed_slots.append(idx)
                
        courses = instructor.qualified_courses or ["GEN101"]
        options: List[Assignment] = []
        
        for slot_index in allowed_slots:
            ts = timeslots[slot_index]
            
            # Group nearby rooms for consecutive classes
            compatible_rooms = get_compatible_rooms(rooms, courses[0])
            
            for room in compatible_rooms:
                for course_code in courses[:1]:
                    options.append((slot_index, room.room_id, course_code))
                    
        domains[instructor.instructor_id] = options
    return domains

def get_compatible_rooms(rooms: List[Room], course_id: str) -> List[Room]:
    """Get rooms compatible with course type and sorted by proximity."""
    course = next((c for c in courses if c.course_id == course_id), None)
    if not course:
        return rooms
        
    # Filter rooms by type compatibility
    compatible = [
        r for r in rooms 
        if (course.course_type.lower() == "lab" and r.room_type.lower() == "lab") or
           (course.course_type.lower() == "lecture" and r.room_type.lower() == "lecture")
    ]
    
    # Sort rooms by proximity (assuming room numbers indicate location)
    return sorted(compatible, key=lambda r: r.room_id)

def backtracking_search(domains: Dict[str, List[Assignment]]) -> Optional[Dict[str, Assignment]]:
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


# -----------------------------
# Output utilities
# -----------------------------


def write_schedule_csv(
    output_path: str,
    solution: Dict[str, Assignment],
    instructors_by_id: Dict[str, Instructor],
    timeslots: List[TimeSlot],
):
    fieldnames = [
        "InstructorID",
        "Name",
        "Day",
        "StartTime",
        "EndTime",
        "RoomID",
        "Course",
    ]
    try:
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for instructor_id, (slot_index, room_id, course) in solution.items():
                instructor = instructors_by_id[instructor_id]
                ts = timeslots[slot_index]
                writer.writerow(
                    {
                        "InstructorID": instructor.instructor_id,
                        "Name": instructor.name,
                        "Day": ts.day,
                        "StartTime": ts.start_time,
                        "EndTime": ts.end_time,
                        "RoomID": room_id,
                        "Course": course,
                    }
                )
    except Exception as e:
        raise Exception(f"Error writing CSV file: {str(e)}")


def print_schedule(solution: Dict[str, Assignment], instructors_by_id: Dict[str, Instructor], timeslots: List[TimeSlot]):
    rows: List[Tuple[str, str, str, str, str, str]] = []
    for instructor_id, (slot_index, room_id, course) in sorted(solution.items(), key=lambda kv: (timeslots[kv[1][0]].day, timeslots[kv[1][0]].start_time)):
        instructor = instructors_by_id[instructor_id]
        ts = timeslots[slot_index]
        rows.append((instructor.name, instructor.instructor_id, ts.day, f"{ts.start_time}-{ts.end_time}", room_id, course))

    # Compute column widths for a simple console table
    headers = ("Instructor", "ID", "Day", "Time", "Room", "Course")
    table = [headers] + rows
    col_widths = [max(len(str(row[i])) for row in table) for i in range(len(headers))]

    def fmt(row: Tuple[str, ...]) -> str:
        return " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(headers)))

    sep = "-+-".join("-" * w for w in col_widths)
    print(fmt(headers))
    print(sep)
    for r in rows:
        print(fmt(r))


# -----------------------------
# Main
# -----------------------------


def generate_schedule(instructors_path: str, rooms_path: str, timeslots_path: str) -> Tuple[Dict[str, Assignment], Dict[str, Instructor], List[TimeSlot]]:
    instructors = load_instructors(instructors_path)
    rooms = load_rooms(rooms_path)
    timeslots = load_timeslots(timeslots_path)

    if not instructors:
        raise ValueError("No instructors found. Please check Instructor.csv")
    if not rooms:
        raise ValueError("No rooms found. Please check Rooms.csv")
    if not timeslots:
        raise ValueError("No timeslots found. Please check TimeSlots.csv")

    domains = build_domains(instructors, timeslots, rooms)
    solution = backtracking_search(domains)
    if solution is None:
        raise RuntimeError("No feasible schedule found with current constraints.")

    instructors_by_id: Dict[str, Instructor] = {i.instructor_id: i for i in instructors}
    return solution, instructors_by_id, timeslots


def generate_schedule_from_memory(
    instructors: List[Instructor], rooms: List[Room], timeslots: List[TimeSlot]
) -> Tuple[Dict[str, Assignment], Dict[str, Instructor], List[TimeSlot]]:
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


def run_cli():
    try:
        solution, instructors_by_id, timeslots = generate_schedule("Instructor.csv", "Rooms.csv", "TimeSlots.csv")
        write_schedule_csv("Schedule.csv", solution, instructors_by_id, timeslots)
        print("Schedule.csv generated. Preview:\n")
        print_schedule(solution, instructors_by_id, timeslots)
    except PermissionError as e:
        print(f"Error: {e}")
        print("Please close any programs that might have Schedule.csv open (like Excel) and try again.")
        print("Or try running the GUI version: py main.py --gui")
    except Exception as e:
        print(f"Error: {e}")
        print("An unexpected error occurred. Please check your input files and try again.")


def run_gui():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox

    root = tk.Tk()
    root.title("Timetable Generator (CSP)")
    root.geometry("1100x720")

    # In-memory stores
    instr_store: List[Instructor] = []
    room_store: List[Room] = []
    course_store: List[Course] = []

    timeslots_path_var = tk.StringVar(value="TimeSlots.csv")

    # Notebook with tabs
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # ----- Instructors Tab -----
    ins_tab = tk.Frame(notebook)
    notebook.add(ins_tab, text="Instructors")

    ins_form = tk.Frame(ins_tab)
    ins_form.pack(fill=tk.X, pady=6)
    ins_id = tk.StringVar(); ins_name = tk.StringVar(); ins_role = tk.StringVar(value="Professor")
    ins_pref = tk.StringVar(value="")
    ins_quals = tk.StringVar(value="")

    def add_row(parent: tk.Widget, label: str, var: tk.StringVar):
        r = tk.Frame(parent); r.pack(fill=tk.X, pady=2)
        tk.Label(r, text=label, width=16, anchor="w").pack(side=tk.LEFT)
        tk.Entry(r, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True)

    add_row(ins_form, "InstructorID", ins_id)
    add_row(ins_form, "Name", ins_name)
    add_row(ins_form, "Role", ins_role)
    add_row(ins_form, "PreferredSlots", ins_pref)
    add_row(ins_form, "QualifiedCourses", ins_quals)

    ins_btns = tk.Frame(ins_form); ins_btns.pack(fill=tk.X, pady=4)
    ins_tree = ttk.Treeview(ins_tab, columns=("InstructorID","Name","Role","PreferredSlots","QualifiedCourses"), show="headings")
    for c in ("InstructorID","Name","Role","PreferredSlots","QualifiedCourses"):
        ins_tree.heading(c, text=c); ins_tree.column(c, width=160, stretch=True)
    ins_tree.pack(fill=tk.BOTH, expand=True)

    def ins_refresh():
        for i in ins_tree.get_children(): ins_tree.delete(i)
        for ins in instr_store:
            pref = f"Not on {ins.unavailable_day}" if ins.unavailable_day else ""
            ins_tree.insert("", tk.END, values=(ins.instructor_id, ins.name, ins.role, pref, ", ".join(ins.qualified_courses)))

    def ins_add():
        iid = ins_id.get().strip()
        if not iid:
            messagebox.showerror("Error", "InstructorID is required"); return
        unavailable = parse_unavailable_day(ins_pref.get())
        quals = [q.strip() for q in ins_quals.get().split(",") if q.strip()]
        existing = [i for i in instr_store if i.instructor_id == iid]
        if existing:
            existing[0].name = ins_name.get().strip()
            existing[0].role = ins_role.get().strip()
            existing[0].unavailable_day = unavailable
            existing[0].qualified_courses = quals
        else:
            instr_store.append(Instructor(iid, ins_name.get().strip(), ins_role.get().strip(), unavailable, quals))
        ins_refresh()

    def ins_delete():
        sel = ins_tree.selection()
        if not sel: return
        iid = ins_tree.item(sel[0], "values")[0]
        instr_store[:] = [i for i in instr_store if i.instructor_id != iid]
        ins_refresh()

    def ins_import():
        p = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")]);
        if not p: return
        try:
            instr_store[:] = load_instructors(p)
            ins_refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def ins_export():
        p = filedialog.asksaveasfilename(defaultextension=".csv");
        if not p: return
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["InstructorID","Name","Role","PreferredSlots","QualifiedCourses"])
            for i in instr_store:
                pref = f"Not on {i.unavailable_day}" if i.unavailable_day else ""
                w.writerow([i.instructor_id, i.name, i.role, pref, ", ".join(i.qualified_courses)])

    tk.Button(ins_btns, text="Add/Update", command=ins_add).pack(side=tk.LEFT)
    tk.Button(ins_btns, text="Delete Selected", command=ins_delete).pack(side=tk.LEFT, padx=5)
    tk.Button(ins_btns, text="Import CSV", command=ins_import).pack(side=tk.LEFT, padx=5)
    def ins_import_excel():
        p = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx;*.xls")]);
        if not p: return
        try:
            instr_store[:] = load_instructors_excel(p)
            ins_refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    tk.Button(ins_btns, text="Import Excel", command=ins_import_excel).pack(side=tk.LEFT, padx=5)
    tk.Button(ins_btns, text="Export CSV", command=ins_export).pack(side=tk.LEFT, padx=5)

    # ----- Rooms Tab -----
    room_tab = tk.Frame(notebook)
    notebook.add(room_tab, text="Rooms/Halls")
    rm_form = tk.Frame(room_tab); rm_form.pack(fill=tk.X, pady=6)
    rm_id = tk.StringVar(); rm_type = tk.StringVar(value="Lecture"); rm_cap = tk.StringVar(value="80")
    add_row(rm_form, "RoomID", rm_id); add_row(rm_form, "Type", rm_type); add_row(rm_form, "Capacity", rm_cap)
    rm_btns = tk.Frame(rm_form); rm_btns.pack(fill=tk.X, pady=4)
    rm_tree = ttk.Treeview(room_tab, columns=("RoomID","Type","Capacity"), show="headings")
    for c in ("RoomID","Type","Capacity"):
        rm_tree.heading(c, text=c); rm_tree.column(c, width=160, stretch=True)
    rm_tree.pack(fill=tk.BOTH, expand=True)

    def rm_refresh():
        for i in rm_tree.get_children(): rm_tree.delete(i)
        for r in room_store: rm_tree.insert("", tk.END, values=(r.room_id, r.room_type, r.capacity))

    def rm_add():
        rid = rm_id.get().strip()
        if not rid: messagebox.showerror("Error", "RoomID is required"); return
        try: cap = int(rm_cap.get())
        except Exception: cap = 0
        ex = [r for r in room_store if r.room_id == rid]
        if ex:
            ex[0].room_type = rm_type.get().strip(); ex[0].capacity = cap
        else:
            room_store.append(Room(rid, rm_type.get().strip(), cap))
        rm_refresh()

    def rm_delete():
        sel = rm_tree.selection();
        if not sel: return
        rid = rm_tree.item(sel[0], "values")[0]
        room_store[:] = [r for r in room_store if r.room_id != rid]
        rm_refresh()

    def rm_import():
        p = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")]);
        if not p: return
        try:
            room_store[:] = load_rooms(p); rm_refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def rm_export():
        p = filedialog.asksaveasfilename(defaultextension=".csv");
        if not p: return
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["RoomID","Type","Capacity"])
            for r in room_store: w.writerow([r.room_id, r.room_type, r.capacity])

    tk.Button(rm_btns, text="Add/Update", command=rm_add).pack(side=tk.LEFT)
    tk.Button(rm_btns, text="Delete Selected", command=rm_delete).pack(side=tk.LEFT, padx=5)
    tk.Button(rm_btns, text="Import CSV", command=rm_import).pack(side=tk.LEFT, padx=5)
    def rm_import_excel():
        p = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx;*.xls")]);
        if not p: return
        try:
            room_store[:] = load_rooms_excel(p); rm_refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    tk.Button(rm_btns, text="Import Excel", command=rm_import_excel).pack(side=tk.LEFT, padx=5)
    tk.Button(rm_btns, text="Export CSV", command=rm_export).pack(side=tk.LEFT, padx=5)

    # ----- Courses Tab -----
    crs_tab = tk.Frame(notebook)
    notebook.add(crs_tab, text="Courses")
    crs_form = tk.Frame(crs_tab); crs_form.pack(fill=tk.X, pady=6)
    c_id = tk.StringVar(); c_name = tk.StringVar(); c_type = tk.StringVar(value="Lecture"); c_cred = tk.StringVar(value="")
    add_row(crs_form, "CourseID", c_id); add_row(crs_form, "CourseName", c_name)
    add_row(crs_form, "Type", c_type); add_row(crs_form, "Credits", c_cred)
    crs_btns = tk.Frame(crs_form); crs_btns.pack(fill=tk.X, pady=4)
    crs_tree = ttk.Treeview(crs_tab, columns=("CourseID","CourseName","Type","Credits"), show="headings")
    for c in ("CourseID","CourseName","Type","Credits"):
        crs_tree.heading(c, text=c); crs_tree.column(c, width=160, stretch=True)
    crs_tree.pack(fill=tk.BOTH, expand=True)

    def crs_refresh():
        for i in crs_tree.get_children(): crs_tree.delete(i)
        for c in course_store: crs_tree.insert("", tk.END, values=(c.course_id, c.course_name, c.course_type, c.credits if c.credits is not None else ""))

    def crs_add():
        cid = c_id.get().strip()
        if not cid: messagebox.showerror("Error", "CourseID is required"); return
        try: cr = int(c_cred.get()) if c_cred.get().strip() else None
        except Exception: cr = None
        ex = [c for c in course_store if c.course_id == cid]
        if ex:
            ex[0].course_name = c_name.get().strip(); ex[0].course_type = c_type.get().strip(); ex[0].credits = cr
        else:
            course_store.append(Course(cid, c_name.get().strip(), c_type.get().strip(), cr))
        crs_refresh()

    def crs_delete():
        sel = crs_tree.selection();
        if not sel: return
        cid = crs_tree.item(sel[0], "values")[0]
        course_store[:] = [c for c in course_store if c.course_id != cid]
        crs_refresh()

    def crs_import():
        p = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")]);
        if not p: return
        try: course_store[:] = load_courses(p); crs_refresh()
        except Exception as e: messagebox.showerror("Error", str(e))

    def crs_export():
        p = filedialog.asksaveasfilename(defaultextension=".csv");
        if not p: return
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["CourseID","CourseName","Type","Credits"])
            for c in course_store: w.writerow([c.course_id, c.course_name, c.course_type, c.credits if c.credits is not None else ""]) 

    tk.Button(crs_btns, text="Add/Update", command=crs_add).pack(side=tk.LEFT)
    tk.Button(crs_btns, text="Delete Selected", command=crs_delete).pack(side=tk.LEFT, padx=5)
    tk.Button(crs_btns, text="Import CSV", command=crs_import).pack(side=tk.LEFT, padx=5)
    def crs_import_excel():
        p = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx;*.xls")]);
        if not p: return
        try: course_store[:] = load_courses_excel(p); crs_refresh()
        except Exception as e: messagebox.showerror("Error", str(e))
    tk.Button(crs_btns, text="Import Excel", command=crs_import_excel).pack(side=tk.LEFT, padx=5)
    tk.Button(crs_btns, text="Export CSV", command=crs_export).pack(side=tk.LEFT, padx=5)

    # ----- Bottom controls -----
    bottom = tk.Frame(root); bottom.pack(fill=tk.X, padx=10, pady=(0,10))
    tk.Label(bottom, text="TimeSlots:").pack(side=tk.LEFT)
    tk.Entry(bottom, textvariable=timeslots_path_var, width=40).pack(side=tk.LEFT, padx=5)
    def browse_ts_csv():
        p = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")]);
        if p: timeslots_path_var.set(p)
    def browse_ts_excel():
        p = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx;*.xls")]);
        if p: timeslots_path_var.set(p)
    tk.Button(bottom, text="Import CSV", command=browse_ts_csv).pack(side=tk.LEFT)
    tk.Button(bottom, text="Import Excel", command=browse_ts_excel).pack(side=tk.LEFT, padx=5)
    generate_btn = tk.Button(bottom, text="Generate Timetable"); generate_btn.pack(side=tk.LEFT, padx=10)
    save_btn = tk.Button(bottom, text="Save Schedule CSV", state=tk.DISABLED); save_btn.pack(side=tk.LEFT)

    export_box = tk.Frame(root); export_box.pack(fill=tk.X, padx=10, pady=(0,10))
    tk.Label(export_box, text="Export Instructor Table:").pack(side=tk.LEFT)
    export_choice = tk.StringVar(value="")
    export_combo = ttk.Combobox(export_box, textvariable=export_choice, width=30, values=[])
    export_combo.pack(side=tk.LEFT, padx=5)
    export_btn = tk.Button(export_box, text="Export PDF", state=tk.DISABLED)
    export_btn.pack(side=tk.LEFT)

    # Results table
    columns = ("Instructor", "ID", "Day", "Time", "Room", "Course")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col); tree.column(col, width=150, stretch=True)
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    state: Dict[str, object] = {}

    def populate_tree(solution: Dict[str, Assignment], instructors_by_id: Dict[str, Instructor], timeslots: List[TimeSlot]):
        for i in tree.get_children(): tree.delete(i)
        rows: List[Tuple[str, str, str, str, str, str]] = []
        for iid, (slot_index, room_id, course) in sorted(solution.items(), key=lambda kv: (timeslots[kv[1][0]].day, timeslots[kv[1][0]].start_time)):
            ins = instructors_by_id[iid]; ts = timeslots[slot_index]
            rows.append((ins.name, ins.instructor_id, ts.day, f"{ts.start_time}-{ts.end_time}", room_id, course))
        for r in rows: tree.insert("", tk.END, values=r)

    def on_generate():
        try:
            path = timeslots_path_var.get()
            if path.lower().endswith((".xlsx", ".xls")):
                ts = load_timeslots_excel(path)
            else:
                ts = load_timeslots(path)
            solution, ins_by_id, timeslots = generate_schedule_from_memory(instr_store, room_store, ts)
            state["solution"] = solution; state["instructors_by_id"] = ins_by_id; state["timeslots"] = timeslots
            populate_tree(solution, ins_by_id, timeslots)
            save_btn.config(state=tk.NORMAL); export_btn.config(state=tk.NORMAL)
            export_combo.config(values=[f"{i.instructor_id} - {i.name}" for i in instr_store])
            messagebox.showinfo("Success", "Timetable generated.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_save():
        if "solution" not in state: return
        p = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not p: return
        write_schedule_csv(p, state["solution"], state["instructors_by_id"], state["timeslots"])  # type: ignore
        messagebox.showinfo("Saved", f"Schedule saved to {p}")

    def render_instructor_pdf(instructor_id: str, path: str):
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
        except Exception:
            messagebox.showerror("Missing ReportLab", "Install ReportLab to export PDF (pip install reportlab)")
            return
        
        solution: Dict[str, Assignment] = state.get("solution", {})  # type: ignore
        timeslots: List[TimeSlot] = state.get("timeslots", [])  # type: ignore
        if not solution or not timeslots:
            return
        
        # Create PDF document
        doc = SimpleDocTemplate(path, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph(f"Instructor Timetable: {instructor_id}", title_style))
        story.append(Spacer(1, 20))
        
        # Get instructor name
        instructor_name = instructor_id
        if "instructors_by_id" in state:
            instructors_by_id = state["instructors_by_id"]  # type: ignore
            if instructor_id in instructors_by_id:
                instructor_name = instructors_by_id[instructor_id].name
        
        story.append(Paragraph(f"<b>Instructor:</b> {instructor_name}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Determine days to show: respect full weekday order and include those present in timeslots
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        existing_days = [d for d in weekdays if any(ts.day.strip().lower() == d.lower() for ts in timeslots)]
        if not existing_days:
            # fallback to any days found in timeslots
            existing_days = sorted({ts.day for ts in timeslots})
        
        # Group timeslots by day (preserving existing_days order)
        day_slots: Dict[str, List[TimeSlot]] = {d: [ts for ts in timeslots if ts.day.strip().lower() == d.lower()] for d in existing_days}
        
        # Build ordered unique time labels across days (preserve first-seen order by day then start time)
        seen_time_keys: List[Tuple[str, str]] = []
        for d in existing_days:
            # sort slots for a day by start_time then end_time to get consistent ordering
            sorted_slots = sorted(day_slots[d], key=lambda t: (t.start_time, t.end_time))
            for ts in sorted_slots:
                key = (ts.start_time.strip(), ts.end_time.strip())
                if key not in seen_time_keys:
                    seen_time_keys.append(key)
        unique_labels: List[str] = [f"{st}-{et}" for (st, et) in seen_time_keys]
        
        # Create table data
        table_data = []
        
        # Header row
        header_row = ["Time"] + existing_days
        table_data.append(header_row)
        
        # Data rows
        for time_label in unique_labels:
            row = [time_label]
            for day in existing_days:
                # Find assignment for this instructor at this time/day
                cell_content = ""
                for iid, (slot_index, room_id, course) in solution.items():
                    if iid != instructor_id:
                        continue
                    ts = timeslots[slot_index]
                    if ts.day.strip().lower() == day.lower() and f"{ts.start_time.strip()}-{ts.end_time.strip()}" == time_label:
                        cell_content = f"{course}\nRoom: {room_id}"
                        break
                row.append(cell_content)
            table_data.append(row)
        
        # Create table
        table = Table(table_data, colWidths=[1.2*inch] + [1.5*inch] * len(existing_days))
        
        # Style the table
        table_style = TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Time column styling
            ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ])
        
        table.setStyle(table_style)
        story.append(table)
        
        # Build PDF
        doc.build(story)

    def on_export():
        if "solution" not in state: return
        sel = export_choice.get()
        if not sel:
            messagebox.showerror("Error", "Choose an instructor"); return
        iid = sel.split(" - ")[0]
        p = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not p: return
        render_instructor_pdf(iid, p); messagebox.showinfo("Saved", f"Instructor table saved to {p}")

    generate_btn.config(command=on_generate)
    save_btn.config(command=on_save)
    export_btn.config(command=on_export)

    # Initial refresh
    ins_refresh(); rm_refresh(); crs_refresh()

    root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Timetable Generator (CSP)")
    parser.add_argument("--cli", action="store_true", help="Run in command line mode instead of GUI")
    args = parser.parse_args()

    if args.cli:
        run_cli()
    else:
        run_gui()  # GUI is now the default


def normalize_day(day: str) -> str:
    """Normalize day abbreviations to full weekday names."""
    day_mapping = {
        "mon": "Monday",
        "tue": "Tuesday",
        "wed": "Wednesday",
        "thu": "Thursday",
        "fri": "Friday",
        "sat": "Saturday",
        "sun": "Sunday",
    }
    normalized = day_mapping.get(day.lower()[:3], day.capitalize())
    return normalized

def build_domains(
    instructors: List[Instructor], timeslots: List[TimeSlot], rooms: List[Room]
) -> Dict[str, List[Assignment]]:
    lecture_rooms = [r for r in rooms if r.room_type.lower() == "lecture"]
    domains: Dict[str, List[Assignment]] = {}
    for instructor in instructors:
        allowed_slots: List[int] = []
        for idx, ts in enumerate(timeslots):
            # Correctly handles all weekdays
            if instructor.unavailable_day and ts.day.lower() == instructor.unavailable_day.lower():
                continue
            allowed_slots.append(idx)
        
        courses = instructor.qualified_courses or ["GEN101"]
        options: List[Assignment] = []
        for slot_index in allowed_slots:
            for room in lecture_rooms:
                for course_code in courses[:1]:
                    options.append((slot_index, room.room_id, course_code))
        domains[instructor.instructor_id] = options
    return domains


def load_csit_data() -> Tuple[List[Course], List[Instructor], List[Room], List[TimeSlot], List[Section]]:
    """Load initial CSIT department data."""
    # Sample CSIT courses for levels 1-4
    courses = [
        Course("CSC101", "Programming 1", "Lecture", 3),
        Course("CSC102", "Programming Lab", "Lab", 1),
        Course("CSC201", "Data Structures", "Lecture", 3),
        Course("CSC301", "Algorithms", "Lecture", 3),
        Course("CSC401", "AI", "Lecture", 3),
    ]
    
    # Sample sections
    sections = [
        Section("SEC1", 1, 30),
        Section("SEC2", 2, 25),
        Section("SEC3", 3, 20),
        Section("SEC4", 4, 15),
    ]
    
    # Time slots (8 AM to 5 PM)
    slots = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday"]
    times = [
        ("9:00 AM", "10:30 AM"),
        ("10:45 AM", "12:15 PM"),
        ("12:30 PM", "2:00 PM"),
    ]
    
    for day in days:
        for start, end in times:
            slots.append(TimeSlot(day, start, end))
    
    return courses, instructors, rooms, slots, sections

if __name__ == "__main__":
    main()


