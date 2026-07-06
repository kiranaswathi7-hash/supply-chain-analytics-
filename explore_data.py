"""
Data Exploration Script for Manufacturing Supply Chain Analytics
Loads all CSV files and prints their structure to understand schema and relationships
"""

import pandas as pd
import os
from pathlib import Path

# Define the expected CSV files
csv_files = [
    'items_master.csv',
    'suppliers.csv',
    'customers.csv',
    'inventory.csv',
    'purchase_orders.csv',
    'goods_receipts.csv',
    'sales_orders.csv',
    'production_orders.csv',
    'production_order_components.csv',
    'bom_header.csv',
    'bom_lines.csv'
]

# Set the data directory - adjust this path to where your CSVs are located
data_dir = Path(__file__).parent / "csv files"  # CSVs are in the 'csv files' subdirectory

print("=" * 80)
print("DATA EXPLORATION - MANUFACTURING SUPPLY CHAIN ANALYTICS")
print("=" * 80)
print()

# Dictionary to store all dataframes
dataframes = {}

for csv_file in csv_files:
    file_path = data_dir / csv_file
    
    print(f"\n{'=' * 80}")
    print(f"FILE: {csv_file}")
    print(f"{'=' * 80}")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        continue
    
    try:
        df = pd.read_csv(file_path)
        dataframes[csv_file] = df
        
        print(f"\n✅ Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        
        print(f"\n📋 Column Names:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i:2d}. {col}")
        
        print(f"\n📊 Data Types:")
        print(df.dtypes.to_string())
        
        print(f"\n🔍 First 5 Rows:")
        print(df.head().to_string())
        
        print(f"\n📈 Basic Statistics (numeric columns):")
        print(df.describe().to_string())
        
        print(f"\n🔎 Null Values:")
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            print(null_counts[null_counts > 0].to_string())
        else:
            print("   No null values found")
            
    except Exception as e:
        print(f"❌ Error reading file: {e}")

print("\n" + "=" * 80)
print("SUMMARY OF ALL LOADED FILES")
print("=" * 80)
print(f"\nTotal files loaded: {len(dataframes)}/{len(csv_files)}")
print(f"Loaded files: {list(dataframes.keys())}")

print("\n" + "=" * 80)
print("POTENTIAL JOIN KEYS ANALYSIS")
print("=" * 80)

# Analyze potential relationships based on common column names
print("\n🔗 Common column names across files (potential join keys):")
all_columns = {}
for csv_file, df in dataframes.items():
    for col in df.columns:
        if col not in all_columns:
            all_columns[col] = []
        all_columns[col].append(csv_file)

for col, files in sorted(all_columns.items()):
    if len(files) > 1:
        print(f"\n   '{col}' appears in: {', '.join(files)}")

print("\n" + "=" * 80)
print("END OF DATA EXPLORATION")
print("=" * 80)
