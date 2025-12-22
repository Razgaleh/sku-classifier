import pandas as pd

# Read the CSV file
df = pd.read_csv('../data/raw_data.csv')

# Set the column names
df.columns = ['PART_SEG', 'PART_NUMBER', 'PART_DESCRIPTION','PART_PRICE']

# Change all PART_SEG values to 'PALO'
df['PART_SEG'] = 'PALO'

df['PART_CATEGORY'] = ''

# Reorder columns: PART_NUMBER first, PART_SEG second
df = df[['PART_NUMBER', 'PART_SEG', 'PART_DESCRIPTION','PART_CATEGORY']]

# Save to updated CSV
df.to_csv('../data/dataset.csv', index=False)


print("Changed Column order: PART_NUMBER, PART_SEG, PART_DESCRIPTION, PART_CATEGORY")
print("All PART_SEG values changed to 'PALO'")
print("Removed PART_PRICE column")
print("CSV updated successfully!")