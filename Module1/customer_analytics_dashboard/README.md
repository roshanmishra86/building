# Python Customer Analytics Dashboard

This is a comprehensive customer analytics dashboard application built with Streamlit, Pandas, and Plotly. It's designed for e-commerce businesses to gain insights into customer behavior, identify high-value customers, and discover growth opportunities.

## Features

- **Customer Segmentation:** Utilizes RFM (Recency, Frequency, Monetary) analysis to segment customers and calculates Customer Lifetime Value (CLV).
- **Sales Performance Metrics:** Tracks key metrics such as revenue trends, top-selling products, and the geographic distribution of sales.
- **Interactive Business Intelligence Dashboard:** Features interactive charts, Key Performance Indicators (KPIs), and allows for filtering and data drill-downs.

## Technical Specifications

- **Framework:** Streamlit
- **Data Processing:** Pandas
- **Visualization:** Plotly
- **Styling:** Custom professional business theme
- **Error Handling:** Comprehensive data validation and user feedback.
- **Performance:** Optimized for datasets up to 100,000 records.

## Setup and Installation

### Prerequisites

- Python 3.8+
- pip

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://your-repository-url/customer-analytics-dashboard.git
    cd customer-analytics-dashboard
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run the Application

1.  **Place your data:**
    - The application looks for a CSV file in the `data` directory. A sample file `sample_ecommerce_data.csv` is provided.
    - Your CSV file should contain the following columns: `CustomerID`, `InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `Country`.

2.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```

3.  Open your web browser and navigate to the local URL provided by Streamlit (usually `http://localhost:8501`).

## Application Structure

-   `app.py`: The main Streamlit application file.
-   `modules/`: Contains the core logic of the application.
    -   `data_processing.py`: Handles data loading, cleaning, and preprocessing.
    -   `analytics.py`: Includes functions for RFM analysis, CLV calculation, and other metrics.
    -   `visualizations.py`: Manages the creation of Plotly charts.
-   `.streamlit/config.toml`: Streamlit configuration file for theme and other settings.
-   `data/`: Directory for input CSV files.
-   `requirements.txt`: A list of all necessary Python libraries.
-   `README.md`: This file.
