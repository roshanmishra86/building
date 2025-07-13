import streamlit as st
from modules import data_processing, analytics, visualizations
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="Customer Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- Title and Description ---
st.title("📊 Customer Analytics Dashboard")
st.markdown("""
This dashboard provides insights into customer behavior and sales performance
for an e-commerce business. Use the sidebar to navigate through different analyses.
""")

# --- Sidebar ---
st.sidebar.title("Navigation")
analysis_choice = st.sidebar.radio("Go to", ["Home", "Customer Segmentation (RFM)", "Customer Lifetime Value", "Sales Performance"])

# --- Data Loading and Caching ---
DATA_PATH = "data/sample_ecommerce_data.csv"
df = data_processing.load_data(DATA_PATH)
df_processed = data_processing.preprocess_data(df.copy() if df is not None else None)

# --- Home Page ---
if analysis_choice == "Home":
    st.header("Business Overview")
    if df_processed is not None:
        total_revenue = df_processed['TotalPrice'].sum()
        total_customers = df_processed['CustomerID'].nunique()
        total_orders = df_processed['InvoiceNo'].nunique()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue", f"${total_revenue:,.2f}")
        col2.metric("Total Unique Customers", f"{total_customers:,}")
        col3.metric("Total Orders", f"{total_orders:,}")

        st.subheader("Data Preview")
        st.dataframe(df_processed.head())
    else:
        st.warning("Could not load or process data. Please check the data file.")

# --- Customer Segmentation (RFM) ---
elif analysis_choice == "Customer Segmentation (RFM)":
    st.header("Customer Segmentation using RFM Analysis")

    if df_processed is not None:
        rfm_data = analytics.calculate_rfm(df_processed)
        rfm_segmented = analytics.segment_customers(rfm_data)

        st.subheader("RFM Segmentation Plot")
        fig_rfm = visualizations.create_rfm_scatter(rfm_segmented)
        st.plotly_chart(fig_rfm, use_container_width=True)

        st.subheader("Customer Segments")
        st.dataframe(rfm_segmented)

        st.sidebar.header("Filter by Segment")
        selected_segment = st.sidebar.selectbox("Choose a customer segment", rfm_segmented['Customer_Segment'].unique())
        st.subheader(f"Customers in '{selected_segment}' Segment")
        st.dataframe(rfm_segmented[rfm_segmented['Customer_Segment'] == selected_segment])

    else:
        st.warning("Data not available for RFM analysis.")


# --- Sales Performance ---
elif analysis_choice == "Sales Performance":
    st.header("Sales Performance Metrics")

    if df_processed is not None:
        st.subheader("Monthly Sales Revenue Trend")
        fig_sales_trend = visualizations.create_sales_trend(df_processed)
        st.plotly_chart(fig_sales_trend, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Top Selling Products")
            top_n_products = st.slider("Select number of top products", 5, 20, 10)
            fig_top_products = visualizations.create_top_products_bar(df_processed, top_n=top_n_products)
            st.plotly_chart(fig_top_products, use_container_width=True)

        with col2:
            st.subheader("Sales by Country")
            fig_country_map = visualizations.create_country_map(df_processed)
            st.plotly_chart(fig_country_map, use_container_width=True)
    else:
        st.warning("Data not available for sales performance analysis.")

# --- Customer Lifetime Value Analysis ---
elif analysis_choice == "Customer Lifetime Value":
    st.header("Customer Lifetime Value Analysis")

    if df_processed is not None:
        # Traditional CLV
        traditional_clv = analytics.calculate_clv(df_processed)
        
        # Predictive CLV
        predictive_clv = analytics.calculate_predictive_clv(df_processed)
        
        tab1, tab2 = st.tabs(["Traditional CLV", "Predictive CLV"])
        
        with tab1:
            if traditional_clv is not None:
                st.subheader("Traditional CLV Analysis")
                st.dataframe(traditional_clv.sort_values(by='CLV', ascending=False))
                
                # Summary statistics
                avg_clv = traditional_clv['CLV'].mean()
                median_clv = traditional_clv['CLV'].median()
                col1, col2 = st.columns(2)
                col1.metric("Average Traditional CLV", f"${avg_clv:,.2f}")
                col2.metric("Median Traditional CLV", f"${median_clv:,.2f}")
            else:
                st.warning("Could not calculate traditional CLV due to insufficient data.")
        
        with tab2:
            st.subheader("Predictive CLV Analysis")
            st.markdown("""
            This analysis uses the Beta-Geometric/Negative Binomial Distribution (BG/NBD) model
            for transaction prediction and the Gamma-Gamma model for monetary value prediction.
            """)
            
            if predictive_clv is not None:
                st.dataframe(predictive_clv)
                
                # Summary statistics
                avg_pred_clv = predictive_clv['predicted_clv'].mean()
                median_pred_clv = predictive_clv['predicted_clv'].median()
                col1, col2 = st.columns(2)
                col1.metric("Average Predicted CLV", f"${avg_pred_clv:,.2f}")
                col2.metric("Median Predicted CLV", f"${median_pred_clv:,.2f}")
                
                # Distribution plot of predicted CLV
                st.subheader("Distribution of Predicted CLV")
                fig = px.histogram(predictive_clv, 
                                x='predicted_clv',
                                title='Distribution of Predicted Customer Lifetime Value',
                                labels={'predicted_clv': 'Predicted CLV ($)'},
                                nbins=50)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Could not calculate predictive CLV. This usually happens when there are not enough repeat purchases in the data.")
    else:
        st.warning("Data not available for CLV analysis.")
