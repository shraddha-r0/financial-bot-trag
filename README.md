# 💸 Financial Bot - Tabular RAG

## 📚 Project Vision

Financial Bot is an AI-powered financial assistant that leverages Tabular RAG (Retrieval-Augmented Generation) to help you analyze your monthly expense data—intelligently, semantically, and conversationally.

Simply drop in your monthly CSVs, and the system enables you to ask natural language questions like:

- "How much did I spend on takeout last month?"
- "What categories spiked compared to June?"
- "Show me spending related to leisure or self-care."

No rigid categories. No SQL skills needed. Just chat with your data using natural language queries.

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