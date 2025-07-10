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

    # For splice_vault dataset, define chunk size to handle large files
    chunk_size = 100000  # Adjust based on your available memory

    # Try to load each file individually with error handling
    for dataset_name, file_path in data_files.items():
        try:
            if os.path.exists(file_path):
                print(f"\nLoading {dataset_name} from {file_path}...")
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                print(f"File size: {file_size_mb:.2f} MB")

                # For splice_vault (potentially large files), use a different approach
                if dataset_name == 'splice_vault' and file_size_mb > 100:  # If file is larger than 100MB
                    print(f"Large file detected for {dataset_name}, using optimized loading")
                    # First read just the header to get column names
                    df_header = pd.read_csv(file_path, sep='\t', nrows=1)
                    column_names = df_header.columns.tolist()

                    # Read the first chunk to estimate total rows
                    first_chunk = pd.read_csv(file_path, sep='\t', dtype=str,
                                             nrows=chunk_size, na_filter=False)

                    # Use the first chunk as our dataframe
                    df = first_chunk
                    print(f"Loaded first {chunk_size} rows of {dataset_name} (sampling large dataset)")
                else:
                    # For smaller files, load everything
                    df = pd.read_csv(file_path, sep='\t', dtype=str, na_filter=False)
                    print(f"Loaded all {len(df)} rows of {dataset_name}")

                # Clean data: replace NaN and None strings with empty strings
                for col in df.columns:
                    df[col] = df[col].replace(['nan', 'None', 'NaN'], '')

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
    # Use smaller per_page for splice_vault or any large dataset
    default_per_page = 5 if dataset == 'splice_vault' else 10
    per_page = int(request.args.get('per_page', default_per_page))
    # Cap per_page to avoid memory issues with large datasets
    if dataset == 'splice_vault' and per_page > 10:
        per_page = 10

    print(f"Parameters: page={page}, per_page={per_page}, search='{search}', column='{column}'")

    try:
        # Time the operation to detect slow operations
        import time
        start_time = time.time()

        # For splice_vault (or any large dataset), we'll use more efficient operations
        is_large_dataset = dataset == 'splice_vault' or len(dfs[dataset]) > 100000

        if is_large_dataset:
            print(f"Large dataset detected ({dataset}), using optimized processing")
            # Instead of copying the entire dataframe, we'll process it differently
            df = dfs[dataset]
            # We'll only report the total size, not modify the full dataset
            total = len(df)

            # If search is applied, we'll filter just-in-time during slicing
            filtered_indices = None
            if search and column and column in df.columns:
                # For large datasets, filtering can be memory-intensive
                # We'll create a boolean mask without creating a new dataframe
                mask = df[column].astype(str).str.contains(search, case=False, na=False)
                filtered_indices = mask[mask].index
                total = len(filtered_indices)
                print(f"Filter applied, matching records: {total}")

            # Calculate pagination - we only need to access the slice we'll display
            start_idx = (page - 1) * per_page
            end_idx = min(start_idx + per_page, total)

            if start_idx >= total:
                print(f"Warning: start_idx {start_idx} >= total {total}, returning empty data")
                return jsonify({
                    'data': [],
                    'total': total,
                    'page': page,
                    'per_page': per_page
                })

            # Get only the necessary slice using loc if filtered or iloc otherwise
            if filtered_indices is not None:
                # Ensure we don't go out of bounds
                end_slice_idx = min(start_idx + per_page, len(filtered_indices))
                if start_idx >= len(filtered_indices):
                    data_slice = pd.DataFrame(columns=df.columns)
                else:
                    slice_indices = filtered_indices[start_idx:end_slice_idx]
                    data_slice = df.loc[slice_indices]
            else:
                data_slice = df.iloc[start_idx:end_idx]
        else:
            # For smaller datasets, continue with the existing approach
            # Work with a copy to avoid modifying the original
            df = dfs[dataset].copy()
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

            # Convert all columns to strings for consistent handling
            for col in df.columns:
                df[col] = df[col].astype(str)
                # Replace 'nan' strings with empty strings
                df[col] = df[col].replace(['nan', 'None', 'NaN'], '')

            # Apply search filter if provided
            if search and column and column in df.columns:
                df = df[df[column].str.contains(search, case=False, na=False)]
                print(f"After search filter, dataframe shape: {df.shape}")

            # Calculate pagination
            total = len(df)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page

            # Ensure indices are valid
            if start_idx >= total:
                print(f"Warning: start_idx {start_idx} >= total {total}, returning empty data")
                return jsonify({
                    'data': [],
                    'total': total,
                    'page': page,
                    'per_page': per_page
                })

            # Get the data slice
            data_slice = df.iloc[start_idx:end_idx]

        # Check if the operation is taking too long
        elapsed_time = time.time() - start_time
        print(f"Data preparation took {elapsed_time:.2f} seconds")

        # Apply search filter if provided
        if search and column and column in df.columns:
            df = df[df[column].str.contains(search, case=False, na=False)]
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

        # More efficient serialization with timeouts and size checks
        data = []
        max_string_length = 1000  # Limit extremely long string values

        # Set a timeout for record processing
        processing_start = time.time()
        processing_timeout = 15  # seconds

        # Convert to records with explicit handling
        for _, row in data_slice.iterrows():
            # Check for timeout during processing
            if time.time() - processing_start > processing_timeout:
                print("Warning: Data processing timeout reached")
                break

            record = {}
            for col in data_slice.columns:  # Use data_slice.columns instead of df.columns
                try:
                    value = row[col]
                    # Ensure all values are simple strings with length limits
                    if pd.isna(value) or value == 'nan' or value == 'None' or value == 'NaN':
                        record[col] = ''
                    else:
                        # Truncate extremely long strings to prevent memory issues
                        str_value = str(value)
                        if len(str_value) > max_string_length:
                            str_value = str_value[:max_string_length] + '... (truncated)'
                        record[col] = str_value
                except Exception as col_error:
                    print(f"Error processing column {col}: {str(col_error)}")
                    record[col] = "[Error]"  # Placeholder for error values
            data.append(record)

        # Calculate total processing time
        total_time = time.time() - start_time
        print(f"Returning {len(data)} records, processing took {total_time:.2f} seconds")

        # Add dataset size info to help troubleshoot frontend issues
        dataset_info = {
            'dataset_name': dataset,
            'total_rows': len(dfs[dataset]),
            'total_columns': len(dfs[dataset].columns),
            'processing_time_seconds': round(total_time, 2),
            'is_large_dataset': is_large_dataset
        }

        response_data = {
            'data': data,
            'total': total,
            'page': page,
            'per_page': per_page,
            'dataset_info': dataset_info
        }

        # Use Flask's built-in json encoding to ensure it works
        return jsonify(response_data)
    except Exception as e:
        print(f"Error processing dataset {dataset}: {str(e)}")
        import traceback
        traceback.print_exc()

        # Return a simplified error response that's guaranteed to serialize
        return jsonify({
            'error': f"Error processing dataset {dataset}: {str(e)}",
            'data': [],
            'total': 0,
            'page': page,
            'per_page': per_page
        }), 500

if __name__ == '__main__':
    # Use port 8000 instead of 5000 to avoid conflicts with AirPlay on macOS
    port = 8000
    print(f"\nStarting Flask server on http://localhost:{port}")
    print("Available datasets:", list(dfs.keys()))
    # Print information about dataset sizes
    for name, df in dfs.items():
        print(f"Dataset '{name}': {len(df)} rows, {len(df.columns)} columns")
    print("\nPress Ctrl+C to stop the server\n")
    try:
        # Increase timeout for large datasets
        from werkzeug.serving import run_simple
        # Make sure the server is accessible from other machines on the network
        app.run(debug=True, host='0.0.0.0', port=port,
                threaded=True, # Enable threading
        ) # Increase request timeout to 2 minutes
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\nError: Port {port} is already in use.")
            print(f"Try running the server with a different port:")
            print(f"    python app.py --port=8080")
        else:
            print(f"\nError starting server: {e}")
