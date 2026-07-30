"""
==========================================================
Project:
    Smart Student Attendance System

File:
    main.py

Purpose:
    The single entry point of the application. Running this
    file is the ONLY way this program should be started.

    Why does this file exist?
    --------------------------
    It creates the ONE AND ONLY Tk() window used by the whole
    app, shows the Login screen first, and then hands control
    over to the main application (app.py) once login succeeds.
    Keeping this logic in its own tiny file makes the program's
    startup flow obvious at a glance.

Author:
    Hackathon Team

Version:
    1.0

Date:
    2026

Dependencies:
    tkinter
    login.py
    app.py
==========================================================
"""

# tkinter is required to create the root application window.
import tkinter as tk

# Import our two custom screens. LoginWindow builds the login
# UI; MainApp builds the sidebar/header/pages UI. Both reuse the
# SAME root window instead of creating their own.
from login import LoginWindow
from app import MainApp


# ------------------------------------------------------------
# Function: launch_main_app()
#
# Purpose:
#     Callback passed into LoginWindow. Called automatically
#     after a successful login to build the main app UI on the
#     same root window that the login screen just cleared.
#
# Called When:
#     LoginWindow.attempt_login() succeeds.
# ------------------------------------------------------------
def launch_main_app():
    MainApp(root)


# ------------------------------------------------------------
# Program entry point.
#
# The "if __name__ == '__main__':" guard ensures this block
# only runs when main.py is executed directly (e.g. via
# `python main.py`), not if it's ever imported by another file.
# ------------------------------------------------------------
if __name__ == "__main__":
    # Create the ONE Tk() instance for the entire application.
    # Every screen (login, dashboard, students, etc.) will draw
    # itself onto this same window. We never call tk.Tk() again
    # anywhere else in the project.
    root = tk.Tk()

    # Show the login screen first. We pass launch_main_app as the
    # "on_success" callback so LoginWindow can hand control back
    # to us once the user logs in successfully.
    LoginWindow(root, on_success=launch_main_app)

    # mainloop() starts Tkinter's event loop, which listens for
    # user actions (clicks, key presses, etc.) and keeps the
    # window open until it is closed. This call blocks here until
    # the window is destroyed.
    root.mainloop()
