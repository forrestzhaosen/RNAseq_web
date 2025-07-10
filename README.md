# Clinical RNA-seq Data Viewer

A web application for querying and visualizing RNA-seq data from TSV files, using a Flask backend and Vue.js with PrimeVue for the frontend.

## Project Structure

```
├── app.py                # Flask backend server
├── data/                 # TSV data files
│   ├── mrsd_splice.tsv.gz
│   ├── splice_vault.tsv.gz
│   └── mrsd_expression.tsv.gz
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

3. Run the application with the helper script (recommended):
   ```bash
   python run_app.py
   ```

   If you encounter port conflicts, you can specify a different port:
   ```bash
   python run_app.py --port=8080
   ```
   This script will:
   - Check if data files exist and create sample data if needed
   - Start the Flask server

   The backend will run at http://localhost:8000

   **Alternatively**, you can generate sample data and run the server separately:
   ```bash
   python create_sample_data.py  # Only if you need sample data
   python app.py                 # Start the Flask server
   ```

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

## Data Description

This application provides a web interface to explore the following RNA-seq datasets:

- **mrsd_splice.tsv.gz**: Contains splicing data
- **splice_vault.tsv.gz**: Contains splicing vault information
- **mrsd_expression.tsv.gz**: Contains expression data

## Technologies Used

- **Backend**: Python, Flask, Pandas
- **Frontend**: Vue.js, PrimeVue, Axios
- **Data Processing**: Pandas for TSV parsing
