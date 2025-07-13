#!/usr/bin/env python
"""
Utility script to convert all TSV files to SQLite databases.

This script will scan the data directory for TSV files and convert them to SQLite databases.
It handles large files efficiently by processing them in chunks to minimize memory usage.

Usage:
  python tsv_to_sql_all.py
"""

import os
import sys
import time
import gc
import pandas as pd
from sqlalchemy import create_engine
from db_config import DATABASE_FILES, DATASET_TABLES

def convert_tsv_to_sqlite(tsv_path, db_path, table_name, chunk_size=100000):
    """
    Convert a TSV file to a SQLite database, processing in chunks to minimize memory usage.

    Args:
        tsv_path: Path to the TSV file
        db_path: Path to the SQLite database file to create
        table_name: Name of the table to create in the database
        chunk_size: Number of rows to process at once
    """
    print(f"\nConverting {tsv_path} to {db_path}")
    start_time = time.time()

    if not os.path.exists(tsv_path):
        print(f"Error: TSV file {tsv_path} does not exist")
        return False

    # Get file size
    file_size_mb = os.path.getsize(tsv_path) / (1024 * 1024)
    print(f"File size: {file_size_mb:.2f} MB")

    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Create database engine
    engine = create_engine(f"sqlite:///{db_path}")

    try:
        # Check if this is a large file
        is_large_file = file_size_mb > 100  # Consider files > 100MB as large

        if is_large_file:
            print(f"Large file detected, processing in chunks of {chunk_size:,} rows")

            # Read the header first to get column names
            header_df = pd.read_csv(tsv_path, sep='\t', nrows=1)
            print(f"Detected {len(header_df.columns)} columns")

            # Process in chunks
            chunk_count = 0
            row_count = 0

            # Use if_exists='replace' for the first chunk, then 'append' for subsequent chunks
            if_exists = 'replace'

            for chunk in pd.read_csv(tsv_path, sep='\t', chunksize=chunk_size, low_memory=True):
                chunk_count += 1
                rows_in_chunk = len(chunk)
                row_count += rows_in_chunk

                # Clean data - replace NaN values with empty strings
                for col in chunk.columns:
                    chunk[col] = chunk[col].replace(['nan', 'None', 'NaN'], '')

                # Write to database
                chunk.to_sql(table_name, engine, if_exists=if_exists, index=False)
                if_exists = 'append'  # Use append for all subsequent chunks

                # Report progress
                elapsed_time = time.time() - start_time
                print(f"Chunk {chunk_count}: Processed {row_count:,} rows ({rows_in_chunk:,} in this chunk) in {elapsed_time:.1f} seconds")

                # Clean up to free memory
                del chunk
                gc.collect()

        else:
            # For smaller files, process all at once
            print("Processing entire file at once")
            df = pd.read_csv(tsv_path, sep='\t')

            # Clean data - replace NaN values with empty strings
            for col in df.columns:
                df[col] = df[col].replace(['nan', 'None', 'NaN'], '')

            # Write to database
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            row_count = len(df)

        # Calculate total time
        total_time = time.time() - start_time
        print(f"Conversion complete: {row_count:,} rows processed in {total_time:.1f} seconds")
        print(f"Average processing speed: {row_count/total_time:.1f} rows/second")
        print(f"Database file created at: {db_path}")

        return True

    except Exception as e:
        print(f"Error converting {tsv_path}: {e}")
        return False

    finally:
        # Always dispose of the engine
        engine.dispose()

def main():
    """
    Main function to scan for TSV files and convert them to SQLite databases.
    """
    data_dir = 'data'

    # Ensure data directory exists
    if not os.path.exists(data_dir):
        print(f"Creating data directory: {data_dir}")
        os.makedirs(data_dir)

    # Check for TSV files in data directory
    tsv_files = [f for f in os.listdir(data_dir) if f.endswith('.tsv.gz') or f.endswith('.tsv')]

    if not tsv_files:
        print(f"No TSV files found in {data_dir} directory")
        return

    print(f"Found {len(tsv_files)} TSV files: {', '.join(tsv_files)}")

    # Process each TSV file
    success_count = 0
    for tsv_file in tsv_files:
        # Get dataset name from filename (remove .tsv.gz or .tsv extension)
        dataset_name = tsv_file.replace('.tsv.gz', '').replace('.tsv', '')

        # Get database path and table name from config
        if dataset_name in DATABASE_FILES:
            db_path = DATABASE_FILES[dataset_name]
            table_name = DATASET_TABLES[dataset_name]
        else:
            # If not in config, use default paths
            db_path = f"data/{dataset_name}.db"
            table_name = dataset_name

        # Convert TSV to SQLite
        tsv_path = os.path.join(data_dir, tsv_file)
        if convert_tsv_to_sqlite(tsv_path, db_path, table_name):
            success_count += 1

    print(f"\nConversion summary: {success_count} of {len(tsv_files)} files successfully converted")
    if success_count == len(tsv_files):
        print("All files converted successfully")
    else:
        print(f"Failed to convert {len(tsv_files) - success_count} files")

if __name__ == "__main__":
    main()
