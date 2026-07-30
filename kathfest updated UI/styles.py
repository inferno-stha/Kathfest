"""
==========================================================
Project:
    Smart Student Attendance System

File:
    styles.py

Purpose:
    Central place for all colors, fonts, and sizing
    constants used across the entire application.

    Why does this file exist?
    --------------------------
    Instead of typing color codes like "#1B2A4A" in every
    single file, we define them ONCE here and import them
    everywhere else. This is a common professional practice
    called "single source of truth". If a teammate wants to
    change the theme color, they only need to edit this file
    instead of hunting through every page.

Author:
    Hackathon Team

Version:
    1.0

Date:
    2026

Dependencies:
    None (pure Python constants)
==========================================================
"""

# ----------------------------------------------------------
# COLOR PALETTE
#
# We keep all colors as hex strings (the same format used
# in CSS / design tools). Grouping them by "role" (sidebar,
# button, background, etc.) instead of by literal color name
# makes it obvious WHERE each color is used in the UI.
# ----------------------------------------------------------

# Dark blue used for the sidebar background
SIDEBAR_COLOR = "#1B2A4A"

# Slightly lighter blue used when a sidebar button is hovered
SIDEBAR_HOVER_COLOR = "#28406e"

# Text color for sidebar buttons (white so it's readable on dark blue)
SIDEBAR_TEXT_COLOR = "#FFFFFF"

# Main blue used for primary action buttons (Login, Add Student, etc.)
BUTTON_COLOR = "#2E5CE6"

# Darker blue shown when a button is pressed/hovered
BUTTON_HOVER_COLOR = "#1E45B8"

# Text color used on top of blue buttons
BUTTON_TEXT_COLOR = "#FFFFFF"

# Light grey used for the main content background
BACKGROUND_COLOR = "#F2F3F7"

# White used for "cards" (dashboard stat boxes, panels, etc.)
CARD_COLOR = "#FFFFFF"

# Dark grey/black used for normal body text
TEXT_COLOR = "#22262F"

# Muted grey used for secondary/helper text
MUTED_TEXT_COLOR = "#6B7280"

# Red used for delete / logout / warning actions
DANGER_COLOR = "#E63946"

# Green used for "present" / success indicators
SUCCESS_COLOR = "#2FA84F"

# Amber used for "absent" / warning indicators
WARNING_COLOR = "#E8A93B"

# Border color for cards and input fields
BORDER_COLOR = "#D9DCE3"

# ----------------------------------------------------------
# FONTS
#
# Tkinter accepts fonts as tuples: (family, size, style)
# We define common font "roles" here so every page uses a
# consistent typography system instead of random font sizes.
# ----------------------------------------------------------

FONT_FAMILY = "Segoe UI"          # Falls back gracefully on most OS

FONT_TITLE = (FONT_FAMILY, 22, "bold")        # Big page titles
FONT_SUBTITLE = (FONT_FAMILY, 13, "normal")   # Small text under titles
FONT_HEADING = (FONT_FAMILY, 16, "bold")      # Section headings
FONT_BODY = (FONT_FAMILY, 11, "normal")       # Normal body text
FONT_BODY_BOLD = (FONT_FAMILY, 11, "bold")    # Emphasized body text
FONT_BUTTON = (FONT_FAMILY, 11, "bold")       # Button labels
FONT_SIDEBAR = (FONT_FAMILY, 12, "bold")      # Sidebar navigation labels
FONT_STAT_NUMBER = (FONT_FAMILY, 26, "bold")  # Big numbers on dashboard cards
FONT_STAT_LABEL = (FONT_FAMILY, 11, "normal") # Label under dashboard numbers

# ----------------------------------------------------------
# ICONS (Unicode symbols)
#
# Using Unicode emoji as icons means we don't need external
# image files to make the UI look modern. This keeps the
# project 100% dependency-free for the UI layer.
# ----------------------------------------------------------

ICON_APP = "🎓"
ICON_DASHBOARD = "📊"
ICON_STUDENTS = "👨‍🎓"
ICON_ATTENDANCE = "📷"
ICON_REPORTS = "📄"
ICON_ABOUT = "ℹ"
ICON_LOGOUT = "🚪"

# ----------------------------------------------------------
# SIZING / SPACING
#
# Keeping consistent spacing values makes the layout feel
# intentional instead of randomly placed.
# ----------------------------------------------------------

SIDEBAR_WIDTH = 220
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 650
PADDING_LARGE = 20
PADDING_MEDIUM = 12
PADDING_SMALL = 6
