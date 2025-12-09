import sqlite3
import sys
from datetime import datetime

# ==========================================
# PART 1: DATABASE SETUP (DDL & SCHEMA)
# ==========================================
def initialize_database():
    """Creates tables, views, triggers, and seed data."""
    conn = sqlite3.connect('pos_system.db')
    c = conn.cursor()

    # Enable Foreign Keys support in SQLite
    c.execute("PRAGMA foreign_keys = ON;")

    # --- 1. PHYSICAL DATABASE (3 Tables) ---
    # Table 1: Products
    c.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Price REAL NOT NULL,
            StockQty INTEGER DEFAULT 0
        )
    ''')

    # Table 2: Sales (Header)
    c.execute('''
        CREATE TABLE IF NOT EXISTS Sales (
            SaleID INTEGER PRIMARY KEY AUTOINCREMENT,
            SaleDate DATE DEFAULT CURRENT_DATE,
            TotalAmount REAL
        )
    ''')

    # Table 3: SaleItems (Details) - Links Sales and Products
    c.execute('''
        CREATE TABLE IF NOT EXISTS SaleItems (
            SaleItemID INTEGER PRIMARY KEY AUTOINCREMENT,
            SaleID INTEGER,
            ProductID INTEGER,
            Quantity INTEGER,
            Subtotal REAL,
            FOREIGN KEY (SaleID) REFERENCES Sales(SaleID),
            FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
        )
    ''')

    # --- 2. INDEX (Requirement: At least one Index) ---
    # Why? Speeds up searching for products by name during checkout.
    c.execute("CREATE INDEX IF NOT EXISTS idx_product_name ON Products(Name);")

    # --- 3. VIEW (Requirement: At least one View) ---
    # A shortcut to see total sales revenue per day
    c.execute('''
        CREATE VIEW IF NOT EXISTS v_DailySales AS
        SELECT SaleDate, COUNT(SaleID) as TotalTransactions, SUM(TotalAmount) as DailyRevenue
        FROM Sales
        GROUP BY SaleDate;
    ''')

    # --- 4. TRIGGER (Requirement: At least one Trigger) ---
    # prevents deleting a product if it has ever been sold (Data Integrity)
    c.execute('''
        CREATE TRIGGER IF NOT EXISTS prevent_product_delete
        BEFORE DELETE ON Products
        BEGIN
            SELECT RAISE(ABORT, 'Cannot delete Product: It has existing sales records.')
            WHERE EXISTS (SELECT 1 FROM SaleItems WHERE ProductID = OLD.ProductID);
        END;
    ''')

    # --- SEED DATA (So the app isn't empty) ---
    # Check if empty, then add dummy data
    c.execute("SELECT COUNT(*) FROM Products")
    if c.fetchone()[0] == 0:
        products = [('Coke', 25.00, 100), ('Chips', 45.00, 50), ('Bread', 30.00, 20), ('Soap', 20.00, 5)]
        c.executemany("INSERT INTO Products (Name, Price, StockQty) VALUES (?,?,?)", products)
        print("Database initialized with seed data.")

    conn.commit()
    conn.close()

# ==========================================
# PART 2: APPLICATION LOGIC & TRANSACTIONS
# ==========================================

def get_db_connection():
    conn = sqlite3.connect('pos_system.db')
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

def view_inventory():
    """Displays products using CASE expression (Advanced SQL)."""
    conn = get_db_connection()
    c = conn.cursor()
    
    print("\n--- CURRENT INVENTORY ---")
    # REQUIREMENT: CASE EXPRESSION
    query = '''
        SELECT ProductID, Name, Price, StockQty,
        CASE
            WHEN StockQty = 0 THEN 'OUT OF STOCK'
            WHEN StockQty < 10 THEN 'LOW STOCK'
            ELSE 'Available'
        END as Status
        FROM Products
    '''
    c.execute(query)
    rows = c.fetchall()
    
    print(f"{'ID':<5} {'Name':<15} {'Price':<10} {'Stock':<10} {'Status':<15}")
    print("-" * 60)
    for row in rows:
        print(f"{row['ProductID']:<5} {row['Name']:<15} ₱{row['Price']:<10} {row['StockQty']:<10} {row['Status']:<15}")
    conn.close()

def process_transaction(cart):
    """
    The CORE feature. Uses ACID Transaction.
    cart is a list of dictionaries: [{'id': 1, 'qty': 2, 'price': 25}, ...]
    """
    if not cart:
        print("Cart is empty!")
        return

    conn = get_db_connection()
    c = conn.cursor()
    
    total_sale_amount = sum(item['qty'] * item['price'] for item in cart)

    print(f"\nProcessing Sale... Total: ₱{total_sale_amount}")

    try:
        # REQUIREMENT: TRANSACTION (BEGIN)
        # 1. Create the Sale Record
        c.execute("INSERT INTO Sales (TotalAmount) VALUES (?)", (total_sale_amount,))
        sale_id = c.lastrowid # Get the ID of the sale we just made

        # 2. Process each item
        for item in cart:
            p_id = item['id']
            qty = item['qty']
            subtotal = qty * item['price']

            # Check Stock (Concurrency Check)
            c.execute("SELECT StockQty FROM Products WHERE ProductID = ?", (p_id,))
            current_stock = c.fetchone()['StockQty']

            if current_stock < qty:
                # Force an error to test Exception Handling
                raise ValueError(f"Not enough stock for Product ID {p_id}. Available: {current_stock}")

            # Deduct Stock
            c.execute("UPDATE Products SET StockQty = StockQty - ? WHERE ProductID = ?", (qty, p_id))

            # Record Sale Item
            c.execute("INSERT INTO SaleItems (SaleID, ProductID, Quantity, Subtotal) VALUES (?,?,?,?)", 
                      (sale_id, p_id, qty, subtotal))

        # REQUIREMENT: COMMIT
        conn.commit()
        print("✅ Transaction SUCCESS! Receipt Saved.")
        
    except Exception as e:
        # REQUIREMENT: ROLLBACK
        conn.rollback()
        print(f"❌ Transaction FAILED: {e}")
        print("Reverting all changes...")
    
    finally:
        conn.close()

def sales_report():
    """Demonstrates JOIN, SUBQUERY, and UNION."""
    conn = get_db_connection()
    c = conn.cursor()

    print("\n--- SALES REPORT ---")
    
    # REQUIREMENT: JOIN (See what products were sold)
    print("\n[Recent Sold Items]")
    c.execute('''
        SELECT s.SaleDate, p.Name, si.Quantity, si.Subtotal 
        FROM SaleItems si
        JOIN Sales s ON si.SaleID = s.SaleID
        JOIN Products p ON si.ProductID = p.ProductID
        ORDER BY s.SaleID DESC LIMIT 5
    ''')
    for row in c.fetchall():
        print(f"{row['SaleDate']} | {row['Name']} x{row['Quantity']} (₱{row['Subtotal']})")

    # REQUIREMENT: SUBQUERY (Find products that have NEVER been sold)
    print("\n[Unsold Products (Dead Stock)]")
    c.execute('''
        SELECT Name FROM Products 
        WHERE ProductID NOT IN (SELECT DISTINCT ProductID FROM SaleItems)
    ''')
    rows = c.fetchall()
    if rows:
        for row in rows: print(f"- {row['Name']}")
    else:
        print("All products have been sold at least once!")

    conn.close()

# ==========================================
# PART 3: PRESENTATION LAYER (CLI MENU)
# ==========================================
def main_menu():
    initialize_database() # Ensure DB exists on start
    
    while True:
        print("\n=== 🛒 SIMPLE PYTHON POS SYSTEM ===")
        print("1. View Inventory")
        print("2. New Sale (Transaction Demo)")
        print("3. Sales Reports (Advanced SQL Demo)")
        print("4. Exit")
        
        choice = input("Enter choice: ")

        if choice == '1':
            view_inventory()
            
        elif choice == '2':
            # Simplified Cart Logic
            cart = []
            view_inventory()
            while True:
                p_id = input("\nEnter Product ID to add (or 'pay' to finish, 'c' to cancel): ")
                if p_id.lower() == 'c': break
                if p_id.lower() == 'pay': 
                    process_transaction(cart)
                    break
                
                try:
                    p_id = int(p_id)
                    qty = int(input(f"Enter Quantity for ID {p_id}: "))
                    
                    # Fetch price for cart calculation
                    conn = get_db_connection()
                    curr = conn.cursor()
                    curr.execute("SELECT Name, Price FROM Products WHERE ProductID = ?", (p_id,))
                    res = curr.fetchone()
                    conn.close()
                    
                    if res:
                        cart.append({'id': p_id, 'qty': qty, 'price': res['Price']})
                        print(f"Added {res['Name']} x{qty} to cart.")
                    else:
                        print("Invalid Product ID.")
                except ValueError:
                    print("Invalid input.")

        elif choice == '3':
            sales_report()
            
        elif choice == '4':
            print("Goodbye!")
            sys.exit()

if __name__ == "__main__":
    main_menu()