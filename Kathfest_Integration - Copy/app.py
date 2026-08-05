"""
app.py - Flask application entry point for the Smart Student Attendance System.

This is THE SINGLE FILE that starts the entire application. Running
this file launches the Flask web server, making the attendance system
accessible from any browser on the local network.

How this maps to the original Tkinter project:
    Tkinter entry point: UI/main.py -> LoginWindow -> MainApp
    Flask entry point:   THIS FILE -> app.run() (routes initialized via init_routes)

Why this file exists:
    - It creates the Flask application instance.
    - It sets the template folder to UI/templates/ and static folder
      to UI/static/ so the existing web_based templates are used.
    - It configures the secret key for session management.
    - It calls init_routes(app) to register all routes (no circular import).
    - It runs the development server.

How to run:
    python app.py
    Then open http://localhost:5000 in your browser.

Original source:
    web_based/app.py (lines 1-58) — rewritten to use proper paths
    and the new integrated module structure.
"""

import os
import sys

# =========================================================================
# Add the project root to sys.path so that imports (config, database,
# backend, routes) work regardless of how the script is invoked.
# =========================================================================
_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from flask import Flask

# =========================================================================
# Create the Flask application.
#
# Parameters:
#     template_folder: Points to UI/templates/ where all HTML files live.
#                      These were originally in web_based/templates/ and
#                      were moved here during integration.
#     static_folder:   Points to UI/static/ where CSS, JS, and images live.
#                      These were originally in web_based/static/.
#     static_url_path: /static so URLs like /static/css/style.css work.
# =========================================================================
app = Flask(
    __name__,
    template_folder=os.path.join(_project_root, "UI", "templates"),
    static_folder=os.path.join(_project_root, "UI", "static"),
    static_url_path="/static",
)

# =========================================================================
# Secret Key for session encryption.
# =========================================================================
from config import SECRET_KEY
app.secret_key = SECRET_KEY

# =========================================================================
# Initialize routes.
#
# The init_routes() function registers all URL routes on the app object.
# Using this function call avoids the circular import problem:
#     OLD (broken with reloader): routes.py imported 'app', app.py imported 'routes'
#     NEW (works always):         app.py calls init_routes(app), passing app as param
#
# The call also triggers database initialization (initialize_database())
# because it's called at module level inside routes.py.
# =========================================================================
from routes import init_routes
init_routes(app)

# =========================================================================
# Start the server.
# =========================================================================
if __name__ == "__main__":
    from config import HOST, PORT, DEBUG

    print("=" * 65)
    print("  Smart Student Attendance System")
    print("  Face Recognition Based Attendance")
    print("=" * 65)
    print(f"  Server starting on http://{HOST}:{PORT}")
    print(f"  Open your browser and navigate to:")
    print(f"  -> http://localhost:{PORT}")
    print(f"  -> http://127.0.0.1:{PORT}")
    print(f"  Login: admin / admin")
    print("=" * 65)

    app.run(host=HOST, port=PORT, debug=DEBUG)
