"""app.py - Flask application entry point.

This file creates and configures the Flask application, registers
routes from routes.py, sets the secret key for session management,
and runs the development server.

How this maps to the original Tkinter project:
    Tkinter's MainApp(root)  ->  Flask app created here
    Tkinter's mainloop()     ->  app.run()

Key concepts explained:
    - Flask(__name__) creates a WSGI application instance.
    - app.secret_key is required to use Flask sessions (storing
      login state across requests).
    - app.register_blueprint() pulls in routes defined in routes.py
      so this file stays clean and focused on configuration.
    - The template_folder parameter tells Flask where to look for
      HTML files (Jinja2 templates).

Team member roles (future integration):
    - Database Developer:  Will replace sample data with SQLite queries.
    - Backend Developer:   Will add face recognition endpoints.
    - Integration Developer: Will connect camera, database, and face
      recognition modules together.
"""

from flask import Flask

# Create the Flask application instance.
# __name__ lets Flask know where to look for templates and static files.
app = Flask(__name__)

# -------------------------------------------------------------------
# Secret Key
# -------------------------------------------------------------------
# Flask needs a secret key to encrypt session cookies. In production,
# this should be a random, unguessable string stored in an environment
# variable. For hackathon/demo purposes, a hardcoded key is acceptable.
# -------------------------------------------------------------------
app.secret_key = "smart-attendance-secret-key-change-in-production"

# -------------------------------------------------------------------
# Import and register routes
# -------------------------------------------------------------------
# We keep routes in a separate file (routes.py) so that app.py only
# handles configuration. This is a common Flask pattern.
# -------------------------------------------------------------------
from routes import *

# -------------------------------------------------------------------
# Run the application
# -------------------------------------------------------------------
# When this file is executed directly (python app.py), the development
# server starts with debug=True for live reloading during development.
# debug=False should be used in production.
# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
