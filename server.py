import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from streamlit_app import app, application

__all__ = ['app', 'application']

if __name__ == "__main__":
    import streamlit.cli as cli
    sys.argv = ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
    cli.main()
