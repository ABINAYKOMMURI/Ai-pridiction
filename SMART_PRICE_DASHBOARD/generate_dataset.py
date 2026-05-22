"""
Smart Multi-Category Price Trend Analysis - Dataset Generator
Generates 10,050 rows of realistic price data across 15 categories.
Uses Growth Rate Formula: (Current - Previous) / Previous
Uses Future Price Formula: Current * (1 + Growth_Rate)^3
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

np.random.seed(42)
random.seed(42)

# ─── Category Definitions ───────────────────────────────────────────────
categories = {
    'Mobiles': {
        'products': ['iPhone 15 Pro', 'Samsung Galaxy S24', 'OnePlus 12', 'Google Pixel 8', 'Xiaomi 14', 'Vivo X100', 'Realme GT 5 Pro', 'Nothing Phone 2'],
        'brands':   ['Apple', 'Samsung', 'OnePlus', 'Google', 'Xiaomi', 'Vivo', 'Realme', 'Nothing'],
        'price_range': (12000, 149999)
    },
    'Laptops': {
        'products': ['MacBook Air M3', 'Dell XPS 15', 'HP Pavilion 15', 'Lenovo ThinkPad X1', 'ASUS ROG Strix', 'Acer Nitro 5', 'MSI Creator 16', 'HP Spectre x360'],
        'brands':   ['Apple', 'Dell', 'HP', 'Lenovo', 'ASUS', 'Acer', 'MSI', 'HP'],
        'price_range': (30000, 249999)
    },
    'Grocery': {
        'products': ['Basmati Rice 5kg', 'Wheat Flour 10kg', 'Sunflower Oil 5L', 'Sugar 5kg', 'Toor Dal 2kg', 'Iodized Salt 1kg', 'Premium Tea 500g', 'Instant Coffee 250g'],
        'brands':   ['India Gate', 'Aashirvaad', 'Fortune', 'Trust', 'Tata', 'Catch', 'Tata Tea', 'Nescafe'],
        'price_range': (40, 1500)
    },
    'Fuel': {
        'products': ['Petrol 1L', 'Diesel 1L', 'CNG 1kg', 'LPG Cylinder 14.2kg', 'Aviation Fuel 1L', 'Kerosene 1L'],
        'brands':   ['Indian Oil', 'Bharat Petroleum', 'HP Gas', 'Indane', 'IOCL', 'BPCL'],
        'price_range': (28, 1200)
    },
    'Gold': {
        'products': ['Gold 24K 10g', 'Gold 22K 10g', 'Gold Coin 5g', 'Gold Chain 10g', 'Gold Ring 5g', 'Gold Bangle 20g'],
        'brands':   ['Tanishq', 'Malabar Gold', 'Kalyan Jewellers', 'PC Jeweller', 'Senco Gold', 'Joyalukkas'],
        'price_range': (28000, 140000)
    },
    'Silver': {
        'products': ['Silver Bar 1kg', 'Silver Coin 100g', 'Silver Chain 50g', 'Silver Ring 20g', 'Silver Anklet 30g', 'Silver Bangle 40g'],
        'brands':   ['Tanishq', 'Malabar Gold', 'MMTC-PAMP', 'Kalyan', 'Senco', 'Joyalukkas'],
        'price_range': (1500, 95000)
    },
    'Electronics': {
        'products': ['Smart TV 55"', 'Bluetooth Speaker', 'Wireless Earbuds', 'Smart Watch', 'Tablet 10"', 'DSLR Camera', 'Projector HD', 'Gaming Console'],
        'brands':   ['Samsung', 'Sony', 'JBL', 'Apple', 'Xiaomi', 'Canon', 'Epson', 'PlayStation'],
        'price_range': (2000, 150000)
    },
    'Home Appliances': {
        'products': ['Washing Machine 7kg', 'Refrigerator 300L', 'Air Conditioner 1.5T', 'Microwave Oven 25L', 'Water Purifier RO', 'Vacuum Cleaner', 'Dishwasher', 'Air Purifier'],
        'brands':   ['LG', 'Samsung', 'Whirlpool', 'IFB', 'Kent', 'Dyson', 'Bosch', 'Philips'],
        'price_range': (5000, 80000)
    },
    'Clothing': {
        'products': ['Formal Shirt', 'Denim Jeans', 'Silk Saree', 'Kurta Set', 'Winter Jacket', 'Sport Shoes', 'Casual T-Shirt', 'Ethnic Dress'],
        'brands':   ['Raymond', 'Levis', 'Fabindia', 'Manyavar', 'Woodland', 'Nike', 'H&M', 'Biba'],
        'price_range': (499, 15000)
    },
    'Fruits and Vegetables': {
        'products': ['Tomato 1kg', 'Onion 1kg', 'Potato 1kg', 'Apple 1kg', 'Banana 1dz', 'Mango 1kg', 'Spinach 500g', 'Carrot 1kg'],
        'brands':   ['Local Market', 'BigBasket', 'FreshToHome', 'Nature Basket', 'Reliance Fresh', 'DMart', 'More Supermarket', 'Star Bazaar'],
        'price_range': (20, 350)
    },
    'Medicine': {
        'products': ['Paracetamol 500mg', 'Cough Syrup 100ml', 'Vitamin D3 60tabs', 'Amoxicillin 500mg', 'Pain Relief Gel 30g', 'Antacid Syrup 200ml', 'Multivitamin 30tabs', 'Bandage Roll 5m'],
        'brands':   ['Cipla', 'Sun Pharma', 'Dr Reddys', 'Lupin', 'Himalaya', 'Dabur', 'Abbott', 'Johnson & Johnson'],
        'price_range': (18, 800)
    },
    'Computer Components': {
        'products': ['RAM DDR5 16GB', 'SSD NVMe 512GB', 'Graphics Card RTX 4060', 'Processor i7 14th Gen', 'Motherboard Z790', 'Power Supply 750W', 'Cabinet Mid Tower', 'Monitor 27" 165Hz'],
        'brands':   ['Corsair', 'Samsung', 'NVIDIA', 'Intel', 'ASUS', 'Cooler Master', 'NZXT', 'LG'],
        'price_range': (3000, 80000)
    },
    'Travel Tickets': {
        'products': ['Flight Domestic', 'Train AC 2-Tier', 'Bus Volvo AC', 'Metro Monthly Pass', 'Flight International', 'Train Sleeper', 'Bus Non-AC', 'Ferry Ticket'],
        'brands':   ['IndiGo', 'IRCTC', 'RedBus', 'DMRC', 'Air India', 'IRCTC', 'KSRTC', 'Govt Ferry'],
        'price_range': (80, 45000)
    },
    'Vehicles': {
        'products': ['Sedan Car', 'Compact SUV', 'Motorcycle 150cc', 'Electric Scooter', 'Mountain Bicycle', 'Hatchback Car', 'Sports Bike 300cc', 'Electric Car'],
        'brands':   ['Maruti Suzuki', 'Hyundai', 'Royal Enfield', 'Ather', 'Hero Cycles', 'Tata Motors', 'Kawasaki', 'MG Motors'],
        'price_range': (8000, 2500000)
    },
    'Books': {
        'products': ['Engineering Textbook', 'Fiction Novel', 'Reference Manual', 'Competitive Exam Guide', 'Notebook Set 5pcs', 'Programming Guide', 'Science Encyclopedia', 'Art & Design Book'],
        'brands':   ['Pearson', 'Penguin', 'McGraw Hill', 'Arihant', 'Classmate', 'OReilly', 'DK Publishing', 'Phaidon'],
        'price_range': (99, 3500)
    },
}

locations = [
    'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata',
    'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow'
]

# Date range
start_date = datetime(2023, 1, 1)
end_date   = datetime(2025, 12, 31)
days_range = (end_date - start_date).days

ROWS_PER_CATEGORY = 670  # 670 × 15 = 10,050 rows

data = []

for category, info in categories.items():
    products   = info['products']
    brands     = info['brands']
    min_p, max_p = info['price_range']

    for _ in range(ROWS_PER_CATEGORY):
        idx = random.randint(0, len(products) - 1)
        product = products[idx]
        brand   = brands[idx]

        # Previous price (base)
        previous_price = round(random.uniform(min_p, max_p), 2)

        # Realistic growth factor: mean ~8%, std 15%
        growth_factor = np.random.normal(0.08, 0.15)

        # Current price
        current_price = round(previous_price * (1 + growth_factor), 2)
        current_price = max(current_price, min_p * 0.3)

        # Growth Rate = (Current - Previous) / Previous
        growth_rate = round((current_price - previous_price) / previous_price, 4)

        # Future Price = Current × (1 + Growth_Rate)^3
        future_price = round(current_price * (1 + growth_rate) ** 3, 2)
        future_price = max(future_price, 0)

        # Random date in range
        rand_date = start_date + timedelta(days=random.randint(0, days_range))

        # Random location
        location = random.choice(locations)

        # Discount 0-30%
        discount = round(random.uniform(0, 30), 1)

        # Quantity 1-500
        quantity = random.randint(1, 500)

        data.append({
            'Product_Name':   product,
            'Category':       category,
            'Brand':          brand,
            'Previous_Price': previous_price,
            'Current_Price':  current_price,
            'Growth_Rate':    growth_rate,
            'Future_Price':   future_price,
            'Date':           rand_date.strftime('%Y-%m-%d'),
            'Location':       location,
            'Discount':       discount,
            'Quantity':        quantity,
        })

df = pd.DataFrame(data)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

os.makedirs('dataset', exist_ok=True)
df.to_csv('dataset/price_data.csv', index=False)

print(f"✅ Dataset generated successfully!")
print(f"   Rows       : {len(df)}")
print(f"   Categories : {df['Category'].nunique()}")
print(f"   Products   : {df['Product_Name'].nunique()}")
print(f"   Brands     : {df['Brand'].nunique()}")
print(f"   Locations  : {df['Location'].nunique()}")
print(f"\nSample rows:")
print(df.head(5).to_string(index=False))
