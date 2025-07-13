import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_rfm_scatter(rfm_segmented):
    """
    Creates an interactive scatter plot for RFM segments.
    """
    if rfm_segmented is None:
        return go.Figure()

    fig = px.scatter(rfm_segmented,
                     x='Recency',
                     y='Frequency',
                     color='Customer_Segment',
                     size='MonetaryValue',
                     hover_name=rfm_segmented.index,
                     title='Customer Segments (RFM)',
                     labels={'Recency': 'Days Since Last Purchase', 'Frequency': 'Number of Purchases'})
    return fig

def create_sales_trend(df):
    """
    Creates a line chart for sales trends over time.
    """
    if df is None:
        return go.Figure()

    sales_by_month = df.set_index('InvoiceDate').groupby(pd.Grouper(freq='M'))['TotalPrice'].sum().reset_index()
    fig = px.line(sales_by_month,
                  x='InvoiceDate',
                  y='TotalPrice',
                  title='Monthly Sales Revenue',
                  labels={'InvoiceDate': 'Month', 'TotalPrice': 'Total Revenue'})
    return fig

def create_top_products_bar(df, top_n=10):
    """
    Creates a bar chart for top-selling products.
    """
    if df is None:
        return go.Figure()

    top_products = df.groupby('Description')['Quantity'].sum().sort_values(ascending=False).head(top_n).reset_index()
    fig = px.bar(top_products,
                 x='Quantity',
                 y='Description',
                 orientation='h',
                 title=f'Top {top_n} Selling Products',
                 labels={'Quantity': 'Total Quantity Sold', 'Description': 'Product'})
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig

def create_country_map(df):
    """
    Creates a choropleth map of sales by country.
    """
    if df is None:
        return go.Figure()

    country_sales = df.groupby('Country')['TotalPrice'].sum().reset_index()
    fig = px.choropleth(country_sales,
                        locations='Country',
                        locationmode='country names',
                        color='TotalPrice',
                        hover_name='Country',
                        color_continuous_scale=px.colors.sequential.Plasma,
                        title='Geographic Distribution of Sales')
    return fig
