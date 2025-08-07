# 💸 Financial Bot - Tabular RAG

## 📚 Project Vision

Financial Bot is an AI-powered financial assistant that leverages Tabular RAG (Retrieval-Augmented Generation) to help you analyze your monthly expense data—intelligently, semantically, and conversationally.

### Key Features

- **Natural Language Queries**: Ask questions like:
  - "How much did I spend on takeout last month?"
  - "What categories spiked compared to June?"
  - "Show me spending related to leisure or self-care."
- **No SQL Required**: Chat with your data using natural language
- **Schema-Aware**: Automatically understands your database structure
- **Semantic Understanding**: Maps natural language to relevant data categories

## 🚀 Quick Start

### 1. Prepare Your Data

1. **Add Raw Data**: Place your Toshl export files in `data/raw/`
   ```
   financial-bot-trag/
   └── data/
       └── raw/
           ├── Toshl_export_June_2025.csv
           └── Toshl_export_July_2025.csv
   ```

2. **Clean the Data**:
   ```bash
   # Process a single file
   python scripts/clean_expense_data.py --input data/raw/Toshl_export_June_2025.csv
   
   # Process multiple files
   for file in data/raw/Toshl_export_*.csv; do
       python scripts/clean_expense_data.py --input "$file"
   done
   ```
   Cleaned files will be saved to `data/clean/` with names like `toshl_june2025_clean.csv`

### 2. Set Up the Database

1. **Build the database** with your cleaned data:
   ```bash
   python scripts/build_db.py data/clean/toshl_june2025_clean.csv
   ```
   This creates/updates tables (expenses, incomes) and views (meta, v_expenses_monthly, v_incomes_monthly).

2. **Verify the import**:
   ```bash
   sqlite3 -header -column data/clean/finances.db "SELECT * FROM meta;"
   ```

### 3. Generate Schema Snapshot (for AI context)

```bash
python -m scripts.snapshot_schema
```
This creates `data/clean/schema_snapshot.json` which helps the AI understand your database structure.

### 4. Start Querying

Ask questions about your finances:
```bash
python scripts/run_sqlgen.py "How much did I spend on groceries last month?"
```

## 📋 Data Formats

### Input Files
Toshl export CSV files should include these columns (case insensitive):
- Date, Account, Category, Tags
- Expense amount, Income amount
- Currency, In main currency
- Description

### Database Schema
- **expenses**: date, category, tags, expense, amount_clp, description
- **incomes**: date, category, tags, income, amount_clp, description

## 🛠️ Tech Stack

- **Backend**: Python with SQLite
- **AI/ML**: OpenAI LLM for natural language understanding and SQL generation
- **Data Processing**: Automated cleaning and transformation pipelines

## 💭 Why This Project?

Most expense tracking tools only categorize transactions but don't understand natural language queries. This system bridges that gap by:
- Understanding nuanced financial questions
- Mapping natural language to your actual spending data
- Providing meaningful insights without requiring technical knowledge
- Giving you control over your financial narrative through simple conversation

## 📝 License
*(License information will be added here)*