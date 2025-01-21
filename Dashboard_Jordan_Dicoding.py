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

# Convert 'order_purchase_timestamp' to datetime format for filtering by date
orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])

# Extract 'season' from the 'order_purchase_timestamp' for seasonal filtering
orders_df['season'] = orders_df['order_purchase_timestamp'].dt.month % 12 // 3 + 1
season_dict = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
orders_df['season_name'] = orders_df['season'].map(season_dict)

# Sidebar for filtering options
st.sidebar.header('Filter Options')

# Date Range Filter
start_date = st.sidebar.date_input('Start Date', orders_df['order_purchase_timestamp'].min())
end_date = st.sidebar.date_input('End Date', orders_df['order_purchase_timestamp'].max())

# Season Filter
season_filter = st.sidebar.selectbox('Select Season', options=['All', 'Spring', 'Summer', 'Fall', 'Winter'])

# Filter data based on date range
filtered_orders = orders_df[(orders_df['order_purchase_timestamp'].dt.date >= pd.to_datetime(start_date).date()) &
                            (orders_df['order_purchase_timestamp'].dt.date <= pd.to_datetime(end_date).date())]

# Further filter data based on the selected season
if season_filter != 'All':
    filtered_orders = filtered_orders[filtered_orders['season_name'] == season_filter]

# Title of the dashboard
st.title('E-commerce Analysis Dashboard')

# Sidebar for navigation
st.sidebar.header('Navigation')
selection = st.sidebar.radio('Go to', ['Home', 'Category Sales', 'Payment Satisfaction', 'Customer Frequency Analysis', 'Daily Orders', 'Product Performance'])

# Home section
if selection == 'Home':
    st.header('Welcome to the Public E-commerce Dicoding Analysis Dashboard! :sparkles:')
    st.write('This dashboard provides insights into daily orders, total revenue, product sales by category, customer satisfaction, transaction frequency analysis, and product performance.')

# Category Sales Visualization
if selection == 'Category Sales':
    st.header('Sales by Product Category')
    st.write('This chart shows total sales by product category.')

    # Merge order items with product category data
    order_items_products_df = pd.merge(order_items_df, products_df[['product_id', 'product_category_name']], on='product_id')

    # Calculate total sales per product category
    sales_by_category = order_items_products_df.groupby('product_category_name')['price'].sum().reset_index()

    # Sort categories by sales
    sales_by_category_sorted = sales_by_category.sort_values(by='price', ascending=False)

    # Create a horizontal bar plot
    fig, ax = plt.subplots(figsize=(12,15))
    ax.barh(sales_by_category_sorted['product_category_name'], sales_by_category_sorted['price'], color='green')
    ax.set_xlabel('Total Sales')
    ax.set_ylabel('Product Category')
    ax.set_title('Volume of Sales per Product Category')

    st.pyplot(fig)

# Payment Satisfaction Visualization
elif selection == 'Payment Satisfaction':
    st.header('Customer Satisfaction by Payment Method')
    st.write('This chart shows the relationship between payment methods and customer satisfaction.')

    # Merge payment data with review data
    payment_reviews_df = pd.merge(order_payments_df, order_reviews_df[['order_id', 'review_score']], on='order_id')

    # Calculate average review score by payment method
    payment_review_scores = payment_reviews_df.groupby('payment_type')['review_score'].mean().reset_index()

    # Create a horizontal bar plot
    fig, ax = plt.subplots(figsize=(8,6))
    ax.barh(payment_review_scores['payment_type'], payment_review_scores['review_score'], color='purple')
    ax.set_xlabel('Average Review Score')
    ax.set_ylabel('Payment Method')
    ax.set_title('Payment Method and Customer Satisfaction')

    st.pyplot(fig)

# Customer Frequency Analysis Visualization
elif selection == 'Customer Frequency Analysis':
    st.header('Customer Frequency Analysis')
    st.write('This section shows the frequency of customer transactions and their distribution.')

    # Binning pelanggan berdasarkan jumlah transaksi
    frequency = orders_df.groupby('customer_id')['order_id'].count().reset_index()
    frequency.columns = ['customer_id', 'frequency']

    # Menambahkan kolom 'frequency' ke dalam orders_df
    orders_df = pd.merge(orders_df, frequency, on='customer_id', how='left', suffixes=('', '_freq'))

    # Binning pelanggan berdasarkan transaksi
    bins = [0, 10, 20, 50, 100, 200]
    labels = ['0-10', '11-20', '21-50', '51-100', '101+']
    orders_df['frequency_bin'] = pd.cut(orders_df['frequency'], bins=bins, labels=labels)

    # Interaktif: Pilih bin untuk melihat jumlah pelanggan per bin
    selected_bin = st.selectbox("Select a Frequency Bin", labels)

    # Filter data berdasarkan pilihan bin
    filtered_data = orders_df[orders_df['frequency_bin'] == selected_bin]

    # Menampilkan hasil
    st.write(f"Showing customers in the {selected_bin} bin")
    st.dataframe(filtered_data[['customer_id', 'frequency', 'frequency_bin']])

    # Visualisasi distribusi pelanggan per bin
    bin_counts = orders_df['frequency_bin'].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10,6))
    bin_counts.plot(kind='barh', color='skyblue', ax=ax)
    ax.set_title('Distribution of Customers by Frequency Bin', fontsize=16)
    ax.set_xlabel('Number of Customers', fontsize=14)
    ax.set_ylabel('Frequency Bin', fontsize=14)
    st.pyplot(fig)

# Daily Orders and Revenue Visualization
elif selection == 'Daily Orders':
    st.header('Daily Orders and Revenue')
    
    # Filter the orders within the selected date range
    filtered_orders = orders_df[(orders_df['order_purchase_timestamp'].dt.date >= start_date) &
                                 (orders_df['order_purchase_timestamp'].dt.date <= end_date)]
    
    # Extract Date and calculate daily orders
    daily_orders = filtered_orders.groupby('order_purchase_timestamp').size().reset_index(name='daily_orders')

    # Calculate total revenue
    total_revenue = order_payments_df[(order_payments_df['order_id'].isin(filtered_orders['order_id']))]['payment_value'].sum()

    # Create a plot for daily orders
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(daily_orders['order_purchase_timestamp'], daily_orders['daily_orders'], color='skyblue')
    ax.set_title('Daily Orders Over Time', fontsize=16)
    ax.set_xlabel('Date', fontsize=14)
    ax.set_ylabel('Total Orders', fontsize=14)
    st.pyplot(fig)

    # Display total orders and revenue
    st.write(f"**Total Orders:** {len(filtered_orders)}")
    st.write(f"**Total Revenue:** AUD {total_revenue:,.2f}")

elif selection == 'Product Performance':
    st.header('Product Performance')
    
    # Menggabungkan order_items dengan produk untuk mendapatkan kategori produk
    order_items_products_df = pd.merge(order_items_df, products_df[['product_id', 'product_category_name']], on='product_id')

    # Menghitung total penjualan per kategori produk
    sales_by_category = order_items_products_df.groupby('product_category_name')['price'].sum().reset_index()

    # Mengurutkan kategori berdasarkan total penjualan
    sales_by_category_sorted = sales_by_category.sort_values(by='price', ascending=False)

    # Menampilkan kategori produk terlaris
    st.write("**Top 5 Product Categories by Total Sales:**")
    st.dataframe(sales_by_category_sorted.head(5))

    # Visualisasi kategori produk terlaris
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(sales_by_category_sorted['product_category_name'].head(5), sales_by_category_sorted['price'].head(5), color='green')
    ax.set_xlabel('Total Sales', fontsize=14)
    ax.set_ylabel('Product Category', fontsize=14)
    ax.set_title('Top 5 Product Categories by Total Sales', fontsize=16)
    st.pyplot(fig)

    # Menampilkan kategori produk dengan penjualan terendah
    st.write("**Bottom 5 Product Categories by Total Sales:**")
    st.dataframe(sales_by_category_sorted.tail(5))

    # Visualisasi kategori produk dengan penjualan terendah
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(sales_by_category_sorted['product
