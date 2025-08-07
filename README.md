# 💸 Financial Bot - Tabular RAG

## 📚 Project Vision

Financial Bot is an AI-powered financial assistant that leverages Tabular RAG (Retrieval-Augmented Generation) to help you analyze your monthly expense data—intelligently, semantically, and conversationally.

Simply drop in your monthly CSVs, and the system enables you to ask natural language questions like:

- "How much did I spend on takeout last month?"
- "What categories spiked compared to June?"
- "Show me spending related to leisure or self-care."

No rigid categories. No SQL skills needed. Just chat with your data using natural language queries.

---

## 🛠️ Database Management

### Building and Updating the Database

Build or update the database with a cleaned CSV:
```bash
python scripts/build_db.py data/clean/toshl_june2025_clean.csv
```
This appends the CSV data into `data/clean/finances.db`, creates/updates the tables (expenses, incomes), and creates/updates the views (meta, v_expenses_monthly, v_incomes_monthly).

### Checking Database Status

Check summary stats:
```bash
sqlite3 -header -column data/clean/finances.db "SELECT * FROM meta;"
```

### Viewing Monthly Rollups

Preview monthly expenses:
```bash
sqlite3 -header -column data/clean/finances.db "SELECT * FROM v_expenses_monthly LIMIT 10;"
```

Preview monthly incomes:
```bash
sqlite3 -header -column data/clean/finances.db "SELECT * FROM v_incomes_monthly LIMIT 10;"
```

### Generating Schema Snapshots

Generate a schema snapshot in JSON format:
```bash
python -m scripts.snapshot_schema
```
This saves the output to: `data/clean/schema_snapshot.json`

---

## 🎯 Key Objectives

### 🧠 Schema-Aware SQL Generation
Automatically parse your SQLite schema using PRAGMA and enable the LLM to craft accurate SQL queries based on your database structure.

### 🔍 Hybrid RAG for Tables
Combine SQL retrieval with semantic filtering to understand and map natural language terms (like "takeout", "fun", or "groceries") to relevant data categories.

### 💬 Natural Language Interface
Answer one-off questions through a lightweight, conversational interface that doesn't require technical expertise.

### 🔄 Repeatable Pipeline
Easily add new monthly CSVs, clean them, and analyze them through the same streamlined system.

---

## 🛠️ Tech Stack

### Backend

- **Database**: SQLite for fast, lightweight tabular storage
- **AI/ML**: 
  - LLM (OpenAI or similar) for:
    - Schema understanding
    - SQL generation
    - Semantic category mapping
    - Natural language response generation

## 🧹 Data Cleaning

Before analysis, use the `clean_expense_data.py` script to process raw Toshl export files:

### Features

- Converts date formats consistently
- Handles currency formatting (removes thousands separators)
- Standardizes column names
- Adds useful derived fields (day of week)
- Handles missing values appropriately
- Outputs cleaned CSV with standardized naming

### Usage

```bash
# Basic usage (saves to data/clean/toshl_<month><year>_clean.csv)
python scripts/clean_expense_data.py --input data/raw/Toshl_export_June_2025.csv

# Specify custom output location
python scripts/clean_expense_data.py --input data/raw/Toshl_export_June_2025.csv --output data/processed/my_cleaned_data.csv

# Process multiple files
for file in data/raw/Toshl_export_*.csv; do
    python scripts/clean_expense_data.py --input "$file"
done
```

### Input Format

Expects Toshl export CSV files with these columns (case insensitive):

- Date
- Account
- Category
- Tags
- Expense amount
- Income amount
- Currency
- In main currency
- Description

### Output

Cleaned CSV files are saved to `data/clean/` by default with the naming convention:
`toshl_<month><year>_clean.csv` (e.g., `toshl_june2025_clean.csv`)

## 💾 Database Setup

After cleaning your Toshl export files, use the `build_db.py` script to load the data into an SQLite database for analysis:

### Features

- Creates/updates an SQLite database at `data/clean/finances.db`
- Separates data into two tables: `expenses` and `incomes`
- Handles data type conversion automatically
- Overwrites existing tables with fresh data

### Usage

```bash
# Basic usage
python scripts/build_db.py data/clean/toshl_june2025_clean.csv

# Using a full path
python scripts/build_db.py /path/to/your/cleaned_expenses.csv
```

### Input Format

Expects a cleaned CSV file with these columns:
- date
- category
- tags
- expense
- income
- amount_clp

### Output

Creates or updates `data/clean/finances.db` with two tables:
- `expenses`: Contains date, category, tags, expense, amount_clp
- `incomes`: Contains date, category, tags, income, amount_clp

---

## 🛠️ Tech Stack

### Backend
- **Database**: SQLite for fast, lightweight tabular storage
- **AI/ML**: 
  - LLM (OpenAI or similar) for:
    - Schema understanding
    - SQL generation
    - Semantic category mapping
    - Natural language response generation

### Python Pipeline
- Data Ingestion: CSV to SQLite conversion
- Schema Management: Automatic parsing and understanding
- Data Processing: Cleaning and transformation
- Query Execution: Natural language to SQL translation
- Response Generation: Human-readable answers

---

## 💭 Why This Project?

Most expense tracking tools only categorize transactions but don't understand natural language queries. This system bridges that gap by:

- Understanding nuanced financial questions
- Mapping natural language to your actual spending data
- Providing meaningful insights without requiring technical knowledge
- Giving you control over your financial narrative through simple conversation

## 🚀 Getting Started
*(Coming soon - Setup instructions will be added here)*

## 📝 License
*(Coming soon - License information will be added here)*