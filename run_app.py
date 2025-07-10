import os
import subprocess
import sys
import time

def check_data_directory():
    """Check if data directory exists and has required files."""
    print("Checking data directory...")
    if not os.path.exists('data'):
        print("Data directory not found, creating it...")
        os.makedirs('data')
        return False

    required_files = [
        'data/mrsd_splice.tsv.gz',
        'data/splice_vault.tsv.gz',
        'data/mrsd_expression.tsv.gz'
    ]

    all_files_exist = True
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"Missing file: {file_path}")
            all_files_exist = False

    return all_files_exist

# Check if required data files exist
data_files_exist = check_data_directory()

# Create sample data if needed
if not data_files_exist:
    print("\nCreating sample data files...")
    try:
        print("Running generate_small_datasets.py to create small, reliable test data...")
        result = subprocess.run([sys.executable, 'generate_small_datasets.py'],
                              check=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              universal_newlines=True)
        print(result.stdout)

        # Double check that data was created
        if not check_data_directory():
            print("\nWARNING: Data files were not created successfully.")
            print("The application will run with minimal sample data.")
        else:
            print("\nSample data created successfully!")

    except subprocess.CalledProcessError as e:
        print(f"Error creating sample data: {e}")
        print(e.stderr)
        print("\nWARNING: Will use minimal built-in sample data instead.")

        # Try alternate scripts as fallback
        try:
            print("Trying fix_data.py as fallback...")
            result = subprocess.run([sys.executable, 'fix_data.py'],
                                  check=True,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  universal_newlines=True)
            print(result.stdout)
        except Exception as e2:
            print(f"fix_data.py fallback failed: {e2}")

            try:
                print("Trying create_sample_data.py as fallback...")
                result = subprocess.run([sys.executable, 'create_sample_data.py'],
                                      check=True,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      universal_newlines=True)
                print(result.stdout)
            except Exception as e3:
                print(f"All data generation fallbacks failed. Will use built-in sample data.")

# Run the Flask application
print("\nStarting Flask server...")
print("The backend will be available at http://localhost:8000")
print("\nPress Ctrl+C to stop the server")
print("\n" + "-"*50)

try:
    # Run the Flask app
    os.environ['FLASK_ENV'] = 'development'
    # Default port is 8000, but allow using a different port via command line
    port = 8000
    if len(sys.argv) > 1 and sys.argv[1].startswith('--port='):
        try:
            port = int(sys.argv[1].split('=')[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1].split('=')[1]}")
            sys.exit(1)

    subprocess.run([sys.executable, 'app.py', f'--port={port}'], check=True)
except KeyboardInterrupt:
    print("\nServer stopped by user")
except Exception as e:
    print(f"\nError running Flask server: {e}")
