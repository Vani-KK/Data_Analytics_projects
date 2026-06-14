import pandas as pd
import numpy as np
import os

# Define path to data folder
DATA_PATH = "data/"

# Load the 5 files we need
orders = pd.read_csv(os.path.join(DATA_PATH, "olist_orders_dataset.csv"),low_memory=False)
order_items = pd.read_csv(os.path.join(DATA_PATH, "olist_order_items_dataset.csv"))
customers = pd.read_csv(os.path.join(DATA_PATH, "olist_customers_dataset.csv"))
payments = pd.read_csv(os.path.join(DATA_PATH, "olist_order_payments_dataset.csv"))
reviews = pd.read_csv(
    os.path.join(DATA_PATH, "olist_order_reviews_dataset.csv"),
    usecols=['order_id', 'review_score']  # only load what we need
)

# See shape (rows, columns) of each file
print("Orders:", orders.shape)
print("Order Items:", order_items.shape)
print("Customers:", customers.shape)
print("Payments:", payments.shape)
print("Reviews:", reviews.shape)


print("\n--- ORDERS ---")
print(orders.head())
print(orders.columns.tolist())

print("\n--- ORDER ITEMS ---")
print(order_items.head())
print(order_items.columns.tolist())

print("\n--- CUSTOMERS ---")
print(customers.head())
print(customers.columns.tolist())

print("\n--- PAYMENTS ---")
print(payments.head())
print(payments.columns.tolist())

print("\n--- REVIEWS ---")
print(reviews.head())
print(reviews.columns.tolist())

# Check missing values in each file
print("\n--- MISSING VALUES ---")
print("Orders nulls:\n", orders.isnull().sum())
print("\nOrder Items nulls:\n", order_items.isnull().sum())
print("\nCustomers nulls:\n", customers.isnull().sum())
print("\nPayments nulls:\n", payments.isnull().sum())
print("\nReviews nulls:\n", reviews.isnull().sum())

# Check what order statuses exist
print("\nOrder status counts:")
print(orders['order_status'].value_counts())


# Keep only delivered orders
orders_delivered = orders[orders['order_status'] == 'delivered'].copy()
print(f"\nDelivered orders: {len(orders_delivered)}")

# Convert date columns from string to datetime
# Right now Python sees these as plain text, not actual dates
orders_delivered['order_purchase_timestamp'] = pd.to_datetime(orders_delivered['order_purchase_timestamp'])
orders_delivered['order_delivered_customer_date'] = pd.to_datetime(orders_delivered['order_delivered_customer_date'])
orders_delivered['order_estimated_delivery_date'] = pd.to_datetime(orders_delivered['order_estimated_delivery_date'])

# Calculate delivery delay in days (your idea from earlier!)
orders_delivered['delivery_delay_days'] = (
    orders_delivered['order_delivered_customer_date'] - 
    orders_delivered['order_estimated_delivery_date']
).dt.days

print("\nDelivery delay sample:")
print(orders_delivered['delivery_delay_days'].describe())

# Drop the 8 rows where delivered date is still null
orders_delivered = orders_delivered.dropna(subset=['order_delivered_customer_date'])
print(f"After dropping null delivery dates: {len(orders_delivered)}")

# Quick check on delay distribution
print(f"\nOrders delivered LATE (delay > 0): {(orders_delivered['delivery_delay_days'] > 0).sum()}")
print(f"Orders delivered ON TIME or EARLY (delay <= 0): {(orders_delivered['delivery_delay_days'] <= 0).sum()}")
print(f"Average delay for LATE orders: {orders_delivered[orders_delivered['delivery_delay_days'] > 0]['delivery_delay_days'].mean():.1f} days")

# Step 1 — merge orders with customers to get customer_unique_id
df = orders_delivered.merge(customers, on='customer_id', how='left')
print(f"After merging customers: {df.shape}")

# Step 2 — merge with order_items to get price
df = df.merge(order_items, on='order_id', how='left')
print(f"After merging order items: {df.shape}")

# Step 3 — merge with payments to get payment_value
df = df.merge(payments, on='order_id', how='left')
print(f"After merging payments: {df.shape}")


# Step 4 — merge with reviews to get review score
df = df.merge(reviews[['order_id', 'review_score']], on='order_id', how='left')
print(f"After merging reviews: {df.shape}")

print("\nFinal columns:")
print(df.columns.tolist())


# Aggregate to get one clean row per order
order_agg = df.groupby(['order_id', 'customer_unique_id', 'customer_state',
                         'order_purchase_timestamp', 'delivery_delay_days']).agg(
    total_items=('order_item_id', 'count'),       # how many items in this order
    total_price=('price', 'sum'),                  # sum of all item prices
    total_payment=('payment_value', 'sum'),        # actual amount paid
    review_score=('review_score', 'mean')          # avg score if multiple reviews
).reset_index()


print(f"Aggregated order shape: {order_agg.shape}")
print(f"\nSample:")
print(order_agg.head())


print(order_agg.isnull().sum())
print(f"\nDate range of orders:")
print(f"Earliest order: {order_agg['order_purchase_timestamp'].min()}")
print(f"Latest order: {order_agg['order_purchase_timestamp'].max()}")
print(f"\nAverage order value: R${order_agg['total_payment'].mean():.2f}")
print(f"Average items per order: {order_agg['total_items'].mean():.2f}")


# Snapshot date = day after last order in dataset
snapshot_date = order_agg['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
print(f"Snapshot date: {snapshot_date}")

# Build RFM — one row per CUSTOMER (not per order)
rfm = order_agg.groupby('customer_unique_id').agg(
    recency=('order_purchase_timestamp', lambda x: (snapshot_date - x.max()).days),
    frequency=('order_id', 'count'),
    monetary=('total_payment', 'sum'),
    avg_review=('review_score', 'mean'),
    late_deliveries=('delivery_delay_days', lambda x: (x > 0).sum())
).reset_index()

print(f"\nRFM shape: {rfm.shape}")
print(f"\nRFM sample:")
print(rfm.head())
print(f"\nRFM stats:")
print(rfm[['recency', 'frequency', 'monetary']].describe())


# Score each RFM dimension 1-4
# Recency — lower days = better = higher score (so we flip it)
rfm['r_score'] = pd.qcut(rfm['recency'], q=4, labels=[4, 3, 2, 1])

# Frequency and Monetary — higher = better = higher score
rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), q=4, labels=[1, 2, 3, 4])
rfm['m_score'] = pd.qcut(rfm['monetary'], q=4, labels=[1, 2, 3, 4])

# Combine into overall RFM score
rfm['rfm_score'] = rfm['r_score'].astype(int) + rfm['f_score'].astype(int) + rfm['m_score'].astype(int)

print("RFM score distribution:")
print(rfm['rfm_score'].value_counts().sort_index())


def assign_segment(row):
    r = int(row['r_score'])
    f = int(row['f_score'])
    m = int(row['m_score'])
    score = row['rfm_score']
    
    if r >= 3 and f >= 3 and m >= 3:
        return 'Champions'          # bought recently, often, spent a lot
    elif r >= 3 and f >= 2:
        return 'Loyal Customers'    # buy regularly, recent
    elif r >= 3 and f <= 1:
        return 'Promising'          # bought recently but not often yet
    elif r == 2 and f >= 2:
        return 'At Risk'            # used to buy often but fading
    elif r == 2 and f <= 1:
        return 'Need Attention'     # middling recency, low frequency
    elif r == 1 and f >= 2:
        return 'Cant Lose Them'     # bought often historically but gone quiet
    else:
        return 'Lost'               # low recency, low frequency

rfm['segment'] = rfm.apply(assign_segment, axis=1)

print("Customer segments:")
print(rfm['segment'].value_counts())
print(f"\nTotal customers: {len(rfm)}")


# Revenue by segment
revenue_by_segment = rfm.groupby('segment').agg(
    total_customers=('customer_unique_id', 'count'),
    total_revenue=('monetary', 'sum'),
    avg_revenue=('monetary', 'mean'),
    avg_recency=('recency', 'mean'),
    avg_review=('avg_review', 'mean'),
    late_delivery_pct=('late_deliveries', lambda x: (x > 0).mean() * 100)
).round(2).reset_index()

# Sort by total revenue
revenue_by_segment = revenue_by_segment.sort_values('total_revenue', ascending=False)

print("\nRevenue by segment:")
print(revenue_by_segment.to_string())

# Calculate revenue at risk
at_risk_revenue = rfm[rfm['segment'].isin(['At Risk', 'Cant Lose Them', 'Lost'])]['monetary'].sum()
total_revenue = rfm['monetary'].sum()
pct_at_risk = (at_risk_revenue / total_revenue) * 100

print(f"\nTotal revenue: R${total_revenue:,.2f}")
print(f"Revenue at risk: R${at_risk_revenue:,.2f}")
print(f"Percentage at risk: {pct_at_risk:.1f}%")


# Create outputs folder if it doesn't exist
os.makedirs('outputs', exist_ok=True)

# Save RFM with segments
rfm.to_csv('outputs/rfm_segments.csv', index=False)

# Save revenue by segment summary
revenue_by_segment.to_csv('outputs/revenue_by_segment.csv', index=False)

# Save the clean order level data
order_agg.to_csv('outputs/orders_clean.csv', index=False)

print("\nFiles saved to outputs/ folder:")
print("- rfm_segments.csv")
print("- revenue_by_segment.csv")
print("- orders_clean.csv")
