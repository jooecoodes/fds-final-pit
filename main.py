import sqlite3
import sys
import random

from ddl.initialize_db import initialize_database

from dml.view_products import view_products
from dml.update_product import update_product_price
from dml.delete_product import delete_product

from core.process_transaction import process_transaction
from core.analyze_sales import analyze_sales


# ==========================================
# MAIN MENU
# ==========================================
def main():
    initialize_database()
    while True:
        print("\n=== 🛒 SUPERMARKET SYSTEM (SQL DEMO) ===")
        print("1. View Inventory (SELECT/CASE)")
        print("2. Update Price (UPDATE)")
        print("3. Delete Product (DELETE/TRIGGER)")
        print("4. New Sale (TRANSACTION/ACID)")
        print("5. Analytics Report (JOIN/UNION/GROUP BY)")
        print("6. Exit")
        
        ch = input("Choice: ")
        if ch == '1': view_products()
        elif ch == '2': update_product_price()
        elif ch == '3': delete_product()
        elif ch == '4': process_transaction()
        elif ch == '5': analyze_sales()
        elif ch == '6': break

if __name__ == "__main__":
    main()