# 💸 Financial Bot - Tabular RAG

## 📚 Project Vision

Financial Bot is an AI-powered financial assistant that leverages Tabular RAG (Retrieval-Augmented Generation) to help you analyze your financial data through natural language. It transforms expense and income data into actionable insights with simple, conversational queries.

### ✨ Key Features

- **Natural Language to SQL**: Convert plain English questions into SQL queries
- **Interactive Web Interface**: Beautiful Streamlit UI for easy interaction
- **CLI Support**: Full functionality through command-line interface
- **Schema-Aware**: Automatically understands your database structure
- **Query Logging**: Tracks all queries for analysis and improvement
- **Result Summarization**: Get concise, natural language summaries of your data

## 🏗️ Project Structure

```
financial-bot-trag/
├── app/                    # Core application modules
│   ├── db.py              # Database connection and query execution
│   ├── executor.py        # SQL execution and result handling
│   ├── logger.py          # Query logging functionality
│   ├── packager.py        # Result packaging and formatting
│   ├── prompts.py         # AI prompt templates
│   ├── sqlgen.py          # Natural language to SQL generation
│   ├── sqlguard.py        # SQL query validation
│   └── summarizer.py      # Result summarization
├── data/
│   ├── clean/             # Processed/cleaned data files
│   └── raw/               # Raw input data files
├── logs/                  # Query logs
├── scripts/               # Utility scripts
│   ├── ask.py            # CLI interface for asking questions
│   ├── build_db.py       # Database initialization
│   ├── clean_expense_data.py  # Data cleaning script
│   └── snapshot_schema.py # Generate schema snapshots
├── ui/
│   └── streamlit_app.py  # Web interface
└── requirements.txt      # Python dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- SQLite 3
- [Hugging Face API Token](https://huggingface.co/settings/tokens) (for LLM access)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/financial-bot-trag.git
   cd financial-bot-trag
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   HF_TOKEN=your_huggingface_token_here
   HF_MODEL=meta-llama/Meta-Llama-3-8B-Instruct  # Or your preferred model
   ```

### Data Preparation

1. **Add your financial data**
   Place your export files (CSV) in the `data/raw/` directory.

2. **Clean the data**
   ```bash
   # Process a single file
   python scripts/clean_expense_data.py --input data/raw/your_export.csv
   
   # Or process multiple files
   for file in data/raw/*.csv; do
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
2. **Generate schema snapshot** (for AI context)
   ```bash
   python -m scripts.snapshot_schema
   ```

## 💻 Usage

### Web Interface

```bash
streamlit run ui/streamlit_app.py
```
This creates `data/clean/schema_snapshot.json` which helps the AI understand your database structure.

### Command Line Interface

```bash
# Basic usage
python scripts/ask.py "How much did I spend on groceries last month?"

# With custom database path
python scripts/ask.py --db path/to/your/database.db "Show my top 5 expense categories"

# Verbose output with preview rows
python scripts/ask.py --verbose "What were my largest expenses last quarter?"
```

## 🔍 Example Queries

- "Show me my total spending last month"
- "What were my top 5 expense categories last quarter?"
- "Compare my food expenses between June and July"
- "What's my current monthly savings rate?"
- "Show me all transactions over $100 in the last 3 months"

## 🛠️ Tech Stack

- **Backend**: Python 3.9+
- **Database**: SQLite 3
- **Web Interface**: Streamlit
- **AI/ML**: Hugging Face Transformers
- **Data Processing**: Pandas, NumPy
- **Logging**: CSV-based query logging

## 🔮 Future Improvements

### 1. Hybrid Search with Semantic Search

- **Vector Embeddings**: Store embeddings of transaction descriptions for semantic search
- **Hybrid Queries**: Combine traditional SQL with semantic similarity search
- **Fuzzy Matching**: Better handling of typos and variations in category/tag names

### 2. Budget Rules Engine

- **Custom Rules**: Define budget rules in natural language
- **Alerts**: Get notified when spending exceeds budget
- **Projections**: Forecast future spending based on patterns

### 3. Enhanced Analytics

- **Time Series Analysis**: Identify spending trends over time
- **Anomaly Detection**: Flag unusual transactions
- **Category Insights**: Automated insights about spending patterns

## 🤝 Contributing

Contributions are welcome! Please open an issue to discuss your ideas or submit a pull request.