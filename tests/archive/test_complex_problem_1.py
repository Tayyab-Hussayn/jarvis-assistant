#!/usr/bin/env python3
"""
Complex Problem Testing - 4 Individual Complex Problems
"""

import asyncio
import sys
sys.path.append('/home/krawin/exp.code/jarvis')

from core.execution.docker_executor import DockerCodeExecutor, ExecutionConfig

async def problem_1_data_analysis():
    """Problem 1: Complex Data Analysis and Statistics"""
    print("📊 PROBLEM 1: Data Analysis & Statistics")
    print("=" * 50)
    print("Task: Analyze sales data, calculate trends, and generate insights")
    
    code = """
# Complex Data Analysis Problem
import json
from collections import defaultdict
from datetime import datetime, timedelta

# Sample sales data
sales_data = [
    {"date": "2024-01-15", "product": "Laptop", "category": "Electronics", "price": 1200, "quantity": 2},
    {"date": "2024-01-16", "product": "Phone", "category": "Electronics", "price": 800, "quantity": 3},
    {"date": "2024-01-17", "product": "Book", "category": "Education", "price": 25, "quantity": 10},
    {"date": "2024-01-18", "product": "Laptop", "category": "Electronics", "price": 1200, "quantity": 1},
    {"date": "2024-01-19", "product": "Tablet", "category": "Electronics", "price": 500, "quantity": 4},
    {"date": "2024-01-20", "product": "Book", "category": "Education", "price": 30, "quantity": 8},
    {"date": "2024-01-21", "product": "Phone", "category": "Electronics", "price": 850, "quantity": 2},
    {"date": "2024-01-22", "product": "Headphones", "category": "Electronics", "price": 150, "quantity": 6}
]

print("=== SALES DATA ANALYSIS ===")
print(f"Total records: {len(sales_data)}")

# Calculate total revenue
total_revenue = sum(item['price'] * item['quantity'] for item in sales_data)
print(f"Total Revenue: ${total_revenue:,}")

# Revenue by category
category_revenue = defaultdict(int)
for item in sales_data:
    category_revenue[item['category']] += item['price'] * item['quantity']

print("\\nRevenue by Category:")
for category, revenue in sorted(category_revenue.items()):
    percentage = (revenue / total_revenue) * 100
    print(f"  {category}: ${revenue:,} ({percentage:.1f}%)")

# Top selling products
product_sales = defaultdict(lambda: {'quantity': 0, 'revenue': 0})
for item in sales_data:
    product_sales[item['product']]['quantity'] += item['quantity']
    product_sales[item['product']]['revenue'] += item['price'] * item['quantity']

print("\\nTop Products by Revenue:")
sorted_products = sorted(product_sales.items(), key=lambda x: x[1]['revenue'], reverse=True)
for i, (product, data) in enumerate(sorted_products[:3], 1):
    print(f"  {i}. {product}: ${data['revenue']:,} ({data['quantity']} units)")

# Daily trends
daily_sales = defaultdict(int)
for item in sales_data:
    daily_sales[item['date']] += item['price'] * item['quantity']

print("\\nDaily Sales Trend:")
for date in sorted(daily_sales.keys()):
    print(f"  {date}: ${daily_sales[date]:,}")

# Calculate growth rate
dates = sorted(daily_sales.keys())
if len(dates) >= 2:
    first_day = daily_sales[dates[0]]
    last_day = daily_sales[dates[-1]]
    growth_rate = ((last_day - first_day) / first_day) * 100
    print(f"\\nGrowth Rate (First to Last Day): {growth_rate:.1f}%")

print("\\n=== ANALYSIS COMPLETE ===")
"""
    
    executor = DockerCodeExecutor()
    executor.docker_available = False
    
    config = ExecutionConfig(language="python", timeout=15)
    result = await executor.execute_code(code, config)
    
    print(f"✅ Success: {result.success}")
    print(f"Output:\n{result.output}")
    print(f"Execution time: {result.execution_time:.3f}s")
    
    return result.success
