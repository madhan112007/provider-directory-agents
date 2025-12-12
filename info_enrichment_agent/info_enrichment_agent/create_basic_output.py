import pandas as pd

# Read the enriched CSV
df = pd.read_csv('data/output/enriched_profiles_20251207_185716.csv')

# Select basic level columns
basic_columns = [
    'name',
    'address_new',
    'phone_new',
    'npi_new',
    'years_experience',
    'primary_specialty',
    'license_status'
]

# Rename columns for clarity
column_mapping = {
    'address_new': 'address',
    'phone_new': 'phone',
    'npi_new': 'npi'
}

# Create new dataframe with selected columns
basic_df = df[basic_columns].copy()
basic_df = basic_df.rename(columns=column_mapping)

# Save to output.csv
basic_df.to_csv('output.csv', index=False)

print(f"Created output.csv with {len(basic_df)} records and {len(basic_columns)} columns")
print("Columns:", list(basic_df.columns))
