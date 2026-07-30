"""app.py - Main application window (Sidebar + Header + Pages)."""

import tkinter as tk
from tkinter import ttk, messagebox
import styles


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Student Attendance System")
        self.root.geometry(f"{styles.WINDOW_WIDTH}x{styles.WINDOW_HEIGHT}")
        self.root.configure(bg=styles.BACKGROUND_COLOR)
        self.root.minsize(950, 600)

        # Dummy data - Database Developer will replace with real queries.
        self.students_data = [
            ("S001", "Aarav Sharma", "R101", "Computer Science", "2nd"),
            ("S002", "Priya Nair", "R102", "Electronics", "4th"),
            ("S003", "Rohan Gupta", "R103", "Computer Science", "6th"),
            ("S004", "Sneha Iyer", "R104", "Mechanical", "8th"),
            ("S005", "Karan Verma", "R105", "Civil", "2nd"),
        ]
        self.attendance_data = [
            ("Aarav Sharma", "09:01 AM", "Present"),
            ("Priya Nair", "09:02 AM", "Present"),
            ("Rohan Gupta", "--", "Absent"),
            ("Sneha Iyer", "09:05 AM", "Present"),
            ("Karan Verma", "--", "Absent"),
        ]

        self.pages = {
            "Dashboard": self.show_dashboard,
            "Students": self.show_students,
            "Attendance": self.show_attendance,
            "Reports": self.show_reports,
            "About": self.show_about,
        }

        self._build_layout()
        self.show_dashboard()

    # ---------------- Layout ----------------

    def _build_layout(self):
        self.sidebar = tk.Frame(self.root, bg=styles.SIDEBAR_COLOR, width=styles.SIDEBAR_WIDTH)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        right = tk.Frame(self.root, bg=styles.BACKGROUND_COLOR)
        right.pack(side="left", fill="both", expand=True)

        self.header = tk.Frame(right, bg=styles.CARD_COLOR, height=60)
        self.header.pack(side="top", fill="x")
        self.header.pack_propagate(False)
        self._build_header()

        self.content_area = tk.Frame(right, bg=styles.BACKGROUND_COLOR)
        self.content_area.pack(side="top", fill="both", expand=True)

    def _build_sidebar(self):
        tk.Label(
            self.sidebar, text=f"{styles.ICON_APP}  Attendance", font=styles.FONT_HEADING,
            bg=styles.SIDEBAR_COLOR, fg=styles.SIDEBAR_TEXT_COLOR, pady=25,
        ).pack(fill="x")

        nav_items = [
            ("Dashboard", styles.ICON_DASHBOARD), ("Students", styles.ICON_STUDENTS),
            ("Attendance", styles.ICON_ATTENDANCE), ("Reports", styles.ICON_REPORTS),
            ("About", styles.ICON_ABOUT),
        ]
        self.nav_buttons = {}
        for label, icon in nav_items:
            btn = self._sidebar_button(f"  {icon}   {label}", styles.SIDEBAR_TEXT_COLOR,
                                        lambda l=label: self.switch_page(l))
            self.nav_buttons[label] = btn

        tk.Frame(self.sidebar, bg=styles.SIDEBAR_COLOR).pack(fill="both", expand=True)  # spacer
        self._sidebar_button(f"  {styles.ICON_LOGOUT}   Logout", styles.DANGER_COLOR, self.logout)

    def _sidebar_button(self, text, fg, command):
        btn = tk.Button(
            self.sidebar, text=text, font=styles.FONT_SIDEBAR, bg=styles.SIDEBAR_COLOR, fg=fg,
            activebackground=styles.SIDEBAR_HOVER_COLOR, activeforeground=fg, bd=0, anchor="w",
            relief="flat", cursor="hand2", command=command,
        )
        btn.pack(fill="x", ipady=10, pady=1)
        return btn

    def _build_header(self):
        self.page_title_label = tk.Label(
            self.header, text="Dashboard", font=styles.FONT_HEADING,
            bg=styles.CARD_COLOR, fg=styles.TEXT_COLOR,
        )
        self.page_title_label.pack(side="left", padx=25)
        tk.Label(
            self.header, text="👤 Welcome, Admin", font=styles.FONT_BODY,
            bg=styles.CARD_COLOR, fg=styles.MUTED_TEXT_COLOR,
        ).pack(side="right", padx=25)

    def switch_page(self, page_name):
        for widget in self.content_area.winfo_children():
            widget.destroy()
        self.page_title_label.config(text=page_name)
        for label, btn in self.nav_buttons.items():
            btn.config(bg=styles.SIDEBAR_HOVER_COLOR if label == page_name else styles.SIDEBAR_COLOR)
        self.pages[page_name]()

    # ---------------- Helpers ----------------

    def _make_card(self, parent, **pack_options):
        card = tk.Frame(parent, bg=styles.CARD_COLOR, highlightbackground=styles.BORDER_COLOR,
                         highlightthickness=1)
        card.pack(**pack_options)
        return card

    def _stat_card(self, parent, label_text, value_text, accent_color):
        card = self._make_card(parent, side="left", fill="both", expand=True, padx=8)
        tk.Frame(card, bg=accent_color, height=4).pack(fill="x")
        inner = tk.Frame(card, bg=styles.CARD_COLOR)
        inner.pack(fill="both", expand=True, padx=20, pady=18)
        tk.Label(inner, text=value_text, font=styles.FONT_STAT_NUMBER,
                 bg=styles.CARD_COLOR, fg=styles.TEXT_COLOR).pack(anchor="w")
        tk.Label(inner, text=label_text, font=styles.FONT_STAT_LABEL,
                 bg=styles.CARD_COLOR, fg=styles.MUTED_TEXT_COLOR).pack(anchor="w")

    def _action_button(self, parent, text, color, command, **pack_options):
        tk.Button(
            parent, text=text, font=styles.FONT_BUTTON, bg=color, fg=styles.BUTTON_TEXT_COLOR,
            activebackground=styles.BUTTON_HOVER_COLOR, activeforeground=styles.BUTTON_TEXT_COLOR,
            relief="flat", cursor="hand2", command=command,
        ).pack(**pack_options)

    def _make_table(self, parent, columns, headings, rows, height=10):
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=height)
        for col, text in zip(columns, headings):
            tree.heading(col, text=text)
            tree.column(col, anchor="w", width=150)
        for row in rows:
            tree.insert("", "end", values=row)
        return tree

    # ---------------- Pages ----------------

    def show_dashboard(self):
        wrapper = tk.Frame(self.content_area, bg=styles.BACKGROUND_COLOR)
        wrapper.pack(fill="both", expand=True, padx=25, pady=20)

        tk.Label(wrapper, text="Welcome back, Admin! 👋", font=styles.FONT_TITLE,
                 bg=styles.BACKGROUND_COLOR, fg=styles.TEXT_COLOR, anchor="w").pack(fill="x")
        tk.Label(wrapper, text="Here's a quick overview of today's attendance activity.",
                 font=styles.FONT_SUBTITLE, bg=styles.BACKGROUND_COLOR,
                 fg=styles.MUTED_TEXT_COLOR, anchor="w").pack(fill="x", pady=(0, 20))

        total = len(self.students_data)
        present = sum(1 for row in self.attendance_data if row[2] == "Present")
        pct = round((present / total) * 100, 1) if total else 0

        stats_row = tk.Frame(wrapper, bg=styles.BACKGROUND_COLOR)
        stats_row.pack(fill="x")
        for label, value, color in [
            ("Total Students", str(total), styles.BUTTON_COLOR),
            ("Present Today", str(present), styles.SUCCESS_COLOR),
            ("Attendance %", f"{pct}%", styles.WARNING_COLOR),
        ]:
            self._stat_card(stats_row, label, value, color)

        tk.Label(wrapper, text="Quick Actions", font=styles.FONT_HEADING,
                 bg=styles.BACKGROUND_COLOR, fg=styles.TEXT_COLOR, anchor="w").pack(fill="x", pady=(25, 10))
        actions_row = tk.Frame(wrapper, bg=styles.BACKGROUND_COLOR)
        actions_row.pack(fill="x")
        for text, page in [
            (f"{styles.ICON_STUDENTS} Students", "Students"),
            (f"{styles.ICON_ATTENDANCE} Attendance", "Attendance"),
            (f"{styles.ICON_REPORTS} Reports", "Reports"),
        ]:
            self._action_button(actions_row, text, styles.BUTTON_COLOR,
                                 lambda p=page: self.switch_page(p),
                                 side="left", padx=(0, 12), ipadx=15, ipady=10)

    def show_students(self):
        wrapper = tk.Frame(self.content_area, bg=styles.BACKGROUND_COLOR)
        wrapper.pack(fill="both", expand=True, padx=25, pady=20)

        filter_row = tk.Frame(wrapper, bg=styles.BACKGROUND_COLOR)
        filter_row.pack(fill="x", pady=(0, 15))

        departments = ["All Departments"] + sorted(set(r[3] for r in self.students_data))
        semesters = ["All Semesters"] + sorted(set(r[4] for r in self.students_data))

        tk.Label(filter_row, text="Department", font=styles.FONT_BODY,
                 bg=styles.BACKGROUND_COLOR, fg=styles.TEXT_COLOR).pack(side="left", padx=(0, 5))
        self.dept_var = tk.StringVar(value="All Departments")
        dept_combo = ttk.Combobox(filter_row, textvariable=self.dept_var, font=styles.FONT_BODY,
                                   state="readonly", width=18)
        dept_combo['values'] = departments
        dept_combo.pack(side="left", padx=(0, 15))
        dept_combo.bind("<<ComboboxSelected>>", lambda e: self._filter_students())

        tk.Label(filter_row, text="Semester", font=styles.FONT_BODY,
                 bg=styles.BACKGROUND_COLOR, fg=styles.TEXT_COLOR).pack(side="left", padx=(0, 5))
        self.sem_var = tk.StringVar(value="All Semesters")
        sem_combo = ttk.Combobox(filter_row, textvariable=self.sem_var, font=styles.FONT_BODY,
                                  state="readonly", width=12)
        sem_combo['values'] = semesters
        sem_combo.pack(side="left", padx=(0, 15))
        sem_combo.bind("<<ComboboxSelected>>", lambda e: self._filter_students())

        tk.Label(filter_row, text="🔍", bg=styles.BACKGROUND_COLOR).pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(filter_row, textvariable=self.search_var, font=styles.FONT_BODY,
                                 fg="grey", relief="solid", bd=1)
        search_entry.pack(side="left", fill="x", expand=True, ipady=4)
        search_entry.insert(0, "Search by Student Name or Roll_No.")
        search_entry.bind("<FocusIn>", lambda e: (search_entry.delete(0, "end"), search_entry.config(fg="black"))
                          if search_entry.get() == "Search by Student Name or Roll_No." else None)
        search_entry.bind("<FocusOut>", lambda e: (search_entry.insert(0, "Search by Student Name or Roll_No."),
                          search_entry.config(fg="grey")) if not search_entry.get() else None)
        search_entry.bind("<KeyRelease>", lambda e: self._filter_students())

        table_row = tk.Frame(wrapper, bg=styles.BACKGROUND_COLOR)
        table_row.pack(fill="both", expand=True)
        columns = ("id", "name", "roll", "department", "semester")
        headings = ("Student ID", "Name", "Roll Number", "Department", "Semester")
        self.students_tree = self._make_table(table_row, columns, headings, self.students_data, height=12)
        scrollbar = ttk.Scrollbar(table_row, orient="vertical", command=self.students_tree.yview)
        self.students_tree.configure(yscrollcommand=scrollbar.set)
        self.students_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")

        button_row = tk.Frame(wrapper, bg=styles.BACKGROUND_COLOR)
        button_row.pack(fill="x", pady=(15, 0))
        for text, color, command in [
            ("➕ Add Student", styles.BUTTON_COLOR, self.save_student),
            ("🗑 Delete Student", styles.DANGER_COLOR, self.delete_student),
            (f"{styles.ICON_ATTENDANCE} Capture Face", styles.SUCCESS_COLOR, self.capture_face),
        ]:
            self._action_button(button_row, text, color, command,
                                 side="left", padx=(0, 10), ipadx=12, ipady=8)

    def _filter_students(self):
        dept = self.dept_var.get()
        sem = self.sem_var.get()
        query = self.search_var.get().strip().lower()
        placeholder = "search by student name or roll_no."

        rows = self.students_data
        if dept != "All Departments":
            rows = [r for r in rows if r[3] == dept]
        if sem != "All Semesters":
            rows = [r for r in rows if r[4] == sem]
        if query and query != placeholder:
            rows = [r for r in rows if query in r[1].lower() or query in r[2].lower()]

        self.students_tree.delete(*self.students_tree.get_children())
        for row in rows:
            self.students_tree.insert("", "end", values=row)

    def show_attendance(self):
        wrapper = tk.Frame(self.content_area, bg=styles.BACKGROUND_COLOR)
        wrapper.pack(fill="both", expand=True, padx=25, pady=20)

        top_row = tk.Frame(wrapper, bg=styles.BACKGROUND_COLOR)
        top_row.pack(fill="x")

        camera_card = self._make_card(top_row, side="left", padx=(0, 15))
        canvas = tk.Canvas(camera_card, width=380, height=260, bg="#0F1B33", highlightthickness=0)
        canvas.pack(padx=15, pady=15)
        canvas.create_text(190, 130, text=f"{styles.ICON_ATTENDANCE}\nCamera Preview\n(Not Connected)",
                            fill="white", font=styles.FONT_BODY_BOLD, justify="center")

        controls = tk.Frame(top_row, bg=styles.BACKGROUND_COLOR)
        controls.pack(side="left", fill="y")
        tk.Label(controls, text="Camera Controls", font=styles.FONT_HEADING,
                 bg=styles.BACKGROUND_COLOR, fg=styles.TEXT_COLOR).pack(anchor="w", pady=(0, 10))
        self._action_button(controls, "▶ Start Camera", styles.BUTTON_COLOR, self.start_camera,
                             fill="x", ipady=10, pady=(0, 10))
        self._action_button(controls, "✅ Mark Attendance", styles.SUCCESS_COLOR, self.mark_attendance,
                             fill="x", ipady=10)

        tk.Label(wrapper, text="Today's Attendance", font=styles.FONT_HEADING,
                 bg=styles.BACKGROUND_COLOR, fg=styles.TEXT_COLOR).pack(anchor="w", pady=(20, 10))
        table = self._make_table(wrapper, ("student", "time", "status"),
                                  ("Student", "Time", "Status"), self.attendance_data, height=8)
        table.pack(fill="both", expand=True)

    def show_reports(self):
        wrapper = tk.Frame(self.content_area, bg=styles.BACKGROUND_COLOR)
        wrapper.pack(fill="both", expand=True, padx=25, pady=20)

        total = len(self.students_data)
        present = sum(1 for row in self.attendance_data if row[2] == "Present")
        absent = total - present

        stats_row = tk.Frame(wrapper, bg=styles.BACKGROUND_COLOR)
        stats_row.pack(fill="x", pady=(0, 20))
        for label, value, color in [
            ("Total Students", str(total), styles.BUTTON_COLOR),
            ("Present Students", str(present), styles.SUCCESS_COLOR),
            ("Absent Students", str(absent), styles.DANGER_COLOR),
        ]:
            self._stat_card(stats_row, label, value, color)

        self._action_button(wrapper, f"{styles.ICON_REPORTS} Export CSV", styles.BUTTON_COLOR,
                             self.export_csv, anchor="w", ipadx=15, ipady=8)

    def show_about(self):
        wrapper = tk.Frame(self.content_area, bg=styles.BACKGROUND_COLOR)
        wrapper.pack(fill="both", expand=True, padx=25, pady=20)
        card = self._make_card(wrapper, fill="both", expand=True)
        inner = tk.Frame(card, bg=styles.CARD_COLOR)
        inner.pack(padx=30, pady=30, anchor="nw")

        tk.Label(inner, text=f"{styles.ICON_APP} Smart Student Attendance System",
                 font=styles.FONT_TITLE, bg=styles.CARD_COLOR, fg=styles.TEXT_COLOR).pack(anchor="w")
        tk.Label(inner, text="Version 1.0", font=styles.FONT_BODY_BOLD,
                 bg=styles.CARD_COLOR, fg=styles.MUTED_TEXT_COLOR).pack(anchor="w", pady=(5, 15))
        tk.Label(
            inner,
            text=("An automated attendance system that uses face recognition\n"
                  "to identify students and record their attendance, removing\n"
                  "the need for manual roll calls. Built for a hackathon to\n"
                  "demonstrate a full-stack desktop application workflow."),
            font=styles.FONT_BODY, bg=styles.CARD_COLOR, fg=styles.TEXT_COLOR, justify="left",
        ).pack(anchor="w", pady=(0, 20))

        tk.Label(inner, text="Team Members", font=styles.FONT_HEADING,
                 bg=styles.CARD_COLOR, fg=styles.TEXT_COLOR).pack(anchor="w", pady=(0, 8))
        for member in [
            "Frontend Developer - Tkinter UI (this codebase)",
            "Backend Developer - Camera & Face Recognition",
            "Database Developer - SQLite Integration",
            "Integration Developer - Connecting all modules",
        ]:
            tk.Label(inner, text=f"• {member}", font=styles.FONT_BODY,
                     bg=styles.CARD_COLOR, fg=styles.TEXT_COLOR).pack(anchor="w")

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout and close the application?"):
            self.root.destroy()

    # ---------------- Placeholders ----------------
    # Hook points for the rest of the team. Each shows a "coming soon"
    # popup for now so every button stays clickable during the demo.

    def load_students(self):
        """Database Developer: replace with a real SELECT query."""
        self._filter_students()

    def save_student(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Student")
        dialog.geometry("400x320")
        dialog.configure(bg=styles.CARD_COLOR)
        dialog.transient(self.root)
        dialog.grab_set()

        fields = ["Student ID", "Name", "Roll Number", "Department", "Semester"]
        entries = {}
        for i, label in enumerate(fields):
            tk.Label(dialog, text=label, font=styles.FONT_BODY,
                     bg=styles.CARD_COLOR, fg=styles.TEXT_COLOR).grid(row=i, column=0, padx=15, pady=8, sticky="w")
            entry = ttk.Entry(dialog, font=styles.FONT_BODY, width=30)
            entry.grid(row=i, column=1, padx=(0, 15), pady=8)
            entries[label] = entry

        def do_save():
            sid = entries["Student ID"].get().strip()
            name = entries["Name"].get().strip()
            roll = entries["Roll Number"].get().strip()
            dept = entries["Department"].get().strip()
            sem = entries["Semester"].get().strip()
            if not all([sid, name, roll, dept, sem]):
                messagebox.showwarning("Validation", "All fields are required.", parent=dialog)
                return
            for s in self.students_data:
                if s[0].lower() == sid.lower():
                    messagebox.showerror("Duplicate Entry", f"Student ID '{sid}' already exists!", parent=dialog)
                    return
                if s[2].lower() == roll.lower():
                    messagebox.showerror("Duplicate Entry", f"Roll Number '{roll}' already exists!", parent=dialog)
                    return
            self.students_data.append((sid, name, roll, dept, sem))
            self._filter_students()
            dialog.destroy()
            messagebox.showinfo("Success", f"Student '{name}' added successfully.")

        tk.Button(dialog, text="Save", font=styles.FONT_BUTTON, bg=styles.BUTTON_COLOR,
                  fg=styles.BUTTON_TEXT_COLOR, activebackground=styles.BUTTON_HOVER_COLOR,
                  relief="flat", cursor="hand2", command=do_save).grid(row=len(fields), column=0, columnspan=2, pady=20)

    def delete_student(self):
        """Database Developer: DELETE the selected row from the database."""
        messagebox.showinfo("Delete Student", "This feature is coming soon!")

    def capture_face(self):
        """Backend Developer: capture a face image and save its encoding."""
        messagebox.showinfo("Capture Face", "This feature is coming soon!")

    def start_camera(self):
        """Backend Developer: open OpenCV VideoCapture and stream to the preview."""
        messagebox.showinfo("Start Camera", "Camera integration coming soon!")

    def recognize_face(self):
        """Backend Developer: match a live frame against stored face encodings."""
        pass

    def mark_attendance(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Mark Attendance")
        dialog.geometry("350x200")
        dialog.configure(bg=styles.CARD_COLOR)
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="Select Student", font=styles.FONT_BODY,
                 bg=styles.CARD_COLOR, fg=styles.TEXT_COLOR).pack(pady=(15, 5))
        student_names = [f"{s[1]} ({s[0]})" for s in self.students_data]
        var = tk.StringVar()
        combo = ttk.Combobox(dialog, textvariable=var, font=styles.FONT_BODY,
                              state="readonly", width=35)
        combo['values'] = student_names
        combo.pack(pady=5)

        def do_mark():
            selected = var.get()
            if not selected:
                messagebox.showwarning("Validation", "Please select a student.", parent=dialog)
                return
            name = selected.split(" (")[0]
            for a in self.attendance_data:
                if a[0] == name and a[2] == "Present":
                    messagebox.showerror("Already Marked", f"'{name}' is already marked present!", parent=dialog)
                    return
            import datetime
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M %p")
            self.attendance_data.append((name, time_str, "Present"))
            dialog.destroy()
            messagebox.showinfo("Success", f"Attendance marked for '{name}'.")
            self.show_attendance()

        tk.Button(dialog, text="Mark Present", font=styles.FONT_BUTTON, bg=styles.SUCCESS_COLOR,
                  fg=styles.BUTTON_TEXT_COLOR, activebackground=styles.BUTTON_HOVER_COLOR,
                  relief="flat", cursor="hand2", command=do_mark).pack(pady=20)

    def export_csv(self):
        """Backend Developer: export attendance records using the csv module."""
        messagebox.showinfo("Export CSV", "CSV export coming soon!")
