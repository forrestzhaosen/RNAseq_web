# Clinical RNA-seq Data Viewer

A web application for querying and visualizing RNA-seq data from SQLite databases, using a Flask backend and Vue.js with PrimeVue for the frontend.

## Project Structure

```
├── app.py                # Flask backend server
├── db_config.py          # Database configuration
├── data/                 # Data files
│   ├── mrsd_splice.db    # SQLite database (converted from TSV)
│   ├── splice_vault.db   # SQLite database (converted from TSV)
│   ├── mrsd_expression.db # SQLite database (converted from TSV)
│   ├── mrsd_splice.tsv.gz # Original TSV file (optional)
│   ├── splice_vault.tsv.gz # Original TSV file (optional)
│   └── mrsd_expression.tsv.gz # Original TSV file (optional)
├── tsv_to_sql_all.py    # Utility to convert TSV files to SQLite
├── prime_vue/            # Vue.js frontend
│   ├── public/
│   ├── src/
│   └── package.json
└── requirements.txt      # Python dependencies
```

## Setup Instructions

### Backend Setup

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Convert TSV files to SQLite databases (if you have TSV files):
   ```bash
   python data/tsv_to_sql_all.py
   ```
   This will scan the `data` directory for TSV files and convert them to SQLite databases.
   The conversion is done in chunks to minimize memory usage, making it suitable for large files.

4. Run the application:
   ```bash
   python app.py
   ```

   If you encounter port conflicts, you can specify a different port:
   ```bash
   python app.py --port=8080
   ```

   The backend will run at http://localhost:8000

   **Note**: If no database files are found, the application will automatically create sample databases with minimal test data.

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd prime_vue
   ```

2. Install JavaScript dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run serve
   ```
   The frontend will run at http://localhost:8080

## Features

- View and search three different RNA-seq datasets
- Filter data by any column
- Interactive data tables with sorting and pagination
- Responsive design for all screen sizes
- Memory-efficient SQLite database backend
- Optimized for large datasets (millions of rows)

## Data Description

This application provides a web interface to explore the following RNA-seq datasets:

- **mrsd_splice**: Contains splicing data
- **splice_vault**: Contains splicing vault information (6.7+ million rows)
- **mrsd_expression**: Contains expression data

All datasets are stored in SQLite databases for efficient querying and minimal memory usage.

## Memory Optimization

The application uses several techniques to minimize memory usage:

1. **SQLite Database Storage**: All data is stored in SQLite databases rather than loaded into memory
2. **SQL Query Pagination**: Data is retrieved from the database in small pages as needed
3. **Direct SQL Filtering**: Search operations are performed directly in SQL rather than in-memory
4. **Chunked Processing**: Large file operations are performed in chunks to limit memory usage
5. **Connection Management**: Database connections are properly managed to prevent resource leaks

## Technologies Used

- **Backend**: Python, Flask, SQLAlchemy, SQLite
- **Frontend**: Vue.js, PrimeVue, Axios
- **Data Processing**: SQL for efficient querying
- **Data Conversion**: Pandas for TSV to SQLite conversion (during setup only)
