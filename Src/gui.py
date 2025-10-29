"""
Enhanced GUI application for the timetable generator with comprehensive features.
"""
import os
import sys
import threading
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path

from data_loader import load_instructors_excel, load_rooms_excel, load_timeslots_excel, load_courses_excel
from csp import generate_schedule_from_memory
from csp_enhanced import generate_schedule_enhanced
from csp_fixed import generate_schedule_fixed
from output_utils import write_schedule_csv, print_schedule, get_proper_sort_key
from htmlexport import export_schedule_html, export_instructor_html, export_grid_html


class TimetableGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 University Timetable Generator - Advanced CSP Solver")
        self.root.geometry("1100x750")
        
        # Modern color scheme (matching HTML output)
        self.colors = {
            'primary': '#2E86AB',      # Blue
            'secondary': '#A23B72',    # Pink
            'accent': '#F18F01',       # Orange
            'success': '#06D6A0',      # Green
            'bg_light': '#F8F9FA',     # Light gray
            'bg_white': '#FFFFFF',     # White
            'text_dark': '#333333',    # Dark gray
            'text_light': '#666666',   # Medium gray
            'course_bg': '#E3F2FD',    # Light blue
            'course_text': '#1976D2',  # Blue
            'room_bg': '#F3E5F5',      # Light purple
            'room_text': '#7B1FA2',    # Purple
            'hover': '#E9ECEF'         # Hover gray
        }
        
        # Configure style
        self.setup_styles()
        
        # Set background color
        self.root.configure(bg=self.colors['bg_light'])
        
        # Data storage
        self.solution = None
        self.instructors_by_id = None
        self.timeslots = None
        self.instructors = None
        self.rooms = None
        self.courses = None
        
        # Worker state
        self.worker_state = {"thread": None, "event": threading.Event()}
        self.progress_q = queue.Queue()
        
        # Configuration variables (Configuration tab removed - using optimal defaults)
        # DEFAULT SETTINGS: Fixed CSP with randomization enabled
        self.max_nodes_var = tk.IntVar(value=200000)
        self.timeout_var = tk.IntVar(value=30)
        self.use_enhanced_csp = tk.BooleanVar(value=False)  # Enhanced CSP - OFF
        self.use_fixed_csp = tk.BooleanVar(value=True)  # FIXED CSP - ON (allows multiple classes per instructor)
        self.randomize_var = tk.BooleanVar(value=True)  # Randomization - ON (better distribution)
        
        # File paths - can be selected from anywhere on the computer
        self.instructors_path_var = tk.StringVar(value="")
        self.rooms_path_var = tk.StringVar(value="")
        self.courses_path_var = tk.StringVar(value="")
        self.timeslots_path_var = tk.StringVar(value="")
        
        self.create_widgets()
        self.start_progress_update()
        self.animate_welcome()
    
    def setup_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure Notebook (tabs) with modern colors
        style.configure('TNotebook', background=self.colors['bg_light'], borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background=self.colors['bg_white'],
                       foreground=self.colors['text_dark'],
                       padding=[20, 10],
                       font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['primary'])],
                 foreground=[('selected', 'white')],
                 expand=[('selected', [1, 1, 1, 0])])
        
        # Configure Frames
        style.configure('TFrame', background=self.colors['bg_light'])
        style.configure('Card.TFrame', background=self.colors['bg_white'], relief='raised')
        
        # Configure Labels
        style.configure('TLabel', background=self.colors['bg_light'], 
                       foreground=self.colors['text_dark'], font=('Segoe UI', 10))
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), 
                       foreground=self.colors['primary'])
        style.configure('Subtitle.TLabel', font=('Segoe UI', 11), 
                       foreground=self.colors['text_light'])
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'), 
                       foreground=self.colors['primary'])
        
        # Configure Buttons with modern styling
        style.configure('TButton',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 10, 'bold'),
                       padding=[15, 8])
        style.map('TButton',
                 background=[('active', self.colors['secondary']), ('pressed', self.colors['secondary'])],
                 relief=[('pressed', 'flat'), ('!pressed', 'flat')])
        
        # Accent button (orange)
        style.configure('Accent.TButton',
                       background=self.colors['accent'],
                       foreground='white',
                       font=('Segoe UI', 11, 'bold'),
                       padding=[20, 10])
        style.map('Accent.TButton',
                 background=[('active', '#FF9800')])
        
        # Success button (green)
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'),
                       padding=[15, 8])
        
        # Configure LabelFrame
        style.configure('TLabelframe', background=self.colors['bg_white'], 
                       borderwidth=2, relief='groove')
        style.configure('TLabelframe.Label', background=self.colors['bg_white'], 
                       foreground=self.colors['primary'], font=('Segoe UI', 11, 'bold'))
        
        # Configure Entry
        style.configure('TEntry', fieldbackground='white', borderwidth=1)
        
        # Configure Progressbar with modern colors
        style.configure('TProgressbar', 
                       background=self.colors['success'],
                       troughcolor=self.colors['hover'],
                       borderwidth=0,
                       thickness=20)
        
    def animate_welcome(self):
        """Subtle welcome animation"""
        # Fade in effect simulation
        self.root.attributes('-alpha', 0.0)
        self.fade_in()
    
    def fade_in(self, alpha=0.0):
        """Fade in animation"""
        alpha += 0.1
        if alpha <= 1.0:
            self.root.attributes('-alpha', alpha)
            self.root.after(30, lambda: self.fade_in(alpha))
        else:
            self.root.attributes('-alpha', 1.0)
    
    def on_button_hover(self, event, button):
        """Button hover effect"""
        button.state(['active'])
    
    def on_button_leave(self, event, button):
        """Button leave effect"""
        button.state(['!active'])
    
    def animate_status(self, message, color=None):
        """Animate status bar message with color"""
        if color is None:
            color = self.colors['primary']
        
        # Update status with animation
        self.status_label.config(text=message, bg=color)
        
        # Pulse effect
        self.pulse_status(color, 0)
    
    def pulse_status(self, target_color, step):
        """Create a pulse effect on status bar"""
        if step < 3:
            # Alternate between target color and slightly darker
            if step % 2 == 0:
                self.status_label.config(bg=target_color)
            else:
                # Slightly darker
                self.status_label.config(bg=self.colors['primary'])
            
            self.root.after(200, lambda: self.pulse_status(target_color, step + 1))
        else:
            # Return to target color
            self.status_label.config(bg=target_color)
        
    def create_widgets(self):
        """Create the main UI layout with tabs"""
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create tabs
        self.create_data_tab()
        # Configuration tab removed - using default settings
        self.create_results_tab()
        self.create_export_tab()
        
        # Status bar at the bottom
        self.create_status_bar()
        
    def create_data_tab(self):
        """Tab for data file selection and generation"""
        data_frame = ttk.Frame(self.notebook, padding=10)
        data_frame.configure(style='TFrame')
        self.notebook.add(data_frame, text="📁 Data Files")
        
        # Modern header with gradient-like effect
        header_frame = tk.Frame(data_frame, bg=self.colors['primary'], height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="📁 Data Files Configuration", 
                        font=("Segoe UI", 18, "bold"), 
                        bg=self.colors['primary'], fg='white')
        title.pack(expand=True)
        
        subtitle = tk.Label(header_frame, text="Load your Excel files to begin scheduling", 
                           font=("Segoe UI", 10), 
                           bg=self.colors['primary'], fg='white')
        subtitle.pack()
        
        # File selection frame
        files_frame = ttk.LabelFrame(data_frame, text="Input Files (Select from anywhere on your computer)", padding=10)
        files_frame.pack(fill="x", pady=5)
        
        # Info message
        info_msg = ttk.Label(files_frame, 
                            text="💡 Click 'Browse...' to select Excel (.xlsx, .xls) or CSV files from any location",
                            foreground="blue", font=("Segoe UI", 9))
        info_msg.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))
        
        files_data = [
            ("Instructors File:", self.instructors_path_var),
            ("Rooms File:", self.rooms_path_var),
            ("Courses File:", self.courses_path_var),
            ("Timeslots File:", self.timeslots_path_var)
        ]
        
        for idx, (label, var) in enumerate(files_data):
            row_idx = idx + 1  # Offset by 1 due to info message
            ttk.Label(files_frame, text=label, width=15).grid(row=row_idx, column=0, sticky="w", pady=3)
            entry = ttk.Entry(files_frame, textvariable=var, width=60)
            entry.grid(row=row_idx, column=1, sticky="ew", padx=5)
            ttk.Button(files_frame, text="Browse...", 
                      command=lambda v=var: self.browse_file(v)).grid(row=row_idx, column=2, padx=5)
        
        files_frame.columnconfigure(1, weight=1)
        
        # Load data button
        load_frame = ttk.Frame(data_frame)
        load_frame.pack(pady=10)
        
        load_btn = ttk.Button(load_frame, text="🔄 Load Data Files", 
                  command=self.load_data_files, width=20, style='Accent.TButton')
        load_btn.pack(side="left", padx=5)
        
        # Add hover effect
        load_btn.bind('<Enter>', lambda e: self.on_button_hover(e, load_btn))
        load_btn.bind('<Leave>', lambda e: self.on_button_leave(e, load_btn))
        
        self.data_status_label = ttk.Label(load_frame, text="⚪ No data loaded", foreground=self.colors['text_light'])
        self.data_status_label.pack(side="left", padx=10)
        
        # Generation frame
        gen_frame = ttk.LabelFrame(data_frame, text="Schedule Generation", padding=15)
        gen_frame.pack(fill="both", expand=True, pady=10)
        
        # Progress
        progress_frame = ttk.Frame(gen_frame)
        progress_frame.pack(fill="x", pady=10)
        
        self.progress_label = ttk.Label(progress_frame, text="Ready to generate (🔧 Fixed CSP - Multiple classes per instructor)", font=("Segoe UI", 10))
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate", length=400)
        self.progress_bar.pack(pady=5)
        
        # Buttons
        button_frame = ttk.Frame(gen_frame)
        button_frame.pack(pady=10)
        
        self.generate_btn = ttk.Button(button_frame, text="▶ Generate Timetable", 
                                       command=self.on_generate, width=25, style='Accent.TButton')
        self.generate_btn.pack(side="left", padx=5)
        self.generate_btn.bind('<Enter>', lambda e: self.on_button_hover(e, self.generate_btn))
        self.generate_btn.bind('<Leave>', lambda e: self.on_button_leave(e, self.generate_btn))
        
        self.cancel_btn = ttk.Button(button_frame, text="⏹ Cancel", 
                                     command=self.on_cancel, state="disabled", width=15)
        self.cancel_btn.pack(side="left", padx=5)
        
    # Configuration tab removed - using default settings (Fixed CSP enabled)
    # def create_config_tab(self):
    #     """Tab for algorithm configuration - REMOVED"""
    #     pass
        
    def create_results_tab(self):
        """Tab for viewing generated results"""
        results_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(results_frame, text="📊 Results")
        
        # Modern header
        header_frame = tk.Frame(results_frame, bg=self.colors['accent'], height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="📊 Generated Schedule", 
                        font=("Segoe UI", 18, "bold"), 
                        bg=self.colors['accent'], fg='white')
        title.pack(expand=True)
        
        subtitle = tk.Label(header_frame, text="View your timetable results", 
                           font=("Segoe UI", 10), 
                           bg=self.colors['accent'], fg='white')
        subtitle.pack()
        
        # Results text area with scrollbar
        text_frame = ttk.Frame(results_frame)
        text_frame.pack(fill="both", expand=True)
        
        self.results_text = scrolledtext.ScrolledText(text_frame, wrap=tk.NONE, 
                                                      font=("Consolas", 9), 
                                                      bg=self.colors['bg_white'], 
                                                      fg=self.colors['text_dark'],
                                                      borderwidth=2,
                                                      relief='solid')
        self.results_text.pack(fill="both", expand=True)
        
        # Add horizontal scrollbar
        xscrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, 
                                   command=self.results_text.xview)
        xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.results_text.configure(xscrollcommand=xscrollbar.set)
        
        self.results_text.insert("1.0", "No schedule generated yet.\n\nClick 'Generate Timetable' in the Data Files tab.")
        self.results_text.configure(state="disabled")
        
    def create_export_tab(self):
        """Tab for exporting results"""
        export_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(export_frame, text="💾 Export")
        
        # Modern header
        header_frame = tk.Frame(export_frame, bg=self.colors['success'], height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="💾 Export Options", 
                        font=("Segoe UI", 18, "bold"), 
                        bg=self.colors['success'], fg='white')
        title.pack(expand=True)
        
        subtitle = tk.Label(header_frame, text="Save your timetable in multiple formats", 
                           font=("Segoe UI", 10), 
                           bg=self.colors['success'], fg='white')
        subtitle.pack()
        
        # CSV Export
        csv_frame = ttk.LabelFrame(export_frame, text="CSV Export", padding=15)
        csv_frame.pack(fill="x", pady=5)
        
        ttk.Label(csv_frame, text="Export schedule as CSV file for Excel/analysis").pack(anchor="w")
        ttk.Button(csv_frame, text="📄 Export to CSV", command=self.export_csv, 
                  width=30).pack(pady=5)
        
        # HTML Exports
        html_frame = ttk.LabelFrame(export_frame, text="HTML Exports", padding=15)
        html_frame.pack(fill="x", pady=5)
        
        ttk.Label(html_frame, text="Export as beautiful HTML pages:").pack(anchor="w", pady=(0, 10))
        
        btn_frame = ttk.Frame(html_frame)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="🌐 Full Schedule (HTML)", 
                  command=self.export_html_full, width=30).pack(pady=3)
        ttk.Button(btn_frame, text="📅 Weekly Grid (HTML)", 
                  command=self.export_html_grid, width=30).pack(pady=3)
        ttk.Button(btn_frame, text="👨‍🏫 Individual Instructor (HTML)", 
                  command=self.export_html_instructor, width=30).pack(pady=3)
        
        # Export all
        all_frame = ttk.LabelFrame(export_frame, text="Batch Export", padding=15)
        all_frame.pack(fill="x", pady=5)
        
        ttk.Label(all_frame, text="Export everything at once:").pack(anchor="w")
        ttk.Button(all_frame, text="📦 Export All Formats", command=self.export_all, 
                  width=30).pack(pady=5)
        
    def create_status_bar(self):
        """Create bottom status bar"""
        status_frame = tk.Frame(self.root, bg=self.colors['primary'], height=35)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="✨ Ready to create amazing timetables!", 
                                    anchor=tk.W, bg=self.colors['primary'], fg='white',
                                    font=('Segoe UI', 9, 'bold'), padx=10)
        self.status_label.pack(side=tk.LEFT, fill='both', expand=True)
        
    # Helper methods
    def browse_file(self, var):
        """Open file browser dialog - can select from anywhere on your computer"""
        # Start from the current file's directory if one is set, otherwise user's home
        initial_dir = None
        current_path = var.get()
        if current_path and os.path.exists(current_path):
            initial_dir = str(Path(current_path).parent)
        elif current_path and os.path.exists(Path(current_path).parent):
            initial_dir = str(Path(current_path).parent)
        else:
            # Try default data path if it exists
            default_data_path = Path(r"d:\projects\timetable\Data")
            if default_data_path.exists():
                initial_dir = str(default_data_path)
        
        filename = filedialog.askopenfilename(
            title="Select file (from anywhere on your computer)",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=initial_dir
        )
        if filename:
            var.set(filename)
            
    def load_data_files(self):
        """Load all data files"""
        try:
            # Validate that all file paths are provided
            instructors_path = self.instructors_path_var.get().strip()
            rooms_path = self.rooms_path_var.get().strip()
            courses_path = self.courses_path_var.get().strip()
            timeslots_path = self.timeslots_path_var.get().strip()
            
            if not instructors_path or not rooms_path or not courses_path or not timeslots_path:
                missing = []
                if not instructors_path: missing.append("Instructors")
                if not rooms_path: missing.append("Rooms")
                if not courses_path: missing.append("Courses")
                if not timeslots_path: missing.append("Timeslots")
                messagebox.showwarning("Missing Files", 
                    f"Please select all required files.\n\nMissing: {', '.join(missing)}")
                return
            
            self.status_label.config(text="Loading data files...")
            self.instructors = load_instructors_excel(instructors_path)
            self.rooms = load_rooms_excel(rooms_path)
            self.courses = load_courses_excel(courses_path)
            self.timeslots = load_timeslots_excel(timeslots_path)
            
            # Validate that data was actually loaded
            if not self.instructors or not self.rooms or not self.courses or not self.timeslots:
                raise ValueError("One or more files did not contain valid data")
            
            msg = f"✅ Loaded: {len(self.instructors)} instructors, {len(self.rooms)} rooms, " \
                  f"{len(self.courses)} courses, {len(self.timeslots)} timeslots"
            self.data_status_label.config(text=msg, foreground=self.colors['success'])
            self.animate_status("✅ Data loaded successfully!", self.colors['success'])
            messagebox.showinfo("✅ Success", msg)
        except Exception as e:
            self.data_status_label.config(text="✗ Error loading data", foreground="red")
            self.status_label.config(text="Error")
            messagebox.showerror("Error", f"Failed to load data:\n{str(e)}")
            
    def start_progress_update(self):
        """Start the progress update loop"""
        def update():
            try:
                while True:
                    nodes = self.progress_q.get_nowait()
                    self.progress_label.config(text=f"Nodes explored: {nodes:,}")
            except queue.Empty:
                pass
            self.root.after(200, update)
        
        self.root.after(200, update)
        
    def progress_callback(self, nodes):
        """Callback for progress updates"""
        try:
            self.progress_q.put(nodes)
        except Exception:
            pass
            
    def on_generate(self):
        """Generate timetable"""
        # Load data if not already loaded
        if self.instructors is None:
            try:
                self.load_data_files()
            except:
                return
                
        self.generate_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.progress_bar.start(10)
        
        # Show which algorithm is being used
        if self.use_fixed_csp.get():
            algo_name = "Fixed CSP"
        elif self.use_enhanced_csp.get():
            algo_name = "Enhanced CSP"
        else:
            algo_name = "Original CSP"
        self.progress_label.config(text=f"Starting generation ({algo_name})...")
        self.status_label.config(text=f"Generating schedule with {algo_name}...")
        self.worker_state["event"].clear()
        
        def worker():
            try:
                # Choose algorithm based on user selection
                if self.use_fixed_csp.get():
                    # Use FIXED CSP algorithm (supports multiple classes per instructor)
                    sol_list, inst_by_id, ts = generate_schedule_fixed(
                        self.instructors, 
                        self.rooms, 
                        self.timeslots, 
                        courses=self.courses,
                        stop_event=self.worker_state["event"],
                        progress_callback=self.progress_callback
                    )
                    # Convert list format to dict for compatibility
                    # Key: (instructor_id, course_id), Value: (timeslot_idx, room_id, course_id)
                    sol = {}
                    for instructor_id, timeslot_idx, room_id, course_id in sol_list:
                        # Use unique key for each assignment
                        key = f"{instructor_id}_{course_id}_{timeslot_idx}"
                        sol[key] = (timeslot_idx, room_id, course_id, instructor_id)
                    
                elif self.use_enhanced_csp.get():
                    # Use enhanced CSP algorithm
                    sol, inst_by_id, ts = generate_schedule_enhanced(
                        self.instructors, 
                        self.rooms, 
                        self.timeslots, 
                        courses=self.courses,
                        stop_event=self.worker_state["event"],
                        progress_callback=self.progress_callback,
                        use_fast_mode=True,  # Always use fast mode in GUI
                        randomize=self.randomize_var.get()
                    )
                else:
                    # Use original CSP algorithm
                    sol, inst_by_id, ts = generate_schedule_from_memory(
                        self.instructors, 
                        self.rooms, 
                        self.timeslots, 
                        courses=self.courses,
                        stop_event=self.worker_state["event"],
                        progress_callback=self.progress_callback
                    )
                
                if not sol:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Result", "No solution found or search was cancelled."))
                    self.root.after(0, lambda: self.status_label.config(text="No solution found"))
                else:
                    self.solution = sol
                    self.instructors_by_id = inst_by_id
                    self.timeslots = ts
                    self.root.after(0, self.display_results)
                    self.root.after(0, lambda: self.animate_status(
                        f"✅ Schedule generated: {len(sol)} classes scheduled!", self.colors['success']))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
                self.root.after(0, lambda: self.status_label.config(text="Error occurred"))
            finally:
                def finish_ui():
                    self.progress_bar.stop()
                    if self.use_fixed_csp.get():
                        algo_name = "🔧 Fixed CSP"
                    elif self.use_enhanced_csp.get():
                        algo_name = "✨ Enhanced CSP"
                    else:
                        algo_name = "⚡ Original CSP"
                    self.progress_label.config(text=f"Ready to generate ({algo_name})")
                    self.generate_btn.config(state="normal")
                    self.cancel_btn.config(state="disabled")
                self.root.after(0, finish_ui)
        
        self.worker_state["thread"] = threading.Thread(target=worker, daemon=True)
        self.worker_state["thread"].start()
        
    def on_cancel(self):
        """Cancel generation"""
        self.worker_state["event"].set()
        self.cancel_btn.config(state="disabled")
        self.progress_label.config(text="Cancelling...")
        self.status_label.config(text="Cancelling...")
        
    def display_results(self):
        """Display results in the results tab"""
        if not self.solution:
            return
            
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", tk.END)
        
        # Build results text
        results = []
        results.append("="*100)
        results.append(f"GENERATED TIMETABLE - {len(self.solution)} CLASSES SCHEDULED")
        results.append("="*100)
        results.append("")
        
        # Sort and display schedule
        rows = []
        for key, value in sorted(
            self.solution.items(), 
            key=lambda kv: get_proper_sort_key(kv, self.timeslots) if len(kv[1]) == 3 else (kv[1][0], kv[1][1])
        ):
            # Handle both old and new formats
            if len(value) == 4:
                # New fixed CSP format: (timeslot_idx, room_id, course_id, instructor_id)
                slot_index, room_id, course, instructor_id = value
            else:
                # Old format: (timeslot_idx, room_id, course_id) with key as instructor_id
                slot_index, room_id, course = value
                instructor_id = key
            
            instructor = self.instructors_by_id.get(instructor_id)
            if not instructor:
                continue
                
            ts = self.timeslots[slot_index]
            rows.append((
                instructor.name or instructor_id,
                instructor.instructor_id,
                ts.day,
                f"{ts.start_time}-{ts.end_time}",
                room_id,
                course
            ))
        
        # Create table
        headers = ("Instructor", "ID", "Day", "Time", "Room", "Course")
        table = [headers] + rows
        col_widths = [max(len(str(row[i])) for row in table) for i in range(len(headers))]
        
        def fmt(row):
            return " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(headers)))
        
        results.append(fmt(headers))
        results.append("-+-".join("-" * w for w in col_widths))
        for r in rows:
            results.append(fmt(r))
        
        # Statistics
        results.append("")
        results.append("="*100)
        results.append("STATISTICS")
        results.append("="*100)
        results.append(f"Total classes scheduled: {len(self.solution)}")
        
        # Day distribution
        day_dist = {}
        for key, value in self.solution.items():
            if len(value) == 4:
                slot_index = value[0]
            else:
                slot_index = value[0]
            day = self.timeslots[slot_index].day
            day_dist[day] = day_dist.get(day, 0) + 1
        
        results.append("\nDay Distribution:")
        for day, count in sorted(day_dist.items()):
            results.append(f"  {day}: {count} classes")
        
        # Room usage
        room_usage = {}
        for key, value in self.solution.items():
            if len(value) == 4:
                room_id = value[1]
            else:
                room_id = value[1]
            room_usage[room_id] = room_usage.get(room_id, 0) + 1
        
        results.append("\nRoom Usage:")
        for room, count in sorted(room_usage.items(), key=lambda x: x[1], reverse=True)[:10]:
            results.append(f"  {room}: {count} classes")
        
        self.results_text.insert("1.0", "\n".join(results))
        self.results_text.configure(state="disabled")
        
        # Switch to results tab
        self.notebook.select(2)
        
        messagebox.showinfo("Success", f"Schedule generated successfully!\n{len(self.solution)} classes scheduled.")
        
    # Export methods
    def get_results_folder(self):
        """Get or create the results folder"""
        # Use absolute path to timetable/Results folder
        results_folder = Path(r"D:\projects\timetable\Results")
        results_folder.mkdir(exist_ok=True)
        return results_folder
    
    def export_csv(self):
        """Export to CSV"""
        if not self.solution:
            messagebox.showwarning("No Data", "Please generate a schedule first.")
            return
        
        results_folder = self.get_results_folder()
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="schedule.csv",
            initialdir=str(results_folder)
        )
        
        if filename:
            try:
                write_schedule_csv(filename, self.solution, self.instructors_by_id, self.timeslots)
                messagebox.showinfo("✅ Success", f"Schedule exported to:\n{filename}")
                self.animate_status(f"✅ Exported to {Path(filename).name}", self.colors['success'])
            except Exception as e:
                messagebox.showerror("❌ Error", f"Export failed:\n{str(e)}")
                
    def export_html_full(self):
        """Export full schedule HTML"""
        if not self.solution:
            messagebox.showwarning("No Data", "Please generate a schedule first.")
            return
        
        results_folder = self.get_results_folder()
        filename = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
            initialfile="schedule_full.html",
            initialdir=str(results_folder)
        )
        
        if filename:
            try:
                export_schedule_html(self.solution, self.instructors_by_id, self.timeslots, filename)
                messagebox.showinfo("Success", f"Full schedule exported to:\n{filename}")
                self.status_label.config(text=f"Exported to {Path(filename).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")
                
    def export_html_grid(self):
        """Export grid format HTML"""
        if not self.solution:
            messagebox.showwarning("No Data", "Please generate a schedule first.")
            return
        
        results_folder = self.get_results_folder()
        filename = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
            initialfile="schedule_grid.html",
            initialdir=str(results_folder)
        )
        
        if filename:
            try:
                export_grid_html(self.solution, self.instructors_by_id, self.timeslots, filename)
                messagebox.showinfo("Success", f"Grid schedule exported to:\n{filename}")
                self.status_label.config(text=f"Exported to {Path(filename).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")
                
    def export_html_instructor(self):
        """Export individual instructor HTML"""
        if not self.solution:
            messagebox.showwarning("No Data", "Please generate a schedule first.")
            return
            
        # Create dialog to select instructor
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Instructor")
        dialog.geometry("400x500")
        
        ttk.Label(dialog, text="Select an instructor:", font=("Segoe UI", 11)).pack(pady=10)
        
        # Listbox with scrollbar
        frame = ttk.Frame(dialog)
        frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=("Segoe UI", 10))
        listbox.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Populate listbox
        instructor_ids = sorted(self.instructors_by_id.keys())
        for iid in instructor_ids:
            inst = self.instructors_by_id[iid]
            listbox.insert(tk.END, f"{inst.name} ({iid})")
        
        def on_export():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select an instructor.")
                return
                
            instructor_id = instructor_ids[selection[0]]
            instructor = self.instructors_by_id[instructor_id]
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
                initialfile=f"schedule_{instructor.name.replace(' ', '_')}.html"
            )
            
            if filename:
                try:
                    export_instructor_html(instructor_id, self.solution, 
                                          self.instructors_by_id, self.timeslots, filename)
                    messagebox.showinfo("Success", f"Instructor schedule exported to:\n{filename}")
                    self.status_label.config(text=f"Exported to {Path(filename).name}")
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Export failed:\n{str(e)}")
        
        ttk.Button(dialog, text="Export Selected", command=on_export, width=20).pack(pady=10)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy, width=20).pack()
        
    def export_all(self):
        """Export all formats"""
        if not self.solution:
            messagebox.showwarning("No Data", "Please generate a schedule first.")
            return
        
        results_folder = self.get_results_folder()
        directory = filedialog.askdirectory(
            title="Select directory for exports",
            initialdir=str(results_folder)
        )
        
        if directory:
            try:
                base_path = Path(directory)
                
                # CSV
                write_schedule_csv(str(base_path / "schedule.csv"), 
                                  self.solution, self.instructors_by_id, self.timeslots)
                
                # HTML Full
                export_schedule_html(self.solution, self.instructors_by_id, 
                                    self.timeslots, str(base_path / "schedule_full.html"))
                
                # HTML Grid
                export_grid_html(self.solution, self.instructors_by_id, 
                                self.timeslots, str(base_path / "schedule_grid.html"))
                
                # Individual instructors
                instructors_dir = base_path / "instructors"
                instructors_dir.mkdir(exist_ok=True)
                
                for instructor_id in self.instructors_by_id.keys():
                    instructor = self.instructors_by_id[instructor_id]
                    safe_name = instructor.name.replace(' ', '_').replace('/', '_')
                    export_instructor_html(
                        instructor_id, self.solution, self.instructors_by_id, 
                        self.timeslots, 
                        str(instructors_dir / f"{safe_name}.html")
                    )
                
                messagebox.showinfo("✅ Success", 
                    f"All exports completed!\n\nFiles saved to:\n{directory}\n\n"
                    f"• schedule.csv\n"
                    f"• schedule_full.html\n"
                    f"• schedule_grid.html\n"
                    f"• instructors/ (individual HTML files)")
                self.animate_status("✅ All formats exported successfully", self.colors['success'])
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")


def run_gui():
    """Main entry point for the GUI"""
    root = tk.Tk()
    app = TimetableGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
