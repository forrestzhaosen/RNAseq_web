
#!/usr/bin/env python3
import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Change to the project directory
os.chdir(project_dir)

# Print debug information
print(f"WSGI: Working directory: {os.getcwd()}")
print(f"WSGI: Python path: {sys.path[:3]}")  # Show first 3 entries
print(f"WSGI: Project directory: {project_dir}")

# Check if data directory exists
data_dir = os.path.join(project_dir, 'data')
print(f"WSGI: Data directory exists: {os.path.exists(data_dir)}")
if os.path.exists(data_dir):
    db_files = [f for f in os.listdir(data_dir) if f.endswith('.db')]
    print(f"WSGI: Database files found: {db_files}")

try:
    from app import app
    print("WSGI: Successfully imported app")
except Exception as e:
    print(f"WSGI: Error importing app: {e}")
    raise

application = app

if __name__ == "__main__":
    app.run()
