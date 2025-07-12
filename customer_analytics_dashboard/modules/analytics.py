import pandas as pd
import streamlit as st
from datetime import timedelta
from lifetimes import BetaGeoFitter, GammaGammaFitter
from lifetimes.utils import summary_data_from_transaction_data

def calculate_rfm(df):
    """
    Calculates Recency, Frequency, and Monetary values for each customer.
    """
    if df is None:
        return None

    snapshot_date = df['InvoiceDate'].max() + timedelta(days=1)

    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda date: (snapshot_date - date.max()).days,
        'InvoiceNo': 'nunique',
        'TotalPrice': 'sum'
    })

    rfm.rename(columns={
        'InvoiceDate': 'Recency',
        'InvoiceNo': 'Frequency',
        'TotalPrice': 'MonetaryValue'
    }, inplace=True)

    return rfm

def segment_customers(rfm):
    """
    Segments customers into different tiers based on RFM scores.
    """
    if rfm is None:
        return None

    r_labels = range(4, 0, -1)
    f_labels = range(1, 5)
    m_labels = range(1, 5)

    # Add robust error handling with duplicates='drop' to handle non-unique bin edges
    try:
        rfm['R_Score'] = pd.qcut(rfm['Recency'], 4, labels=r_labels, duplicates='drop')
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=f_labels, duplicates='drop')
        rfm['M_Score'] = pd.qcut(rfm['MonetaryValue'], 4, labels=m_labels, duplicates='drop')
    except ValueError as e:
        st.warning(f"RFM segmentation encountered an issue due to data distribution. Some scores may be imprecise: {str(e)}")
        # If qcut fails even with duplicates='drop', fall back to simpler quartile assignment
        rfm['R_Score'] = pd.qcut(rfm['Recency'].rank(method='first'), 4, labels=r_labels)
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=f_labels)
        rfm['M_Score'] = pd.qcut(rfm['MonetaryValue'].rank(method='first'), 4, labels=m_labels)

    rfm['RFM_Segment'] = rfm.apply(lambda x: str(x['R_Score']) + str(x['F_Score']) + str(x['M_Score']), axis=1)
    rfm['RFM_Score'] = rfm[['R_Score', 'F_Score', 'M_Score']].sum(axis=1)

    def get_customer_segment(rfm_score):
        if rfm_score >= 9:
            return 'Top Customers'
        elif rfm_score >= 5:
            return 'Potential Customers'
        elif rfm_score >= 3:
            return 'At-Risk Customers'
        else:
            return 'Lost Customers'

    rfm['Customer_Segment'] = rfm['RFM_Score'].apply(get_customer_segment)

    return rfm

def calculate_clv(df):
    """
    Calculates the Customer Lifetime Value (CLV) for each customer.
    """
    if df is None:
        return None

    clv = df.groupby('CustomerID').agg({
        'TotalPrice': 'sum',
        'InvoiceNo': 'nunique'
    })
    clv.rename(columns={'TotalPrice': 'TotalRevenue', 'InvoiceNo': 'TotalTransactions'}, inplace=True)
    
    # Add error handling for division by zero
    clv['AverageOrderValue'] = clv['TotalRevenue'].div(clv['TotalTransactions']).fillna(0)

    total_customers = len(df['CustomerID'].unique())
    if total_customers > 0:
        purchase_frequency = clv['TotalTransactions'] / total_customers
    else:
        purchase_frequency = 0
    clv['PurchaseFrequency'] = purchase_frequency

    clv['CustomerValue'] = clv['AverageOrderValue'] * clv['PurchaseFrequency']
    clv['CLV'] = clv['CustomerValue'] * 3  # Assuming a 3-year customer lifetime for simplicity

    return clv

def calculate_predictive_clv(df):
    """
    Calculates predictive CLV using BG/NBD and Gamma-Gamma models.
    """
    if df is None:
        return None

    try:
        summary = summary_data_from_transaction_data(
            df,
            customer_id_col='CustomerID',
            datetime_col='InvoiceDate',
            monetary_value_col='TotalPrice'
        )

        # Filter for customers with repeat purchases to ensure model stability
        summary = summary[summary['frequency'] > 0]

        if len(summary) < 2:
            st.warning("Insufficient data for predictive CLV calculation. Need more customers with repeat purchases.")
            return None

        # Add penalizer coefficients to help model convergence with small datasets
        bgf = BetaGeoFitter(penalizer_coef=0.001)
        ggf = GammaGammaFitter(penalizer_coef=0.001)

        # Fit the models with error handling
        try:
            bgf.fit(summary['frequency'], summary['recency'], summary['T'])
            ggf.fit(summary['frequency'], summary['monetary_value'])

            # Calculate conditional expected average profit
            clv = ggf.conditional_expected_average_profit(
                summary['frequency'],
                summary['monetary_value']
            )

            # Add predictive CLV to the summary table
            summary['predicted_clv'] = clv
            return summary.sort_values(by='predicted_clv', ascending=False)

        except Exception as e:
            st.warning(f"Could not calculate predictive CLV due to model fitting issues: {str(e)}")
            return None

    except Exception as e:
        st.warning(f"Error preparing data for CLV calculation: {str(e)}")
        return None
