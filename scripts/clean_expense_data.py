import pandas as pd
from openai import OpenAIEmbeddings  # or use HuggingFace
from sklearn.metrics.pairwise import cosine_similarity

# Step 1: Load raw data
df = pd.read_csv("data/raw_expenses.csv")

# Step 2: Drop rows with missing or zero amounts
df = df[df['Amount'] > 0]
df.dropna(subset=['Date', 'Description'], inplace=True)

# Step 3: Standardize category names
manual_map = {
    "Starbucks": "Coffee", 
    "Subway": "Fast Food", 
    "Mercado Pago": "Groceries"
}
df['Category'] = df['Description'].map(manual_map).fillna(df['Category'])

# Step 4 (Optional): Use embeddings to auto-cluster unknowns
# For rows where category is missing or vague, use semantic similarity to classify

# Save clean version
df.to_csv("data/clean_expenses.csv", index=False)
print("✅ Cleaned file saved to data/clean_expenses.csv")