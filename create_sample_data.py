import pandas as pd
import os

# Create data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')
    print("Created data directory")

# Create sample mrsd_splice dataset
mrsd_splice = pd.DataFrame({
    'gene_id': ['ENSG00000000003', 'ENSG00000000005', 'ENSG00000000419', 'ENSG00000000457', 'ENSG00000000460'],
    'transcript_id': ['ENST00000000003', 'ENST00000000005', 'ENST00000000419', 'ENST00000000457', 'ENST00000000460'],
    'exon_id': ['ENSE00000000003', 'ENSE00000000005', 'ENSE00000000419', 'ENSE00000000457', 'ENSE00000000460'],
    'expression': [10.5, 20.3, 15.7, 8.2, 12.9],
    'sample': ['sample1', 'sample2', 'sample3', 'sample4', 'sample5']
})
import pandas as pd
import os
import numpy as np

# Create data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')
    print("Created data directory")

# Function to generate random gene IDs
def generate_gene_ids(n):
    return [f"ENSG{i:08d}" for i in range(1, n+1)]

# Function to generate random transcript IDs
def generate_transcript_ids(n):
    return [f"ENST{i:08d}" for i in range(1, n+1)]

# Function to generate random sample names
def generate_sample_names(n):
    return [f"sample_{i}" for i in range(1, n+1)]

# Generate mrsd_splice data (20 rows)
print("Creating mrsd_splice.tsv.gz...")
num_splice_rows = 20
gene_ids = generate_gene_ids(num_splice_rows)
transcript_ids = generate_transcript_ids(num_splice_rows)
samples = generate_sample_names(5)  # 5 different sample names

mrsd_splice_data = {
    'gene_id': gene_ids,
    'transcript_id': transcript_ids,
    'sample': np.random.choice(samples, num_splice_rows),
    'expression': np.random.uniform(5, 25, num_splice_rows).round(2),
    'junction_count': np.random.randint(10, 1000, num_splice_rows)
}

mrsd_splice_df = pd.DataFrame(mrsd_splice_data)
mrsd_splice_df.to_csv('data/mrsd_splice.tsv.gz', sep='\t', index=False, compression='gzip')

# Generate splice_vault data (20 rows)
print("Creating splice_vault.tsv.gz...")
num_vault_rows = 20
transcript_ids = generate_transcript_ids(num_vault_rows)

# Generate random genomic positions
chromosomes = ['chr1', 'chr2', 'chr3', 'chr4', 'chr5']
junctions = []
for i in range(num_vault_rows):
    chrom = np.random.choice(chromosomes)
    start = np.random.randint(1000, 100000)
    end = start + np.random.randint(1000, 5000)
    junctions.append(f"{chrom}:{start}-{end}")

splice_vault_data = {
    'transcript_id': transcript_ids,
    'junction': junctions,
    'count': np.random.randint(50, 5000, num_vault_rows),
    'score': np.random.uniform(0, 1, num_vault_rows).round(3),
    'tissue': np.random.choice(['brain', 'heart', 'liver', 'kidney', 'lung'], num_vault_rows)
}

splice_vault_df = pd.DataFrame(splice_vault_data)
splice_vault_df.to_csv('data/splice_vault.tsv.gz', sep='\t', index=False, compression='gzip')

# Generate mrsd_expression data (20 rows)
print("Creating mrsd_expression.tsv.gz...")
num_expression_rows = 20
gene_ids = generate_gene_ids(num_expression_rows)
samples = generate_sample_names(5)  # 5 different sample names

mrsd_expression_data = {
    'gene_id': gene_ids,
    'tpm': np.random.uniform(0.5, 50, num_expression_rows).round(2),
    'fpkm': np.random.uniform(0.1, 40, num_expression_rows).round(2),
    'sample': np.random.choice(samples, num_expression_rows),
    'condition': np.random.choice(['control', 'treatment'], num_expression_rows)
}

mrsd_expression_df = pd.DataFrame(mrsd_expression_data)
mrsd_expression_df.to_csv('data/mrsd_expression.tsv.gz', sep='\t', index=False, compression='gzip')

print("\nSample data creation complete!")
print(f"Created mrsd_splice.tsv.gz with {len(mrsd_splice_df)} rows")
print(f"Created splice_vault.tsv.gz with {len(splice_vault_df)} rows")
print(f"Created mrsd_expression.tsv.gz with {len(mrsd_expression_df)} rows")
# Create sample splice_vault dataset
splice_vault = pd.DataFrame({
    'transcript_id': ['ENST00000000003', 'ENST00000000005', 'ENST00000000419', 'ENST00000000457', 'ENST00000000460'],
    'junction': ['chr1:1000-2000', 'chr1:3000-4000', 'chr2:1000-2000', 'chr2:3000-4000', 'chr3:1000-2000'],
    'count': [100, 200, 150, 80, 120],
    'sample': ['sample1', 'sample2', 'sample3', 'sample4', 'sample5'],
    'gene_name': ['GENE1', 'GENE2', 'GENE3', 'GENE4', 'GENE5']
})

# Create sample mrsd_expression dataset
mrsd_expression = pd.DataFrame({
    'gene_id': ['ENSG00000000003', 'ENSG00000000005', 'ENSG00000000419', 'ENSG00000000457', 'ENSG00000000460'],
    'tpm': [5.2, 10.1, 7.8, 3.4, 6.5],
    'fpkm': [4.5, 9.8, 7.2, 3.1, 6.0],
    'sample': ['sample1', 'sample2', 'sample3', 'sample4', 'sample5'],
    'gene_name': ['GENE1', 'GENE2', 'GENE3', 'GENE4', 'GENE5']
})

# Save datasets to compressed TSV files
mrsd_splice.to_csv('data/mrsd_splice.tsv.gz', sep='\t', index=False, compression='gzip')
print("Created sample mrsd_splice.tsv.gz file")

splice_vault.to_csv('data/splice_vault.tsv.gz', sep='\t', index=False, compression='gzip')
print("Created sample splice_vault.tsv.gz file")

mrsd_expression.to_csv('data/mrsd_expression.tsv.gz', sep='\t', index=False, compression='gzip')
print("Created sample mrsd_expression.tsv.gz file")

print("\nSample data files have been created in the 'data' directory.")
print("You can now run the application with 'python app.py'")
