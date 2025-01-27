import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# URLs of the raw CSV files on GitHub
orders_url = 'https://raw.githubusercontent.com/jordanngz/Dicoding-Analysis-Data/main/orders_dataset.csv'
order_payments_url = 'https://raw.githubusercontent.com/jordanngz/Dicoding-Analysis-Data/main/order_payments_dataset.csv'
order_items_url = 'https://raw.githubusercontent.com/jordanngz/Dicoding-Analysis-Data/main/order_items_dataset.csv'
products_url = 'https://raw.githubusercontent.com/jordanngz/Dicoding-Analysis-Data/main/products_dataset.csv'
order_reviews_url = 'https://raw.githubusercontent.com/jordanngz/Dicoding-Analysis-Data/main/order_reviews_dataset.csv'

# Load data directly from the raw GitHub URLs
orders_df = pd.read_csv(orders_url)
order_payments_df = pd.read_csv(order_payments_url)
order_items_df = pd.read_csv(order_items_url)
products_df = pd.read_csv(products_url)
order_reviews_df = pd.read_csv(order_reviews_url)

# Data Cleaning Process
products_df.fillna({
    'product_category_name': 'Unknown',
    'product_name_lenght': 0,
    'product_description_lenght': 0,
    'product_photos_qty': 0,
    'product_weight_g': 0,
    'product_length_cm': 0,
    'product_height_cm': 0,
    'product_width_cm': 0
}, inplace=True)

order_items_df.dropna(subset=['order_id', 'order_item_id', 'product_id', 'seller_id', 'price'], inplace=True)

orders_df.fillna({
    'order_status': 'Unknown',
    'order_approved_at': 'Unknown',
    'order_delivered_carrier_date': 'Unknown',
    'order_delivered_customer_date': 'Unknown'
}, inplace=True)

order_reviews_df.fillna({
    'review_comment_title': 'No Title',
    'review_comment_message': 'No Message'
}, inplace=True)

# Remove duplicates
dfs = [order_items_df, products_df, orders_df]
for df in dfs:
    df.drop_duplicates(inplace=True)

# Add 'season_name' column to orders_df
orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])

def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Fall'

orders_df['season_name'] = orders_df['order_purchase_timestamp'].dt.month.apply(get_season)

# Sidebar for season selection and filters
st.sidebar.header('Filters')
season_filter = st.sidebar.selectbox("Select Season", ['All', 'Winter', 'Spring', 'Summer', 'Fall'])

start_date = st.sidebar.date_input("Start Date", orders_df['order_purchase_timestamp'].min())
end_date = st.sidebar.date_input("End Date", orders_df['order_purchase_timestamp'].max())

filtered_orders = orders_df[
    (orders_df['order_purchase_timestamp'].dt.date >= start_date) &
    (orders_df['order_purchase_timestamp'].dt.date <= end_date)
]

if season_filter != 'All':
    filtered_orders = filtered_orders[filtered_orders['season_name'] == season_filter]

# Title of the dashboard
st.title('E-commerce Analysis Dashboard')

# Sidebar navigation
selection = st.sidebar.radio('Navigation', [
    'Home', 'Category Sales', 'Payment Satisfaction', 'Customer Frequency Analysis', 'Daily Orders', 'Product Performance'
])

# Home section
if selection == 'Home':
    st.header('Welcome to the E-commerce Analysis Dashboard!')
    st.write('Explore insights about sales, customer behavior, satisfaction, and product performance.')

# Category Sales Visualization
if selection == 'Category Sales':
    st.header('Sales by Product Category')

    order_items_products_df = pd.merge(order_items_df, products_df[['product_id', 'product_category_name']], on='product_id')
    order_items_products_df = pd.merge(order_items_products_df, filtered_orders[['order_id']], on='order_id')

    sales_by_category = order_items_products_df.groupby('product_category_name')['price'].sum().reset_index()
    sales_by_category_sorted = sales_by_category.sort_values(by='price', ascending=False)

    fig, ax = plt.subplots(figsize=(15, 8))
    ax.barh(sales_by_category_sorted['product_category_name'], sales_by_category_sorted['price'], color='green')
    ax.set_xlabel('Total Sales')
    ax.set_ylabel('Product Category')
    ax.set_title(f'Sales by Product Category ({season_filter} Season)')

    st.pyplot(fig)

# Payment Satisfaction Visualization
elif selection == 'Payment Satisfaction':
    st.header('Customer Satisfaction by Payment Method')

    payment_reviews_df = pd.merge(order_payments_df, order_reviews_df[['order_id', 'review_score']], on='order_id')
    payment_reviews_filtered = payment_reviews_df[payment_reviews_df['order_id'].isin(filtered_orders['order_id'])]

    payment_review_scores = payment_reviews_filtered.groupby('payment_type')['review_score'].mean().reset_index()

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(payment_review_scores['payment_type'], payment_review_scores['review_score'], color='purple')
    ax.set_xlabel('Average Review Score')
    ax.set_ylabel('Payment Method')
    ax.set_title(f'Payment Satisfaction ({season_filter} Season)')

    st.pyplot(fig)

# Customer Frequency Analysis Visualization
elif selection == 'Customer Frequency Analysis':
    st.header('Customer Frequency Analysis')

    frequency = filtered_orders.groupby('customer_id')['order_id'].count().reset_index()
    frequency.columns = ['customer_id', 'frequency']

    bins = [0, 10, 20, 50, 100, 200]
    labels = ['0-10', '11-20', '21-50', '51-100', '101+']
    frequency['frequency_bin'] = pd.cut(frequency['frequency'], bins=bins, labels=labels)

    bin_counts = frequency['frequency_bin'].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    bin_counts.plot(kind='barh', color='skyblue', ax=ax)
    ax.set_title(f'Distribution of Customers by Transaction Frequency ({season_filter} Season)')
    ax.set_xlabel('Number of Customers')
    ax.set_ylabel('Frequency Bin')

    st.pyplot(fig)

# Daily Orders Visualization
elif selection == 'Daily Orders':
    st.header('Daily Orders and Revenue')

    daily_orders = filtered_orders.groupby(filtered_orders['order_purchase_timestamp'].dt.date).size().reset_index(name='daily_orders')

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(daily_orders['order_purchase_timestamp'], daily_orders['daily_orders'], color='skyblue')
    ax.set_title('Daily Orders Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Number of Orders')

    st.pyplot(fig)

# Product Performance Visualization
elif selection == 'Product Performance':
    st.header('Product Performance')

    order_items_products_df = pd.merge(order_items_df, products_df[['product_id', 'product_category_name']], on='product_id')
    order_items_products_df = pd.merge(order_items_products_df, filtered_orders[['order_id']], on='order_id')

    sales_by_category = order_items_products_df.groupby('product_category_name')['price'].sum().reset_index()
    sales_by_category_sorted = sales_by_category.sort_values(by='price', ascending=False)

    st.write("**Top 5 Product Categories by Total Sales:**")
    st.dataframe(sales_by_category_sorted.head(5))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(sales_by_category_sorted['product_category_name'].head(5), sales_by_category_sorted['price'].head(5), color='green')
    ax.set_title('Top 5 Product Categories')
    ax.set_xlabel('Total Sales')
    ax.set_ylabel('Category')
    st.pyplot(fig)

# Footer
footer_text = """
    <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #f1f1f1;
            text-align: center;
            padding: 10px;
            font-size: 12px;
            color: #555;
        }
    </style>
    <div class="footer">
        Created by Muhammad Jordan, acc min pls :)
    </div>
"""

st.markdown(footer_text, unsafe_allow_html=True)
