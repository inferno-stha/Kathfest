"""
==========================================================
Project:
    Smart Student Attendance System

File:
    login.py

Purpose:
    Displays the Login screen that appears before the main
    application opens. Validates dummy credentials and, on
    success, closes itself and launches the main app window.

Author:
    Hackathon Team

Version:
    1.0

Date:
    2026

Dependencies:
    tkinter
    tkinter.ttk
    tkinter.messagebox
==========================================================
"""

# We import "tkinter" to build the graphical interface (windows,
# labels, buttons, text fields, etc.). It comes built into Python,
# so no extra installation is required.
import tkinter as tk

# "ttk" (Themed Tkinter) gives us more modern-looking widgets than
# plain tkinter, such as ttk.Entry and ttk.Button with nicer styling.
from tkinter import ttk

# "messagebox" lets us show popup dialogs (errors, warnings,
# confirmations) without building our own popup windows manually.
from tkinter import messagebox

# Import our shared color/font constants so the login screen
# matches the rest of the application visually.
import styles


# ==========================================================
# Class: LoginWindow
#
# Purpose:
#     Builds and manages the Login screen UI.
#
# Responsibility:
#     - Show username/password fields.
#     - Validate dummy credentials (admin / admin).
#     - On success, close the login window and start the
#       main application (app.py).
#
# When it is used:
#     LoginWindow is created once, when main.py starts the
#     program. It is the very first thing the user sees.
#
# Future Integration:
#     Database/Backend developer will replace the dummy
#     credential check inside `attempt_login()` with a real
#     authentication call (e.g. checking a users table in
#     SQLite, or hashing passwords).
# ==========================================================
class LoginWindow:
    def __init__(self, root, on_success):
        """
        Set up the Login window.

        Args:
            root: The single shared Tk() instance created in
                  main.py. We NEVER create a second Tk() window;
                  every screen in this app reuses this same root
                  window and just changes what is displayed on it.
            on_success: A function (callback) that main.py gives
                  us. We call this function after a successful
                  login so that main.py knows it's time to launch
                  the main application window.
        """
        self.root = root
        self.on_success = on_success

        # Give the window a title shown in the OS title bar.
        self.root.title("Smart Student Attendance System - Login")

        # Fix the login window to a comfortable, centered size.
        self.root.geometry("450x540")
        self.root.configure(bg=styles.BACKGROUND_COLOR)

        # StringVar is a special Tkinter variable type. Unlike a
        # normal Python variable, a StringVar is "watched" by
        # Tkinter widgets. When you link an Entry field to a
        # StringVar, typing in the field automatically updates
        # the variable, and changing the variable in code
        # automatically updates the field. This makes it easy to
        # read/write widget text without manually querying widgets.
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        # BooleanVar works the same way as StringVar, but stores
        # True/False. We use it for the "Show Password" checkbox.
        self.show_password_var = tk.BooleanVar(value=False)

        # Build all the visual widgets for this screen.
        self._build_ui()

    # ------------------------------------------------------------
    # Function: _build_ui()
    #
    # Purpose:
    #     Creates and arranges every widget on the login screen.
    #
    # Called When:
    #     Once, automatically, from __init__() when the
    #     LoginWindow object is created.
    #
    # How it works:
    #     All login widgets are wrapped inside one container Frame.
    #     The root window uses grid() with equal row/column weights
    #     so the container sits at the exact center (both horizontally
    #     and vertically). No extra padding pushes it off-center.
    # ------------------------------------------------------------
    def _build_ui(self):
        # Configure root grid so the container is centered
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # ---- Centered container ----
        # One Frame holds ALL login content. Grid centers it
        # automatically because the cell is larger than the frame.
        container = tk.Frame(self.root, bg=styles.BACKGROUND_COLOR)
        container.grid(row=0, column=0)

        # ---- Title Section ----
        title_label = tk.Label(
            container,
            text=f"{styles.ICON_APP} Smart Attendance System",
            font=styles.FONT_TITLE,
            bg=styles.BACKGROUND_COLOR,
            fg=styles.TEXT_COLOR,
            wraplength=380,
            justify="center",
        )
        title_label.pack(pady=(0, 0))

        subtitle_label = tk.Label(
            container,
            text="Face Recognition Based Attendance",
            font=styles.FONT_SUBTITLE,
            bg=styles.BACKGROUND_COLOR,
            fg=styles.MUTED_TEXT_COLOR,
        )
        subtitle_label.pack(pady=(6, 20))

        # ---- Card that holds the login form ----
        card = tk.Frame(
            container,
            bg=styles.CARD_COLOR,
            highlightbackground=styles.BORDER_COLOR,
            highlightthickness=1,
        )
        card.pack(fill="x")

        form_inner = tk.Frame(card, bg=styles.CARD_COLOR)
        form_inner.pack(fill="x", padx=25, pady=22)

        # ---- Username field ----
        username_label = tk.Label(
            form_inner,
            text="Username",
            font=styles.FONT_BODY_BOLD,
            bg=styles.CARD_COLOR,
            fg=styles.TEXT_COLOR,
            anchor="w",
        )
        username_label.pack(fill="x")

        username_entry = ttk.Entry(
            form_inner, textvariable=self.username_var, font=styles.FONT_BODY, width=28
        )
        username_entry.pack(fill="x", pady=(5, 14), ipady=5)
        username_entry.focus()

        # ---- Password field ----
        password_label = tk.Label(
            form_inner,
            text="Password",
            font=styles.FONT_BODY_BOLD,
            bg=styles.CARD_COLOR,
            fg=styles.TEXT_COLOR,
            anchor="w",
        )
        password_label.pack(fill="x")

        self.password_entry = ttk.Entry(
            form_inner,
            textvariable=self.password_var,
            font=styles.FONT_BODY,
            show="*",
            width=28,
        )
        self.password_entry.pack(fill="x", pady=(5, 10), ipady=5)

        # ---- Show Password checkbox ----
        show_password_check = ttk.Checkbutton(
            form_inner,
            text="Show Password",
            variable=self.show_password_var,
            command=self._toggle_password_visibility,
        )
        show_password_check.pack(anchor="w", pady=(0, 18))

        # ---- Login button (full width inside the card) ----
        login_button = tk.Button(
            form_inner,
            text="Login",
            font=styles.FONT_BUTTON,
            bg=styles.BUTTON_COLOR,
            fg=styles.BUTTON_TEXT_COLOR,
            activebackground=styles.BUTTON_HOVER_COLOR,
            activeforeground=styles.BUTTON_TEXT_COLOR,
            relief="flat",
            cursor="hand2",
            command=self.attempt_login,
        )
        login_button.pack(fill="x", ipady=8)

        self.root.bind("<Return>", lambda event: self.attempt_login())

        # ---- Exit button (below the card, inside the container) ----
        exit_button = tk.Button(
            container,
            text="Exit",
            font=styles.FONT_BUTTON,
            bg=styles.DANGER_COLOR,
            fg=styles.BUTTON_TEXT_COLOR,
            activebackground="#B32734",
            activeforeground=styles.BUTTON_TEXT_COLOR,
            relief="flat",
            cursor="hand2",
            command=self.root.destroy,
        )
        exit_button.pack(fill="x", pady=(12, 0), ipady=6)

        # ---- Centered demo credentials hint ----
        hint_label = tk.Label(
            container,
            text="Demo credentials \u2192 Username: admin | Password: admin",
            font=("Segoe UI", 9),
            bg=styles.BACKGROUND_COLOR,
            fg=styles.MUTED_TEXT_COLOR,
        )
        hint_label.pack(pady=(14, 0))

    # ------------------------------------------------------------
    # Function: _toggle_password_visibility()
    #
    # Purpose:
    #     Shows or hides the password text depending on whether
    #     the "Show Password" checkbox is ticked.
    #
    # Called When:
    #     The user clicks the "Show Password" checkbox.
    # ------------------------------------------------------------
    def _toggle_password_visibility(self):
        if self.show_password_var.get():
            # Empty string means "show every character normally".
            self.password_entry.config(show="")
        else:
            # "*" masks every typed character again.
            self.password_entry.config(show="*")

    # ------------------------------------------------------------
    # Function: attempt_login()
    #
    # Purpose:
    #     Checks the entered username/password against dummy
    #     credentials and either proceeds to the main app or
    #     shows an error message.
    #
    # Called When:
    #     The user clicks "Login" or presses Enter.
    #
    # Future Integration:
    #     Database developer should replace the hard-coded
    #     "admin"/"admin" check below with a real lookup against
    #     a users table (ideally with hashed passwords).
    # ------------------------------------------------------------
    def attempt_login(self):
        """
        Validates the username and password.

        Current Version:
            Uses dummy hard-coded credentials (admin / admin).

        Future Version:
            Backend/Database developer will replace this with
            real authentication (e.g. SQLite lookup + password
            hashing).
        """
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if username == "admin" and password == "admin":
            # Unbind the Enter key so it doesn't linger and
            # accidentally trigger something on the next screen.
            self.root.unbind("<Return>")

            # Remove every widget currently on the root window.
            # This is how we "switch screens" using a SINGLE Tk()
            # window instead of opening a second window.
            for widget in self.root.winfo_children():
                widget.destroy()

            # Tell main.py that login succeeded so it can build
            # the main application UI on this same root window.
            self.on_success()
        else:
            # messagebox.showerror() pops up a small OS-native
            # error dialog. It's the simplest way to alert users
            # to problems without building a custom popup.
            messagebox.showerror(
                "Login Failed", "Invalid username or password. Please try again."
            )
