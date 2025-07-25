import pandas as pd

# Load dataset
df = pd.read_csv('dataset/cleaned_movies.csv')

# Drop duplicates
df.drop_duplicates(inplace=True)

# Drop rows with missing values in important columns
df.dropna(subset=['title', 'tags', 'genre', 'actor', 'language', 'rating'], inplace=True)

# Remove extra spaces and lowercase for uniformity
df['title'] = df['title'].str.strip()
df['tags'] = df['tags'].str.strip().str.lower()
df['genre'] = df['genre'].str.strip().str.lower()
df['actor'] = df['actor'].str.strip().str.lower()
df['language'] = df['language'].str.strip().str.lower()

# Convert rating to float if not already
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

# Drop rows where rating conversion failed
df.dropna(subset=['rating'], inplace=True)

# Save cleaned data
df.to_csv('cleaned_movies.csv', index=False)

print("✅ Data cleaning completed. Saved as 'cleaned_movies.csv'")
