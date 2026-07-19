import pandas as pd
import numpy as np
import os

# Load clean outputs from script 01
orders = pd.read_csv('outputs/orders_clean.csv',
                     parse_dates=['order_purchase_timestamp'])
rfm = pd.read_csv('outputs/rfm_segments.csv')

print("Orders loaded:", orders.shape)
print("RFM loaded:", rfm.shape)

# Extract year and month from timestamp
orders['year_month'] = orders['order_purchase_timestamp'].dt.to_period('M')

# Monthly revenue and order volume
monthly_trends = orders.groupby('year_month').agg(
    total_orders=('order_id', 'count'),
    total_revenue=('total_payment', 'sum'),
    avg_order_value=('total_payment', 'mean'),
    avg_review=('review_score', 'mean'),
    late_delivery_count=('delivery_delay_days', lambda x: (x > 0).sum()),
    total_deliveries=('delivery_delay_days', 'count')
).reset_index()

# Calculate late delivery percentage per month
monthly_trends['late_delivery_pct'] = (
    monthly_trends['late_delivery_count'] / 
    monthly_trends['total_deliveries'] * 100
).round(2)

# Convert period to string for CSV export
monthly_trends['year_month'] = pd.to_datetime(monthly_trends['year_month'].astype(str)).dt.strftime('%Y-%m-01')

print("Monthly trends shape:", monthly_trends.shape)
print("\nMonthly trends:")
print(monthly_trends.to_string())

# Merge orders with rfm to get segment info
orders_with_segment = orders.merge(
    rfm[['customer_unique_id', 'segment']], 
    on='customer_unique_id', 
    how='left'
)

# Revenue and orders by state
state_analysis = orders_with_segment.groupby('customer_state').agg(
    total_orders=('order_id', 'count'),
    total_revenue=('total_payment', 'sum'),
    avg_order_value=('total_payment', 'mean'),
    avg_review=('review_score', 'mean'),
    late_delivery_pct=('delivery_delay_days', lambda x: (x > 0).mean() * 100)
).round(2).reset_index()

# Sort by revenue
state_analysis = state_analysis.sort_values('total_revenue', ascending=False)

print("\nTop 10 states by revenue:")
print(state_analysis.head(10).to_string())

# Save monthly trends
monthly_trends.to_csv('outputs/monthly_trends.csv', index=False)

# Save state analysis
state_analysis.to_csv('outputs/state_analysis.csv', index=False)

# Save orders with segment for Power BI
orders_with_segment.to_csv('outputs/orders_with_segment.csv', index=False)

print("\nFiles saved to outputs/:")
print("- monthly_trends.csv")
print("- state_analysis.csv")
print("- orders_with_segment.csv")

