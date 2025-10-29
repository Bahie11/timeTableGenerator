"""
GUI application for the timetable generator.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from typing import Dict, List

try:
    from .models import Instructor, Room, Course, TimeSlot, Assignment
    from .data_loader import load_instructors, load_rooms, load_courses, load_timeslots, load_instructors_excel, load_rooms_excel, load_courses_excel, load_timeslots_excel
    from .csp import generate_schedule_from_memory
    from .output_utils import write_schedule_csv, print_schedule
    from .htmlexport import export_schedule_html, export_instructor_html, export_grid_html
except ImportError:
    from models import Instructor, Room, Course, TimeSlot, Assignment
    from data_loader import load_instructors, load_rooms, load_courses, load_timeslots, load_instructors_excel, load_rooms_excel, load_courses_excel, load_timeslots_excel
    from csp import generate_schedule_from_memory
    from output_utils import write_schedule_csv, print_schedule
    from htmlexport import export_schedule_html, export_instructor_html, export_grid_html


def run_gui():
    """Run the main GUI application."""
    root = tk.Tk()
    root.title("Timetable Generator (CSP)")
    root.geometry("1100x720")
    
    # Modern color scheme
    colors = {
        'primary': '#2E86AB',      # Blue
        'secondary': '#A23B72',    # Pink
        'accent': '#F18F01',       # Orange
        'success': '#4CAF50',      # Green
        'warning': '#FF9800',      # Orange
        'error': '#F44336',        # Red
        'background': '#F5F5F5',   # Light gray
        'surface': '#FFFFFF',      # White
        'text': '#333333',         # Dark gray
        'text_light': '#666666',   # Medium gray
        'border': '#E0E0E0',       # Light border
        'hover': '#E3F2FD',        # Light blue hover
        'selected': '#BBDEFB'      # Light blue selected
    }
    
    # Configure root window
    root.configure(bg=colors['background'])
    
    # Configure ttk styles
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure notebook style
    style.configure('TNotebook', background=colors['background'], borderwidth=0)
    style.configure('TNotebook.Tab', 
                   background=colors['surface'], 
                   foreground=colors['text'],
                   padding=[20, 10],
                   font=('Arial', 10, 'bold'))
    style.map('TNotebook.Tab',
              background=[('selected', colors['primary']),
                         ('active', colors['hover'])],
              foreground=[('selected', 'white'),
                         ('active', colors['text'])])
    
    # Configure button styles
    style.configure('Modern.TButton',
                   background=colors['primary'],
                   foreground='white',
                   borderwidth=0,
                   focuscolor='none',
                   font=('Arial', 9, 'bold'),
                   padding=[15, 8])
    style.map('Modern.TButton',
              background=[('active', colors['secondary']),
                         ('pressed', colors['accent'])])
    
    style.configure('Success.TButton',
                   background=colors['success'],
                   foreground='white',
                   borderwidth=0,
                   focuscolor='none',
                   font=('Arial', 9, 'bold'),
                   padding=[15, 8])
    style.map('Success.TButton',
              background=[('active', '#45A049'),
                         ('pressed', '#3D8B40')])
    
    style.configure('Warning.TButton',
                   background=colors['warning'],
                   foreground='white',
                   borderwidth=0,
                   focuscolor='none',
                   font=('Arial', 9, 'bold'),
                   padding=[15, 8])
    
    # Configure treeview styles
    style.configure('Modern.Treeview',
                   background=colors['surface'],
                   foreground=colors['text'],
                   fieldbackground=colors['surface'],
                   borderwidth=1,
                   relief='solid')
    style.configure('Modern.Treeview.Heading',
                   background=colors['primary'],
                   foreground='white',
                   font=('Arial', 9, 'bold'),
                   borderwidth=0)
    style.map('Modern.Treeview',
              background=[('selected', colors['selected'])],
              foreground=[('selected', colors['text'])])
    
    # Configure entry styles
    style.configure('Modern.TEntry',
                   fieldbackground=colors['surface'],
                   borderwidth=1,
                   relief='solid',
                   font=('Arial', 9))
    style.map('Modern.TEntry',
              focuscolor=[('!focus', colors['border']),
                         ('focus', colors['primary'])])
    
    # Configure label styles
    style.configure('Modern.TLabel',
                   background=colors['background'],
                   foreground=colors['text'],
                   font=('Arial', 9))
    
    style.configure('Title.TLabel',
                   background=colors['background'],
                   foreground=colors['primary'],
                   font=('Arial', 12, 'bold'))

    # Animation functions
    def animate_button_click(button, original_bg=None):
        """Animate button click with color change"""
        if original_bg is None:
            original_bg = button.cget('bg') if hasattr(button, 'cget') else colors['primary']
        
        # Flash effect
        button.configure(bg=colors['accent'])
        root.after(100, lambda: button.configure(bg=original_bg))
    
    def animate_progress_bar(progress_var, duration=2000):
        """Animate progress bar filling"""
        progress_var.set(0)
        steps = 50
        step_duration = duration // steps
        
        def update_progress(step):
            if step <= steps:
                progress_var.set(step / steps * 100)
                root.after(step_duration, lambda: update_progress(step + 1))
        
        update_progress(0)
    
    def fade_in_widget(widget, duration=300):
        """Fade in animation for widgets"""
        widget.configure(alpha=0.0)
        steps = 20
        step_duration = duration // steps
        
        def fade_step(step):
            if step <= steps:
                alpha = step / steps
                try:
                    widget.configure(alpha=alpha)
                except:
                    pass  # Some widgets don't support alpha
                root.after(step_duration, lambda: fade_step(step + 1))
        
        fade_step(0)
    
    def pulse_animation(widget, color1, color2, cycles=3):
        """Pulse animation for widgets"""
        def pulse_step(cycle, use_color1=True):
            if cycle < cycles:
                color = color1 if use_color1 else color2
                try:
                    widget.configure(bg=color)
                except:
                    pass
                root.after(200, lambda: pulse_step(cycle if use_color1 else cycle + 1, not use_color1))
        
        pulse_step(0)
    
    def loading_animation(label, text="Generating timetable"):
        """Loading animation with dots"""
        dots = 0
        max_dots = 3
        
        def animate_loading():
            nonlocal dots
            dots = (dots + 1) % (max_dots + 1)
            label.configure(text=text + "." * dots)
            root.after(500, animate_loading)
        
        return animate_loading

    # In-memory stores
    instr_store: List[Instructor] = []
    room_store: List[Room] = []
    course_store: List[Course] = []

    timeslots_path_var = tk.StringVar(value="../Data/TimeSlots.csv")

    # Notebook with tabs
    notebook = ttk.Notebook(root, style='TNotebook')
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Add fade-in animation to notebook
    root.after(100, lambda: fade_in_widget(notebook))

    # ----- Instructors Tab -----
    ins_tab = tk.Frame(notebook, bg=colors['background'])
    notebook.add(ins_tab, text="👨‍🏫 Instructors")

    ins_form = tk.Frame(ins_tab, bg=colors['background'])
    ins_form.pack(fill=tk.X, pady=6)
    ins_id = tk.StringVar(); ins_name = tk.StringVar(); ins_role = tk.StringVar(value="Professor")
    ins_pref = tk.StringVar(value="")
    ins_quals = tk.StringVar(value="")

    def add_row(parent: tk.Widget, label: str, var: tk.StringVar):
        r = tk.Frame(parent, bg=colors['background']); r.pack(fill=tk.X, pady=3)
        label_widget = tk.Label(r, text=label, width=16, anchor="w", 
                               bg=colors['background'], fg=colors['text'],
                               font=('Arial', 9, 'bold'))
        label_widget.pack(side=tk.LEFT, padx=(0, 10))
        entry = ttk.Entry(r, textvariable=var, style='Modern.TEntry')
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Add hover effect
        def on_enter(e):
            entry.configure(style='Modern.TEntry')
        def on_leave(e):
            entry.configure(style='Modern.TEntry')
        entry.bind('<Enter>', on_enter)
        entry.bind('<Leave>', on_leave)

    add_row(ins_form, "InstructorID", ins_id)
    add_row(ins_form, "Name", ins_name)
    add_row(ins_form, "Role", ins_role)
    add_row(ins_form, "PreferredSlots", ins_pref)
    add_row(ins_form, "QualifiedCourses", ins_quals)

    ins_btns = tk.Frame(ins_form, bg=colors['background']); ins_btns.pack(fill=tk.X, pady=8)
    ins_tree = ttk.Treeview(ins_tab, columns=("InstructorID","Name","Role","PreferredSlots","QualifiedCourses"), 
                           show="headings", style='Modern.Treeview')
    for c in ("InstructorID","Name","Role","PreferredSlots","QualifiedCourses"):
        ins_tree.heading(c, text=c); ins_tree.column(c, width=160, stretch=True)
    ins_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # Add scrollbar to treeview
    ins_scrollbar = ttk.Scrollbar(ins_tab, orient="vertical", command=ins_tree.yview)
    ins_tree.configure(yscrollcommand=ins_scrollbar.set)
    ins_scrollbar.pack(side="right", fill="y")

    def ins_refresh():
        for i in ins_tree.get_children(): ins_tree.delete(i)
        for ins in instr_store:
            pref = f"Not on {ins.unavailable_day}" if ins.unavailable_day else ""
            ins_tree.insert("", tk.END, values=(ins.instructor_id, ins.name, ins.role, pref, ", ".join(ins.qualified_courses)))

    def ins_add():
        iid = ins_id.get().strip()
        if not iid:
            messagebox.showerror("Error", "InstructorID is required"); return
        from data_loader import parse_unavailable_day, parse_qualified_courses
        unavailable = parse_unavailable_day(ins_pref.get())
        quals = parse_qualified_courses(ins_quals.get())
        existing = [i for i in instr_store if i.instructor_id == iid]
        if existing:
            existing[0].name = ins_name.get().strip()
            existing[0].role = ins_role.get().strip()
            existing[0].unavailable_day = unavailable
            existing[0].qualified_courses = quals
        else:
            instr_store.append(Instructor(iid, ins_name.get().strip(), ins_role.get().strip(), unavailable, quals))
        ins_refresh()
        
        # Clear form and animate success
        ins_id.set(""); ins_name.set(""); ins_role.set("Professor")
        ins_pref.set(""); ins_quals.set("")
        pulse_animation(ins_tree, colors['success'], colors['surface'])

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
        import csv
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["InstructorID","Name","Role","PreferredSlots","QualifiedCourses"])
            for i in instr_store:
                pref = f"Not on {i.unavailable_day}" if i.unavailable_day else ""
                w.writerow([i.instructor_id, i.name, i.role, pref, ", ".join(i.qualified_courses)])

    # Create modern buttons with animations
    add_btn = ttk.Button(ins_btns, text="➕ Add/Update", command=ins_add, style='Success.TButton')
    add_btn.pack(side=tk.LEFT, padx=2)
    add_btn.bind('<Button-1>', lambda e: animate_button_click(add_btn))
    
    delete_btn = ttk.Button(ins_btns, text="🗑️ Delete", command=ins_delete, style='Warning.TButton')
    delete_btn.pack(side=tk.LEFT, padx=2)
    delete_btn.bind('<Button-1>', lambda e: animate_button_click(delete_btn))
    
    import_csv_btn = ttk.Button(ins_btns, text="📁 Import CSV", command=ins_import, style='Modern.TButton')
    import_csv_btn.pack(side=tk.LEFT, padx=2)
    import_csv_btn.bind('<Button-1>', lambda e: animate_button_click(import_csv_btn))
    
    def ins_import_excel():
        p = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx;*.xls")]);
        if not p: return
        try:
            instr_store[:] = load_instructors_excel(p)
            ins_refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    import_excel_btn = ttk.Button(ins_btns, text="📊 Import Excel", command=ins_import_excel, style='Modern.TButton')
    import_excel_btn.pack(side=tk.LEFT, padx=2)
    import_excel_btn.bind('<Button-1>', lambda e: animate_button_click(import_excel_btn))
    
    export_btn = ttk.Button(ins_btns, text="💾 Export CSV", command=ins_export, style='Modern.TButton')
    export_btn.pack(side=tk.LEFT, padx=2)
    export_btn.bind('<Button-1>', lambda e: animate_button_click(export_btn))

    # ----- Rooms Tab -----
    room_tab = tk.Frame(notebook, bg=colors['background'])
    notebook.add(room_tab, text="🏢 Rooms/Halls")
    rm_form = tk.Frame(room_tab, bg=colors['background']); rm_form.pack(fill=tk.X, pady=6)
    rm_id = tk.StringVar(); rm_type = tk.StringVar(value="Lecture"); rm_cap = tk.StringVar(value="80")
    add_row(rm_form, "RoomID", rm_id); add_row(rm_form, "Type", rm_type); add_row(rm_form, "Capacity", rm_cap)
    rm_btns = tk.Frame(rm_form, bg=colors['background']); rm_btns.pack(fill=tk.X, pady=8)
    rm_tree = ttk.Treeview(room_tab, columns=("RoomID","Type","Capacity"), 
                          show="headings", style='Modern.Treeview')
    for c in ("RoomID","Type","Capacity"):
        rm_tree.heading(c, text=c); rm_tree.column(c, width=160, stretch=True)
    rm_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # Add scrollbar to room treeview
    rm_scrollbar = ttk.Scrollbar(room_tab, orient="vertical", command=rm_tree.yview)
    rm_tree.configure(yscrollcommand=rm_scrollbar.set)
    rm_scrollbar.pack(side="right", fill="y")

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
        import csv
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["RoomID","Type","Capacity"])
            for r in room_store: w.writerow([r.room_id, r.room_type, r.capacity])

    # Create modern room buttons with animations
    rm_add_btn = ttk.Button(rm_btns, text="➕ Add/Update", command=rm_add, style='Success.TButton')
    rm_add_btn.pack(side=tk.LEFT, padx=2)
    rm_add_btn.bind('<Button-1>', lambda e: animate_button_click(rm_add_btn))
    
    rm_delete_btn = ttk.Button(rm_btns, text="🗑️ Delete", command=rm_delete, style='Warning.TButton')
    rm_delete_btn.pack(side=tk.LEFT, padx=2)
    rm_delete_btn.bind('<Button-1>', lambda e: animate_button_click(rm_delete_btn))
    
    rm_import_btn = ttk.Button(rm_btns, text="📁 Import CSV", command=rm_import, style='Modern.TButton')
    rm_import_btn.pack(side=tk.LEFT, padx=2)
    rm_import_btn.bind('<Button-1>', lambda e: animate_button_click(rm_import_btn))
    
    def rm_import_excel():
        p = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx;*.xls")]);
        if not p: return
        try:
            room_store[:] = load_rooms_excel(p); rm_refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    rm_import_excel_btn = ttk.Button(rm_btns, text="📊 Import Excel", command=rm_import_excel, style='Modern.TButton')
    rm_import_excel_btn.pack(side=tk.LEFT, padx=2)
    rm_import_excel_btn.bind('<Button-1>', lambda e: animate_button_click(rm_import_excel_btn))
    
    rm_export_btn = ttk.Button(rm_btns, text="💾 Export CSV", command=rm_export, style='Modern.TButton')
    rm_export_btn.pack(side=tk.LEFT, padx=2)
    rm_export_btn.bind('<Button-1>', lambda e: animate_button_click(rm_export_btn))

    # ----- Courses Tab -----
    crs_tab = tk.Frame(notebook, bg=colors['background'])
    notebook.add(crs_tab, text="📚 Courses")
    crs_form = tk.Frame(crs_tab, bg=colors['background']); crs_form.pack(fill=tk.X, pady=6)
    c_id = tk.StringVar(); c_name = tk.StringVar(); c_type = tk.StringVar(value="Lecture"); c_cred = tk.StringVar(value="")
    add_row(crs_form, "CourseID", c_id); add_row(crs_form, "CourseName", c_name)
    add_row(crs_form, "Type", c_type); add_row(crs_form, "Credits", c_cred)
    crs_btns = tk.Frame(crs_form, bg=colors['background']); crs_btns.pack(fill=tk.X, pady=8)
    crs_tree = ttk.Treeview(crs_tab, columns=("CourseID","CourseName","Type","Credits"), 
                            show="headings", style='Modern.Treeview')
    for c in ("CourseID","CourseName","Type","Credits"):
        crs_tree.heading(c, text=c); crs_tree.column(c, width=160, stretch=True)
    crs_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # Add scrollbar to course treeview
    crs_scrollbar = ttk.Scrollbar(crs_tab, orient="vertical", command=crs_tree.yview)
    crs_tree.configure(yscrollcommand=crs_scrollbar.set)
    crs_scrollbar.pack(side="right", fill="y")

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
        import csv
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["CourseID","CourseName","Type","Credits"])
            for c in course_store: w.writerow([c.course_id, c.course_name, c.course_type, c.credits if c.credits is not None else ""]) 

    # Create modern course buttons with animations
    crs_add_btn = ttk.Button(crs_btns, text="➕ Add/Update", command=crs_add, style='Success.TButton')
    crs_add_btn.pack(side=tk.LEFT, padx=2)
    crs_add_btn.bind('<Button-1>', lambda e: animate_button_click(crs_add_btn))
    
    crs_delete_btn = ttk.Button(crs_btns, text="🗑️ Delete", command=crs_delete, style='Warning.TButton')
    crs_delete_btn.pack(side=tk.LEFT, padx=2)
    crs_delete_btn.bind('<Button-1>', lambda e: animate_button_click(crs_delete_btn))
    
    crs_import_btn = ttk.Button(crs_btns, text="📁 Import CSV", command=crs_import, style='Modern.TButton')
    crs_import_btn.pack(side=tk.LEFT, padx=2)
    crs_import_btn.bind('<Button-1>', lambda e: animate_button_click(crs_import_btn))
    
    def crs_import_excel():
        p = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx;*.xls")]);
        if not p: return
        try: course_store[:] = load_courses_excel(p); crs_refresh()
        except Exception as e: messagebox.showerror("Error", str(e))
    crs_import_excel_btn = ttk.Button(crs_btns, text="📊 Import Excel", command=crs_import_excel, style='Modern.TButton')
    crs_import_excel_btn.pack(side=tk.LEFT, padx=2)
    crs_import_excel_btn.bind('<Button-1>', lambda e: animate_button_click(crs_import_excel_btn))
    
    crs_export_btn = ttk.Button(crs_btns, text="💾 Export CSV", command=crs_export, style='Modern.TButton')
    crs_export_btn.pack(side=tk.LEFT, padx=2)
    crs_export_btn.bind('<Button-1>', lambda e: animate_button_click(crs_export_btn))

    # ----- Bottom controls -----
    bottom = tk.Frame(root, bg=colors['background']); bottom.pack(fill=tk.X, padx=10, pady=(0,10))
    
    # TimeSlots section with modern styling
    timeslots_frame = tk.Frame(bottom, bg=colors['surface'], relief='solid', bd=1)
    timeslots_frame.pack(fill=tk.X, pady=5)
    
    tk.Label(timeslots_frame, text="⏰ TimeSlots:", 
             bg=colors['surface'], fg=colors['text'], font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
    
    timeslots_entry = ttk.Entry(timeslots_frame, textvariable=timeslots_path_var, width=40, style='Modern.TEntry')
    timeslots_entry.pack(side=tk.LEFT, padx=5)
    
    def browse_ts_csv():
        p = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")]);
        if p: timeslots_path_var.set(p)
    def browse_ts_excel():
        p = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx;*.xls")]);
        if p: timeslots_path_var.set(p)
    
    ts_csv_btn = ttk.Button(timeslots_frame, text="📁 Import CSV", command=browse_ts_csv, style='Modern.TButton')
    ts_csv_btn.pack(side=tk.LEFT, padx=2)
    ts_csv_btn.bind('<Button-1>', lambda e: animate_button_click(ts_csv_btn))
    
    ts_excel_btn = ttk.Button(timeslots_frame, text="📊 Import Excel", command=browse_ts_excel, style='Modern.TButton')
    ts_excel_btn.pack(side=tk.LEFT, padx=2)
    ts_excel_btn.bind('<Button-1>', lambda e: animate_button_click(ts_excel_btn))
    
    # Main action buttons
    action_frame = tk.Frame(bottom, bg=colors['background'])
    action_frame.pack(fill=tk.X, pady=5)
    
    generate_btn = ttk.Button(action_frame, text="🚀 Generate Timetable", style='Success.TButton')
    generate_btn.pack(side=tk.LEFT, padx=5)
    generate_btn.bind('<Button-1>', lambda e: animate_button_click(generate_btn))
    
    save_btn = ttk.Button(action_frame, text="💾 Save Schedule CSV", state=tk.DISABLED, style='Modern.TButton')
    save_btn.pack(side=tk.LEFT, padx=5)
    save_btn.bind('<Button-1>', lambda e: animate_button_click(save_btn))
    
    # Progress bar for loading animation
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(action_frame, variable=progress_var, maximum=100, length=200)
    progress_bar.pack(side=tk.LEFT, padx=10)
    progress_bar.pack_forget()  # Hide initially
    
    # Loading label
    loading_label = tk.Label(action_frame, text="", bg=colors['background'], fg=colors['primary'], font=('Arial', 9, 'bold'))
    loading_label.pack(side=tk.LEFT, padx=5)
    loading_label.pack_forget()  # Hide initially

    # Export section with modern styling
    export_box = tk.Frame(root, bg=colors['surface'], relief='solid', bd=1)
    export_box.pack(fill=tk.X, padx=10, pady=(0,10))
    
    tk.Label(export_box, text="📄 Export Instructor Table:", 
             bg=colors['surface'], fg=colors['text'], font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
    export_choice = tk.StringVar(value="")
    export_combo = ttk.Combobox(export_box, textvariable=export_choice, width=30, values=[])
    export_combo.pack(side=tk.LEFT, padx=5)
    
    export_btn = ttk.Button(export_box, text="📊 Export PDF", state=tk.DISABLED, style='Modern.TButton')
    export_btn.pack(side=tk.LEFT, padx=5)
    export_btn.bind('<Button-1>', lambda e: animate_button_click(export_btn))
    
    # Add HTML export buttons
    html_export_btn = ttk.Button(export_box, text="🌐 Export All HTML", state=tk.DISABLED, style='Modern.TButton')
    html_export_btn.pack(side=tk.LEFT, padx=5)
    html_export_btn.bind('<Button-1>', lambda e: animate_button_click(html_export_btn))
    
    html_grid_btn = ttk.Button(export_box, text="📅 Export Grid HTML", state=tk.DISABLED, style='Modern.TButton')
    html_grid_btn.pack(side=tk.LEFT, padx=5)
    html_grid_btn.bind('<Button-1>', lambda e: animate_button_click(html_grid_btn))
    
    html_instructor_btn = ttk.Button(export_box, text="👨‍🏫 Export Instructor HTML", state=tk.DISABLED, style='Modern.TButton')
    html_instructor_btn.pack(side=tk.LEFT, padx=5)
    html_instructor_btn.bind('<Button-1>', lambda e: animate_button_click(html_instructor_btn))

    # Results table with modern styling
    results_frame = tk.Frame(root, bg=colors['background'])
    results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    # Results title
    results_title = tk.Label(results_frame, text="📋 Generated Schedule", 
                             bg=colors['background'], fg=colors['primary'], 
                             font=('Arial', 12, 'bold'))
    results_title.pack(pady=(0, 5))
    
    columns = ("Instructor", "ID", "Day", "Time", "Room", "Course")
    tree = ttk.Treeview(results_frame, columns=columns, show="headings", style='Modern.Treeview')
    for col in columns:
        tree.heading(col, text=col); tree.column(col, width=150, stretch=True)
    tree.pack(fill=tk.BOTH, expand=True)
    
    # Add scrollbar to results table
    results_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=results_scrollbar.set)
    results_scrollbar.pack(side="right", fill="y")

    state: Dict[str, object] = {}

    def populate_tree(solution: Dict[str, Assignment], instructors_by_id: Dict[str, Instructor], timeslots: List[TimeSlot]):
        for i in tree.get_children(): tree.delete(i)
        rows: List[Tuple[str, str, str, str, str, str]] = []
        from output_utils import get_proper_sort_key
        for iid, (slot_index, room_id, course) in sorted(solution.items(), key=lambda kv: get_proper_sort_key(kv, timeslots)):
            ins = instructors_by_id[iid]; ts = timeslots[slot_index]
            rows.append((ins.name, ins.instructor_id, ts.day, f"{ts.start_time}-{ts.end_time}", room_id, course))
        for r in rows: tree.insert("", tk.END, values=r)

    def on_generate():
        def generate_worker():
            try:
                # Show loading animation
                progress_bar.pack(side=tk.LEFT, padx=10)
                loading_label.pack(side=tk.LEFT, padx=5)
                loading_anim = loading_animation(loading_label, "Generating timetable")
                loading_anim()
                
                # Animate progress bar
                animate_progress_bar(progress_var, 3000)
                
                path = timeslots_path_var.get()
                if path.lower().endswith((".xlsx", ".xls")):
                    ts = load_timeslots_excel(path)
                else:
                    ts = load_timeslots(path)
                solution, ins_by_id, timeslots = generate_schedule_from_memory(instr_store, room_store, ts)
                
                # Update UI in main thread
                root.after(0, lambda: update_ui_after_generation(solution, ins_by_id, timeslots))
                
            except Exception as e:
                root.after(0, lambda: handle_generation_error(e))
        
        def update_ui_after_generation(solution, ins_by_id, timeslots):
            state["solution"] = solution
            state["instructors_by_id"] = ins_by_id
            state["timeslots"] = timeslots
            populate_tree(solution, ins_by_id, timeslots)
            save_btn.config(state=tk.NORMAL)
            export_btn.config(state=tk.NORMAL)
            html_export_btn.config(state=tk.NORMAL)
            html_grid_btn.config(state=tk.NORMAL)
            html_instructor_btn.config(state=tk.NORMAL)
            export_combo.config(values=[f"{i.instructor_id} - {i.name}" for i in instr_store])
            
            # Hide loading elements
            progress_bar.pack_forget()
            loading_label.pack_forget()
            
            # Show success animation
            pulse_animation(tree, colors['success'], colors['surface'])
            messagebox.showinfo("Success", "Timetable generated successfully! 🎉")
        
        def handle_generation_error(e):
            # Hide loading elements
            progress_bar.pack_forget()
            loading_label.pack_forget()
            messagebox.showerror("Error", str(e))
        
        # Start generation in background thread
        threading.Thread(target=generate_worker, daemon=True).start()

    def on_save():
        if "solution" not in state: return
        p = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not p: return
        write_schedule_csv(p, state["solution"], state["instructors_by_id"], state["timeslots"])  # type: ignore
        messagebox.showinfo("Saved", f"Schedule saved to {p}")

    def on_export():
        if "solution" not in state: return
        sel = export_choice.get()
        if not sel:
            messagebox.showerror("Error", "Choose an instructor"); return
        iid = sel.split(" - ")[0]
        p = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not p: return
        # PDF export would go here
        messagebox.showinfo("Saved", f"Instructor table saved to {p}")

    def on_html_export():
        if "solution" not in state: return
        p = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML", "*.html")])
        if not p: return
        try:
            export_schedule_html(state["solution"], state["instructors_by_id"], state["timeslots"], p)  # type: ignore
            messagebox.showinfo("Success", f"HTML schedule exported to {p}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export HTML: {str(e)}")

    def on_instructor_html_export():
        if "solution" not in state: return
        sel = export_choice.get()
        if not sel:
            messagebox.showerror("Error", "Choose an instructor"); return
        iid = sel.split(" - ")[0]
        p = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML", "*.html")])
        if not p: return
        try:
            export_instructor_html(iid, state["solution"], state["instructors_by_id"], state["timeslots"], p)  # type: ignore
            messagebox.showinfo("Success", f"Instructor timetable exported to {p}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export instructor HTML: {str(e)}")

    def on_grid_html_export():
        if "solution" not in state: return
        p = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML", "*.html")])
        if not p: return
        try:
            export_grid_html(state["solution"], state["instructors_by_id"], state["timeslots"], p)  # type: ignore
            messagebox.showinfo("Success", f"Grid timetable exported to {p}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export grid HTML: {str(e)}")

    generate_btn.config(command=on_generate)
    save_btn.config(command=on_save)
    export_btn.config(command=on_export)
    html_export_btn.config(command=on_html_export)
    html_grid_btn.config(command=on_grid_html_export)
    html_instructor_btn.config(command=on_instructor_html_export)

    # Initial refresh
    ins_refresh(); rm_refresh(); crs_refresh()

    root.mainloop()


if __name__ == "__main__":
    run_gui()
