# E-commerce Customer Churn & Revenue Risk Analysis

## Overview
Ever wondered how many customers an e-commerce company is quietly losing — 
and how much money walks out the door with them?

This project analyzes 99,000+ real orders from Olist, a Brazilian e-commerce 
marketplace, to identify which customers are about to stop buying and how much 
revenue is at risk. Using RFM (Recency, Frequency, Monetary) analysis, I 
segmented 93,350 customers into 7 behavioral groups and built a dashboard to 
tell the story visually.

## Key Findings
- **42.6% of total revenue (R$8.46M) is at risk** — sitting in churning or 
  already-lost customer segments
- **96.7% of customers made only one purchase** — Olist has a severe repeat 
  purchase problem
- **6.8% of orders were delivered late** — averaging 10.6 days past the 
  expected date
- **States RJ and BA have 12%+ late delivery rates** — directly correlating 
  with the lowest review scores in the dataset (3.93–3.97)
- **Nov 2017 and Mar 2018 were crisis months** — late delivery spiked to 12% 
  and 19% respectively, causing review scores to drop to their lowest points

## What is RFM Analysis?
RFM is a customer segmentation technique used by companies like Amazon and 
Flipkart to understand buying behavior.

- **R**ecency — how recently did the customer buy?
- **F**requency — how many times have they bought?
- **M**onetary — how much have they spent in total?

Each customer gets scored on all three dimensions. Combining the scores 
segments customers into groups — from Champions (recent, frequent, high 
spenders) to Lost (haven't bought in over a year).

## Customer Segments Found

| Segment | Customers | Revenue | Avg Spend |
|---|---|---|---|
| Champions | 12,258 | R$4.6M | R$378 |
| At Risk | 17,436 | R$3.7M | R$211 |
| Can't Lose Them | 17,408 | R$3.6M | R$206 |
| Loyal Customers | 22,910 | R$3.1M | R$134 |
| Promising | 11,673 | R$2.4M | R$202 |
| Need Attention | 5,763 | R$1.3M | R$234 |
| Lost | 5,902 | R$1.2M | R$204 |

## Dashboard
Built in Looker Studio — shows executive summary, monthly trends breakdown across Brazilian states.

[View Live Dashboard] (https://datastudio.google.com/reporting/fb54acf2-7896-40e3-b54c-9f586ad515a2)

## Tools Used
- **Python** — pandas, numpy (data cleaning, RFM calculation, feature engineering)
- **Looker Studio** — interactive dashboard
- **Git & GitHub** — version control

## Dataset
Real transaction data from Olist, Brazil's largest e-commerce marketplace.

Download from Kaggle: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Place all CSV files inside the `data/` folder before running scripts.

## How to Run

1. Clone this repository
2. Create a virtual environment and activate it:
```bash
   python -m venv venv
   venv\Scripts\activate
```
3. Install dependencies:
```bash
   pip install -r requirements.txt
```
4. Download dataset from Kaggle and place CSVs in `data/` folder
5. Run scripts in order:
```bash
   python scripts/01_load_clean.py
   python scripts/02_monthly_trends.py
```
6. Open the dashboard link above to view results
