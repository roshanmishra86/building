
import pandas as pd
import matplotlib.pyplot as plt
import sqlalchemy
import logging
import os

# --- Configuration ---
INPUT_CSV_PATH = "data/sales_data.csv"
OUTPUT_DIR = "output"
DATABASE_PATH = os.path.join(OUTPUT_DIR, "sales_data.db")
LOG_FILE_PATH = os.path.join(OUTPUT_DIR, "data_pipeline.log")
TOP_N_PRODUCTS = 10

# --- Setup Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler()
    ]
)

def clean_data(df):
    """Cleans the dataframe by handling missing values."""
    logging.info("Starting data cleaning...")
    # Drop rows with missing date or product_id
    df.dropna(subset=['date', 'product_id'], inplace=True)
    # Fill missing quantity and revenue with the mean
    df['quantity'].fillna(df['quantity'].mean(), inplace=True)
    df['revenue'].fillna(df['revenue'].mean(), inplace=True)
    logging.info("Data cleaning complete.")
    return df

def generate_insights(df):
    """Generates insights from the dataframe."""
    logging.info("Generating insights...")
    top_products = df.groupby('product_id')['revenue'].sum().nlargest(TOP_N_PRODUCTS)
    logging.info(f"""Top {TOP_N_PRODUCTS} products by revenue:
{top_products}""")
    return top_products

def create_visualisations(top_products):
    """Creates and saves visualisations."""
    logging.info("Creating visualisations...")
    plt.figure(figsize=(10, 6))
    top_products.plot(kind='bar')
    plt.title(f"Top {TOP_N_PRODUCTS} Products by Revenue")
    plt.xlabel("Product ID")
    plt.ylabel("Total Revenue")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "top_products_revenue.png"))
    logging.info("Visualisations saved to output/top_products_revenue.png")

def store_in_database(df):
    """Stores the cleaned dataframe in a SQLite database."""
    logging.info("Storing data in database...")
    engine = sqlalchemy.create_engine(f"sqlite:///{DATABASE_PATH}")
    df.to_sql('sales', engine, if_exists='replace', index=False)
    logging.info(f"Data stored in database at {DATABASE_PATH}")

def main():
    """Main function to run the data pipeline."""
    logging.info("Starting data pipeline...")
    try:
        df = pd.read_csv(INPUT_CSV_PATH)
        df = clean_data(df)
        top_products = generate_insights(df)
        create_visualisations(top_products)
        store_in_database(df)
    except FileNotFoundError:
        logging.error(f"Error: Input file not found at {INPUT_CSV_PATH}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    logging.info("Data pipeline finished.")

if __name__ == "__main__":
    main()
