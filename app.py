from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import argparse
import os
import logging
import math
from data.db_config import DATABASE_FILES, DATASET_TABLES

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run the Flask server for RNA-seq data viewer')
parser.add_argument('--port', type=int, default=8000, help='Port to run the server on (default: 8000)')
args = parser.parse_args()

app = Flask(__name__)
# Enable CORS for all routes and origins
CORS(app, resources={r"/*": {"origins": "*"}})

# Track database availability
available_datasets = {}

def check_database_exists(db_path):
    """Check if database file exists"""
    return os.path.exists(db_path)

def create_sample_data():
    """Create sample SQLite databases if they don't exist"""
    sample_data = {
        'mrsd_splice': [
            {'hgnc_symbol': 'ENSG00000001'},
            {'hgnc_symbol': 'ENSG00000002'}
        ],
        'splice_vault': [
            {'tx_id': 'ENST00000001'},
            {'tx_id': 'ENST00000002'}
        ],
        'mrsd_expression': [
            {'hgnc_symbol': 'ENSG00000001'},
            {'hgnc_symbol': 'ENSG00000002'}
        ]
    }

    for dataset_name, data in sample_data.items():
        db_path = DATABASE_FILES[dataset_name]

        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Create database and table
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create table based on first row structure
        if data:
            # Get column names and types from first row
            columns = []
            for key, value in data[0].items():
                if isinstance(value, str):
                    columns.append(f"{key} TEXT")
                elif isinstance(value, float):
                    columns.append(f"{key} REAL")
                else:
                    columns.append(f"{key} INTEGER")

            # Create table
            table_name = DATASET_TABLES[dataset_name]
            create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
            cursor.execute(create_table_sql)

            # Insert sample data
            for row in data:
                placeholders = ', '.join(['?'] * len(row))
                columns_str = ', '.join(row.keys())
                values = list(row.values())

                insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                cursor.execute(insert_sql, values)

        conn.commit()
        conn.close()
        logger.info(f"Created sample database for {dataset_name}")

def initialize_databases():
    """Initialize database connections and check availability"""
    global available_datasets

    for dataset_name, db_path in DATABASE_FILES.items():
        try:
            if not check_database_exists(db_path):
                logger.warning(f"Database file {db_path} not found. Creating sample data.")
                create_sample_data()

            # Test connection
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            conn.close()

            available_datasets[dataset_name] = True
            logger.info(f"Successfully connected to {dataset_name} database")

        except Exception as e:
            logger.error(f"Failed to initialize database {dataset_name}: {e}")
            available_datasets[dataset_name] = False

def get_table_columns(dataset_name):
    """Get column names for a dataset"""
    try:
        if not available_datasets.get(dataset_name, False):
            return []

        db_path = DATABASE_FILES[dataset_name]
        table_name = DATASET_TABLES[dataset_name]

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get column information using PRAGMA
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]  # row[1] is the column name

        conn.close()
        return columns
    except Exception as e:
        logger.error(f"Error getting columns for {dataset_name}: {e}")
        return []

def query_data(dataset_name, search_term=None, search_column=None, page=1, per_page=10):
    """Query data from database with optional filtering and pagination"""
    try:
        if not available_datasets.get(dataset_name, False):
            return {'data': [], 'total': 0, 'error': 'Database not available'}

        db_path = DATABASE_FILES[dataset_name]
        table_name = DATASET_TABLES[dataset_name]

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()

        # Build base query
        base_query = f"SELECT * FROM {table_name}"
        count_query = f"SELECT COUNT(*) FROM {table_name}"

        # Add search filter if provided
        params = []
        if search_term and search_column:
            where_clause = f" WHERE {search_column} LIKE ?"
            base_query += where_clause
            count_query += where_clause
            params.append(f"%{search_term}%")

        # Get total count
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]

        # Add pagination
        offset = (page - 1) * per_page
        base_query += f" LIMIT ? OFFSET ?"
        params.extend([per_page, offset])

        # Get data
        cursor.execute(base_query, params)
        rows = cursor.fetchall()

        # Convert to list of dictionaries and ensure all values are properly serializable
        data = []
        for row in rows:
            row_dict = dict(row)
            # Ensure all values can be serialized to JSON
            for key, value in row_dict.items():
                if isinstance(value, bytes):
                    row_dict[key] = value.decode('utf-8', errors='replace')
                elif isinstance(value, float):
                    # Handle infinity and NaN values with math module functions
                    if math.isinf(value):
                        row_dict[key] = "Infinity" if value > 0 else "-Infinity"
                    elif math.isnan(value):
                        row_dict[key] = "NaN"
                    else:
                        row_dict[key] = value
                elif value is None:
                    row_dict[key] = ""
            data.append(row_dict)

        conn.close()

        # Debug info to help diagnose issues
        sample_data = data[:1] if data else {}
        logger.info(f"Query for {dataset_name} returned {len(data)} rows with columns: {list(sample_data[0].keys()) if sample_data else 'none'}")

        # Log if special values were encountered
        has_special_values = any(
            isinstance(v, str) and v in ("Infinity", "-Infinity", "NaN")
            for item in data[:5]  # Check just first few rows
            for k, v in item.items()
        )
        if has_special_values:
            logger.info(f"Special numeric values (Infinity/NaN) detected in {dataset_name} dataset")

        return {
            'data': data,
            'total': total,
            'page': page,
            'per_page': per_page
        }

    except sqlite3.Error as e:
        logger.error(f"Database error for {dataset_name}: {e}")
        return {'data': [], 'total': 0, 'error': f'Database error: {str(e)}'}
    except Exception as e:
        logger.error(f"Unexpected error for {dataset_name}: {e}")
        return {'data': [], 'total': 0, 'error': f'Unexpected error: {str(e)}'}

# API Routes
@app.route('/api/datasets', methods=['GET'])
def get_datasets():
    """Get list of available datasets"""
    try:
        active_datasets = [name for name, status in available_datasets.items() if status]
        return jsonify(active_datasets)
    except Exception as e:
        logger.error(f"Error getting datasets: {e}")
        return jsonify({'error': 'Failed to get datasets'}), 500

@app.route('/api/columns/<dataset>', methods=['GET'])
def get_columns(dataset):
    """Get column names for a specific dataset"""
    try:
        if dataset not in available_datasets or not available_datasets[dataset]:
            return jsonify({'error': 'Dataset not found'}), 404

        columns = get_table_columns(dataset)
        return jsonify(columns)
    except Exception as e:
        logger.error(f"Error getting columns for {dataset}: {e}")
        return jsonify({'error': 'Failed to get columns'}), 500

@app.route('/api/data/<dataset>', methods=['GET'])
def get_data(dataset):
    """Get data for a specific dataset with optional filtering and pagination"""
    try:
        if dataset not in available_datasets or not available_datasets[dataset]:
            return jsonify({'error': 'Dataset not found'}), 404

        # Get query parameters
        search_term = request.args.get('search', '').strip()
        search_column = request.args.get('column', '').strip()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        # Validate parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:  # Limit per_page to prevent abuse
            per_page = 10

        # Validate search column if provided
        if search_column:
            available_columns = get_table_columns(dataset)
            if search_column not in available_columns:
                return jsonify({'error': f'Column {search_column} not found in dataset'}), 400

        # Query data
        result = query_data(dataset, search_term, search_column, page, per_page)

        if 'error' in result and result['error']:
            return jsonify({'error': result['error']}), 500

        return jsonify(result)

    except ValueError as e:
        return jsonify({'error': f'Invalid parameter: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Error getting data for {dataset}: {e}")
        return jsonify({'error': 'Failed to get data'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    dataset_info = {}
    for name, status in available_datasets.items():
        if status:
            try:
                columns = get_table_columns(name)
                sample_data = query_data(name, per_page=1)
                dataset_info[name] = {
                    'columns': columns,
                    'sample_row_keys': list(sample_data['data'][0].keys()) if sample_data['data'] else [],
                    'row_count': sample_data['total']
                }
            except Exception as e:
                dataset_info[name] = {'error': str(e)}

    return jsonify({
        'status': 'healthy',
        'databases': [name for name, status in available_datasets.items() if status],
        'message': 'RNA-seq data viewer backend is running',
        'dataset_info': dataset_info
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = args.port

    # Initialize databases
    print("Initializing databases...")
    initialize_databases()

    active_datasets = [name for name, status in available_datasets.items() if status]
    if not active_datasets:
        print("Warning: No databases were successfully initialized.")
        print("The server will start but may not have any data available.")

    print(f"\nStarting Flask server on http://localhost:{port}")
    print("Available datasets:", active_datasets)
    print("\nAPI Endpoints:")
    print(f"  GET http://localhost:{port}/api/health - Health check")
    print(f"  GET http://localhost:{port}/api/datasets - List datasets")
    print(f"  GET http://localhost:{port}/api/columns/<dataset> - Get columns")
    print(f"  GET http://localhost:{port}/api/data/<dataset> - Get data")
    print("\nPress Ctrl+C to stop the server\n")

    try:
        app.run(debug=True, host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\nError: Port {port} is already in use.")
            print(f"Try running the server with a different port:")
            print(f"    python app.py --port=8080")
        else:
            print(f"\nError starting server: {e}")
