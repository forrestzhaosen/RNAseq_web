#!/usr/bin/env python3
import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Change to the project directory
os.chdir(project_dir)

from app import app

if __name__ == "__main__":
    app.run()
