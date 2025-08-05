import pandas as pd
import sqlite3
import os
import argparse

# Define the CLI arguments
parser = argparse.ArgumentParser()
parser.add_argument("file", help="The CSV file to write to the database")
args = parser.parse_args()

# Paths
csv_path = args.file
db_path = "./data/clean/finances.db"

# Ensure the output directory exists
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Load cleaned CSV into a DataFrame
df = pd.read_csv(csv_path)

# Connect to (or create) SQLite DB
conn = sqlite3.connect(db_path)

# Split the DataFrame into two separate DataFrames for expenses and incomes, 
# and only include non-negative values
expenses_df = df[(df['expense'] > 0)][['date', 'category', 'tags', 'expense', 'amount_clp', 'description', 'day']]
incomes_df = df[(df['income'] > 0)][['date', 'category', 'tags', 'income', 'amount_clp', 'description', 'day']]

# Create tables if they don't exist
conn.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        date DATE,
        category TEXT,
        tags TEXT,
        expense REAL,
        amount_clp REAL,
        description TEXT,
        day TEXT
    )
''')
conn.execute('''
    CREATE TABLE IF NOT EXISTS incomes (
        date DATE,
        category TEXT,
        tags TEXT,
        income REAL,
        amount_clp REAL,
        description TEXT,
        day TEXT
    )
''')

# Insert rows
expenses_df.to_sql('expenses', conn, if_exists="append", index=False)
incomes_df.to_sql('incomes', conn, if_exists="append", index=False)

# Confirm it worked
print(f"✅ Successfully wrote 'expenses' and 'incomes' to SQLite DB at: {db_path}")

# Close connection
conn.close()