"""
Entry point for deployment
This file serves as the main entry point for the Streamlit application
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the main app
from app import app, application

# For deployment compatibility, expose the app
__all__ = ['app', 'application']

if __name__ == "__main__":
    import streamlit.cli as cli
    sys.argv = ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
    cli.main()
