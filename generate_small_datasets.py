import pandas as pd
import os
import numpy as np

"""
This script generates small, clean test datasets that are guaranteed to work with the app.
"""

print("Generating small test datasets...")

# Create data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')
    print("Created data directory")

# Generate a small mrsd_splice dataset (10 rows)
print("Creating mrsd_splice.tsv.gz...")

mrsd_splice_data = {
    'gene_id': [f'ENSG{i:08d}' for i in range(1, 11)],
    'transcript_id': [f'ENST{i:08d}' for i in range(1, 11)],
    'sample': [f'sample_{i}' for i in range(1, 11)],
    'expression': [round(np.random.uniform(5, 25), 2) for _ in range(10)],
    'junction_count': [np.random.randint(10, 1000) for _ in range(10)]
}

mrsd_splice_df = pd.DataFrame(mrsd_splice_data)
mrsd_splice_df.to_csv('data/mrsd_splice.tsv.gz', sep='\t', index=False, compression='gzip')

# Generate a small splice_vault dataset (10 rows)
print("Creating splice_vault.tsv.gz...")

splice_vault_data = {
    'transcript_id': [f'ENST{i:08d}' for i in range(1, 11)],
    'junction': [f'chr{np.random.randint(1,22)}:{np.random.randint(1000,100000)}-{np.random.randint(1000,100000)}' for _ in range(10)],
    'count': [np.random.randint(50, 5000) for _ in range(10)],
    'score': [round(np.random.uniform(0, 1), 3) for _ in range(10)],
    'tissue': np.random.choice(['brain', 'heart', 'liver', 'kidney', 'lung'], 10)
}

splice_vault_df = pd.DataFrame(splice_vault_data)
splice_vault_df.to_csv('data/splice_vault.tsv.gz', sep='\t', index=False, compression='gzip')

# Generate a small mrsd_expression dataset (10 rows)
print("Creating mrsd_expression.tsv.gz...")

mrsd_expression_data = {
    'gene_id': [f'ENSG{i:08d}' for i in range(1, 11)],
    'tpm': [round(np.random.uniform(0.5, 50), 2) for _ in range(10)],
    'fpkm': [round(np.random.uniform(0.1, 40), 2) for _ in range(10)],
    'sample': [f'sample_{i}' for i in range(1, 11)],
    'condition': np.random.choice(['control', 'treatment'], 10)
}

mrsd_expression_df = pd.DataFrame(mrsd_expression_data)
mrsd_expression_df.to_csv('data/mrsd_expression.tsv.gz', sep='\t', index=False, compression='gzip')

print("\nSmall test datasets created successfully!")
print(f"Created mrsd_splice.tsv.gz with {len(mrsd_splice_df)} rows")
print(f"Created splice_vault.tsv.gz with {len(splice_vault_df)} rows")
print(f"Created mrsd_expression.tsv.gz with {len(mrsd_expression_df)} rows")
print("\nYou can now run the application with 'python run_app.py'")
