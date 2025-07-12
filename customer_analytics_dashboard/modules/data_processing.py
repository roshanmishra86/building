import pandas as pd
import streamlit as st

@st.cache_data
def load_data(file_path):
    """
    Loads data from a CSV file and performs initial cleaning.
    """
    try:
        df = pd.read_csv(file_path, encoding='ISO-8859-1')
        return df
    except FileNotFoundError:
        st.error(f"Error: The file at {file_path} was not found.")
        return None

def preprocess_data(df):
    """
    Cleans and preprocesses the transaction data.
    """
    if df is None:
        return None

    # Drop rows with missing CustomerID
    df.dropna(axis=0, subset=['CustomerID'], inplace=True)

    # Convert CustomerID to integer
    df['CustomerID'] = df['CustomerID'].astype(int)

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    # Handle negative Quantity and zero UnitPrice
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]

    # Convert InvoiceDate to datetime
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format='%m/%d/%Y %H:%M')

    # Create a TotalPrice column
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']

    return df
