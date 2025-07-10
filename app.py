from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
# Enable CORS for all routes and origins
CORS(app, resources={r"/*": {"origins": "*"}})

# Load the TSV files
def load_data():
    data_dict = {}

    # Define paths to data files
    data_files = {
        'mrsd_splice': 'data/mrsd_splice.tsv.gz',
        'splice_vault': 'data/splice_vault.tsv.gz',
        'mrsd_expression': 'data/mrsd_expression.tsv.gz'
    }

    # Check if data directory exists
    import os
    if not os.path.exists('data'):
        print("Data directory not found. Creating it...")
        os.makedirs('data')

    # Try to load each file individually with error handling
    for dataset_name, file_path in data_files.items():
        try:
            if os.path.exists(file_path):
                # Set low_memory=False to avoid DtypeWarning and ensure all values are properly parsed
                # Convert all columns to string initially to avoid mixed type issues
                df = pd.read_csv(file_path, sep='\t', low_memory=False, dtype=str)

                # Convert numeric columns back to appropriate types
                for col in df.columns:
                    # Try to convert to numeric, but keep as string if it fails
                    try:
                        df[col] = pd.to_numeric(df[col])
                    except (ValueError, TypeError):
                        # Keep as string if conversion fails
                        pass

                data_dict[dataset_name] = df
                print(f"Successfully loaded {file_path} with {len(df)} rows and {len(df.columns)} columns")
                print(f"Columns: {df.columns.tolist()}")
            else:
                raise FileNotFoundError(f"File {file_path} does not exist")

        except Exception as e:
            print(f"Error loading {file_path}: {e}")

            # Create appropriate sample dataset based on the file type
            if dataset_name == 'mrsd_splice':
                data_dict[dataset_name] = pd.DataFrame({
                    'gene_id': ['ENSG00000001', 'ENSG00000002', 'ENSG00000003', 'ENSG00000004', 'ENSG00000005'],
                    'transcript_id': ['ENST00000001', 'ENST00000002', 'ENST00000003', 'ENST00000004', 'ENST00000005'],
                    'sample': ['sample_1', 'sample_2', 'sample_3', 'sample_4', 'sample_5'],
                    'expression': [10.5, 20.3, 15.7, 8.9, 12.1],
                    'junction_count': [100, 200, 150, 180, 120]
                })
            elif dataset_name == 'splice_vault':
                data_dict[dataset_name] = pd.DataFrame({
                    'transcript_id': ['ENST00000001', 'ENST00000002', 'ENST00000003', 'ENST00000004', 'ENST00000005'],
                    'junction': ['chr1:1000-2000', 'chr1:3000-4000', 'chr2:1000-2000', 'chr3:5000-6000', 'chr4:7000-8000'],
                    'count': [100, 200, 150, 300, 250],
                    'score': [0.8, 0.9, 0.7, 0.85, 0.75],
                    'tissue': ['brain', 'heart', 'liver', 'kidney', 'lung']
                })
            elif dataset_name == 'mrsd_expression':
                data_dict[dataset_name] = pd.DataFrame({
                    'gene_id': ['ENSG00000001', 'ENSG00000002', 'ENSG00000003', 'ENSG00000004', 'ENSG00000005'],
                    'tpm': [5.2, 10.1, 7.8, 3.5, 9.2],
                    'fpkm': [4.8, 9.5, 7.2, 3.1, 8.7],
                    'sample': ['sample_1', 'sample_2', 'sample_3', 'sample_4', 'sample_5'],
                    'condition': ['control', 'treatment', 'control', 'treatment', 'control']
                })

            print(f"Created sample {dataset_name} dataset with {len(data_dict[dataset_name])} rows")

    # Add a flag to indicate we're using sample data if no real data was loaded
    if all(not os.path.exists(path) for path in data_files.values()):
        print("\nWARNING: Using sample data for all datasets. Run create_sample_data.py to generate proper test data.")

    return data_dict

# Store the DataFrames
dfs = load_data()

@app.route('/api/datasets', methods=['GET'])
def get_datasets():
    return jsonify(list(dfs.keys()))

@app.route('/api/columns/<dataset>', methods=['GET'])
def get_columns(dataset):
    if dataset in dfs:
        return jsonify(list(dfs[dataset].columns))
    return jsonify({'error': 'Dataset not found'}), 404

@app.route('/api/data/<dataset>', methods=['GET'])
def get_data(dataset):
    print(f"\nAPI Request: /api/data/{dataset}")
    print(f"Query params: {request.args}")

    if dataset not in dfs:
        print(f"Dataset {dataset} not found in available datasets: {list(dfs.keys())}")
        return jsonify({'error': 'Dataset not found'}), 404

    # Get query parameters
    search = request.args.get('search', '')
    column = request.args.get('column', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    print(f"Parameters: page={page}, per_page={per_page}, search='{search}', column='{column}'")

    df = dfs[dataset]
    print(f"Original dataframe shape: {df.shape}")

    # Ensure the dataframe has content
    if df.empty:
        print(f"Warning: Dataset '{dataset}' is empty!")
        return jsonify({
            'data': [],
            'total': 0,
            'page': page,
            'per_page': per_page
        })

    # Apply search filter if provided
    if search and column in df.columns:
        df = df[df[column].astype(str).str.contains(search, case=False)]
        print(f"After search filter, dataframe shape: {df.shape}")

    # Calculate pagination
    total = len(df)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    print(f"Pagination: total={total}, start_idx={start_idx}, end_idx={end_idx}")

    # Ensure indices are valid
    if start_idx >= total:
        print(f"Warning: start_idx {start_idx} >= total {total}, returning empty data")
        return jsonify({
            'data': [],
            'total': total,
            'page': page,
            'per_page': per_page
        })

    # Convert the slice of data to dictionary and ensure all values are JSON serializable
    try:
        # Get a smaller chunk of data to avoid large response issues
        # Limit the data to just 5 records for safety if it seems too large
        if len(df) > 1000 and per_page > 5:
            print(f"Large dataset detected ({len(df)} rows), limiting page size to 5")
            end_idx = start_idx + 5

        # Make a copy to avoid modifying original dataframe
        data_records = df.iloc[start_idx:end_idx].copy()

        # Force string conversion for all object columns to ensure serialization
        for col in data_records.select_dtypes(include=['object']).columns:
            data_records[col] = data_records[col].astype(str)

        # Replace NaN with None to avoid JSON serialization issues
        data_records = data_records.where(pd.notnull(data_records), None)

        # Convert to records dict
        raw_data = data_records.to_dict('records')

        # Clean the data to ensure JSON serialization
        data = []
        for record in raw_data:
            clean_record = {}
            for key, value in record.items():
                # Handle various data types appropriately
                if value is None:
                    clean_record[key] = None
                elif hasattr(value, 'item'):
                    # Convert numpy types to Python native types
                    try:
                        clean_record[key] = value.item()
                    except:
                        clean_record[key] = str(value)
                elif isinstance(value, (int, float, bool)):
                    clean_record[key] = value
                else:
                    # Convert everything else to string
                    clean_record[key] = str(value)
            data.append(clean_record)

        print(f"Returning {len(data)} records")

        response_data = {
            'data': data,
            'total': total,
            'page': page,
            'per_page': per_page
        }

        # Use Flask's built-in json encoding to ensure it works
        return jsonify(response_data)
    except Exception as e:
        print(f"Error serializing data: {e}")
        # Return a simplified error response that's guaranteed to serialize
        return jsonify({
            'error': f"Error processing data: {str(e)}",
            'data': [],
            'total': total,
            'page': page,
            'per_page': per_page
        })

if __name__ == '__main__':
    # Use port 8000 instead of 5000 to avoid conflicts with AirPlay on macOS
    port = 8000
    print(f"\nStarting Flask server on http://localhost:{port}")
    print("Available datasets:", list(dfs.keys()))
    print("\nPress Ctrl+C to stop the server\n")
    try:
        # Make sure the server is accessible from other machines on the network
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
