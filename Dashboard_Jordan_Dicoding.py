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

# Data Cleaning Process (without displaying to the user)

# 1. Cleaning Data in products_df
products_df['product_category_name'].fillna('Unknown', inplace=True)
products_df['product_name_lenght'].fillna(0, inplace=True)
products_df['product_description_lenght'].fillna(0, inplace=True)
products_df['product_photos_qty'].fillna(0, inplace=True)
products_df['product_weight_g'].fillna(0, inplace=True)
products_df['product_length_cm'].fillna(0, inplace=True)
products_df['product_height_cm'].fillna(0, inplace=True)
products_df['product_width_cm'].fillna(0, inplace=True)

# 2. Cleaning Data in order_items_df
order_items_df.dropna(subset=['order_id', 'order_item_id', 'product_id', 'seller_id', 'price'], inplace=True)

# 3. Cleaning Data in orders_df
orders_df['order_status'].fillna('Unknown', inplace=True)
orders_df['order_approved_at'].fillna('Unknown', inplace=True)
orders_df['order_delivered_carrier_date'].fillna('Unknown', inplace=True)
orders_df['order_delivered_customer_date'].fillna('Unknown', inplace=True)

# 4. Cleaning Data in order_reviews_df
order_reviews_df['review_comment_title'].fillna('No Title', inplace=True)
order_reviews_df['review_comment_message'].fillna('No Message', inplace=True)

# Remove duplicates after cleaning
order_items_df.drop_duplicates(inplace=True)
products_df.drop_duplicates(inplace=True)
orders_df.drop_duplicates(inplace=True)

# Add 'season_name' column based on 'order_purchase_timestamp'
def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Fall'

# Add 'season_name' column to orders_df based on the 'order_purchase_timestamp'
orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
orders_df['season_name'] = orders_df['order_purchase_timestamp'].dt.month.apply(get_season)

# Sidebar for season selection
season_filter = st.sidebar.selectbox("Select Season", ['All', 'Winter', 'Spring', 'Summer', 'Fall'])

# Date input for filtering
start_date = st.sidebar.date_input("Start Date", orders_df['order_purchase_timestamp'].min())
end_date = st.sidebar.date_input("End Date", orders_df['order_purchase_timestamp'].max())

# Filter the orders based on the selected date range and season
filtered_orders = orders_df[
    (orders_df['order_purchase_timestamp'].dt.date >= start_date) & 
    (orders_df['order_purchase_timestamp'].dt.date <= end_date)
]

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
    order_items_products_df = pd.merge(filtered_orders, products_df[['product_id', 'product_category_name']], on='product_id')

    # Calculate total sales per product category
    sales_by_category = order_items_products_df.groupby('product_category_name')['price'].sum().reset_index()

    # Sort categories by sales
    sales_by_category_sorted = sales_by_category.sort_values(by='price', ascending=False)

    # Create a horizontal bar plot
    fig, ax = plt.subplots(figsize=(12, 15))
    ax.barh(sales_by_category_sorted['product_category_name'], sales_by_category_sorted['price'], color='green')
    ax.set_xlabel('Total Sales')
    ax.set_ylabel('Product Category')
    ax.set_title(f'Volume of Sales per Product Category for {season_filter} Season')

    st.pyplot(fig)

# Payment Satisfaction Visualization
elif selection == 'Payment Satisfaction':
    st.header('Customer Satisfaction by Payment Method')
    st.write('This chart shows the relationship between payment methods and customer satisfaction.')

    # Merge payment data with review data
    payment_reviews_df = pd.merge(order_payments_df, order_reviews_df[['order_id', 'review_score']], on='order_id')

    # Filter the data based on season
    payment_reviews_filtered = payment_reviews_df[payment_reviews_df['order_id'].isin(filtered_orders['order_id'])]

    # Calculate average review score by payment method
    payment_review_scores = payment_reviews_filtered.groupby('payment_type')['review_score'].mean().reset_index()

    # Create a horizontal bar plot
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(payment_review_scores['payment_type'], payment_review_scores['review_score'], color='purple')
    ax.set_xlabel('Average Review Score')
    ax.set_ylabel('Payment Method')
    ax.set_title(f'Payment Method and Customer Satisfaction for {season_filter} Season')

    st.pyplot(fig)

# Customer Frequency Analysis Visualization
elif selection == 'Customer Frequency Analysis':
    st.header('Customer Frequency Analysis')
    st.write('This section shows the frequency of customer transactions and their distribution.')

    # Binning customers by transaction frequency
    frequency = filtered_orders.groupby('customer_id')['order_id'].count().reset_index()
    frequency.columns = ['customer_id', 'frequency']

    # Adding frequency column to orders_df
    filtered_orders = pd.merge(filtered_orders, frequency, on='customer_id', how='left', suffixes=('', '_freq'))

    # Binning customers by transactions
    bins = [0, 10, 20, 50, 100, 200]
    labels = ['0-10', '11-20', '21-50', '51-100', '101+']
    filtered_orders['frequency_bin'] = pd.cut(filtered_orders['frequency'], bins=bins, labels=labels)

    # Select bin to view number of customers per bin
    selected_bin = st.selectbox("Select a Frequency Bin", labels)

    # Filter data based on the selected bin
    filtered_data = filtered_orders[filtered_orders['frequency_bin'] == selected_bin]

    # Display results
    st.write(f"Showing customers in the {selected_bin} bin")
    st.dataframe(filtered_data[['customer_id', 'frequency', 'frequency_bin']])

    # Visualize customer distribution per bin
    bin_counts = filtered_orders['frequency_bin'].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    bin_counts.plot(kind='barh', color='skyblue', ax=ax)
    ax.set_title(f'Distribution of Customers by Frequency Bin for {season_filter} Season', fontsize=16)
    ax.set_xlabel('Number of Customers', fontsize=14)
    ax.set_ylabel('Frequency Bin', fontsize=14)
    st.pyplot(fig)

# Daily Orders and Revenue Visualization
elif selection == 'Daily Orders':
    st.header('Daily Orders and Revenue')
    
    # Convert 'order_purchase_timestamp' to datetime format
    filtered_orders['order_purchase_timestamp'] = pd.to_datetime(filtered_orders['order_purchase_timestamp'])
    
    # Add Date filter using date_input
    start_date = st.date_input('Start Date', filtered_orders['order_purchase_timestamp'].min())
    end_date = st.date_input('End Date', filtered_orders['order_purchase_timestamp'].max())

    # Filter the orders within the selected date range
    filtered_orders_date = filtered_orders[(filtered_orders['order_purchase_timestamp'].dt.date >= start_date) & 
                                           (filtered_orders['order_purchase_timestamp'].dt.date <= end_date)]
    
    # Extract Date and calculate daily orders
    daily_orders = filtered_orders_date.groupby('order_purchase_timestamp').size().reset_index(name='daily_orders')

    # Calculate total revenue (assuming 'price' column exists in the orders data)
    total_revenue = order_payments_df[(order_payments_df['order_id'].isin(filtered_orders_date['order_id']))]['payment_value'].sum()

    # Create a plot for daily orders
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(daily_orders['order_purchase_timestamp'], daily_orders['daily_orders'], color='skyblue')
    ax.set_title(f'Daily Orders Over Time for {season_filter} Season', fontsize=16)
    ax.set_xlabel('Date', fontsize=14)
    ax.set_ylabel('Total Orders', fontsize=14)
    st.pyplot(fig)

    # Display total orders and revenue
    st.write(f"**Total Orders:** {len(filtered_orders_date)}")
    st.write(f"**Total Revenue:** AUD {total_revenue:,.2f}")

# Product Performance Visualization
elif selection == 'Product Performance':
    st.header('Product Performance')
    
    # Merge order items with product category data
    order_items_products_df = pd.merge(filtered_orders, products_df[['product_id', 'product_category_name']], on='product_id')

    # Calculate total sales per product category
    sales_by_category = order_items_products_df.groupby('product_category_name')['price'].sum().reset_index()

    # Sort categories by sales
    sales_by_category_sorted = sales_by_category.sort_values(by='price', ascending=False)

    # Display top 5 product categories by total sales
    st.write("**Top 5 Product Categories by Total Sales:**")
    st.dataframe(sales_by_category_sorted.head(5))

    # Plot the top 5 product categories
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(sales_by_category_sorted['product_category_name'].head(5), sales_by_category_sorted['price'].head(5), color='green')
    ax.set_xlabel('Total Sales', fontsize=14)
    ax.set_ylabel('Product Category', fontsize=14)
    ax.set_title(f'Top 5 Product Categories by Total Sales for {season_filter} Season', fontsize=16)
    st.pyplot(fig)

    # Display bottom 5 product categories by total sales
    st.write("**Bottom 5 Product Categories by Total Sales:**")
    st.dataframe(sales_by_category_sorted.tail(5))

    # Plot the bottom 5 product categories
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(sales_by_category_sorted['product_category_name'].tail(5), sales_by_category_sorted['price'].tail(5), color='red')
    ax.set_xlabel('Total Sales', fontsize=14)
    ax.set_ylabel('Product Category', fontsize=14)
    ax.set_title(f'Bottom 5 Product Categories by Total Sales for {season_filter} Season', fontsize=16)
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
            border-top: 1px solid #ddd;
        }
        .footer a {
            text-decoration: none;
            color: #1e90ff;
        }
        .footer a:hover {
            text-decoration: underline;
        }
    </style>
    <div class="footer">
        Created by Muhammad Jordan, acc min pls : )  
    </div>
"""
st.markdown(footer_text, unsafe_allow_html=True)
