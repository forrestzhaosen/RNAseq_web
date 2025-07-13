# Database configuration

# Path to SQLite database files
DATABASE_FILES = {
    'mrsd_splice': 'data/mrsd_splice.db',
    'splice_vault': 'data/splice_vault.db',
    'mrsd_expression': 'data/mrsd_expression.db'
}

# Map dataset names to their database tables
DATASET_TABLES = {
    'mrsd_splice': 'mrsd_splice',
    'splice_vault': 'splice_vault',
    'mrsd_expression': 'mrsd_expression'
}

# SQLite connection string format
def get_db_uri(dataset):
    return f"sqlite:///{DATABASE_FILES[dataset]}"

# Default chunk size for batch operations
DEFAULT_CHUNK_SIZE = 1000

# Timeout settings for database operations (in seconds)
DATABASE_TIMEOUT = 30
