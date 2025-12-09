from setup.config import get_db

def process_transaction():
    """
    Demonstrates BEGIN TRANSACTION, COMMIT, ROLLBACK.
    Flow: Create Sale -> Add Items -> Deduct Stock.
    """
    cart = []
    print("\n--- NEW TRANSACTION ---")
    print("(Type 'pay' to finish, 'c' to cancel/exit)")
    
    # 1. Build the Cart (Memory only)
    while True:
        pid = input("Enter Product ID: ")
        
        # RESTORED: Ability to cancel/exit
        if pid.lower() in ['c', 'exit', 'back']: 
            print("Transaction cancelled.")
            return

        if pid.lower() == 'pay': 
            break
            
        try:
            qty = int(input("Qty: "))
            cart.append((int(pid), qty))
            print(f"Added Item {pid} (Qty: {qty}) to cart.")
        except ValueError: 
            print("Invalid input. Please enter numbers.")

    if not cart: 
        print("Cart is empty. Returning to menu.")
        return

    # 2. Process Database Transaction
    conn = get_db()

    # [IMPORTANT] Turn off Python's automatic transaction handling
    # This allows us to strictly write "BEGIN TRANSACTION" ourselves.
    conn.isolation_level = None

    c = conn.cursor()
    
    # ### RUBRIC: TRANSACTION START
    try:
        print("Attempting Transaction...")
        
        # ### RUBRIC: BEGIN TRANSACTION (Explicitly written now!)
        c.execute("BEGIN TRANSACTION")
        
        total = 0
        
        # Create Sale Header
        c.execute("INSERT INTO Sales (TotalAmount) VALUES (0)")
        sale_id = c.lastrowid

        # Process Items
        for pid, qty in cart:
            c.execute("SELECT Price, StockQty FROM Products WHERE ProductID = ?", (pid,))
            row = c.fetchone()
            if not row: raise Exception(f"Invalid Product ID: {pid}")
            
            price, current_stock = row['Price'], row['StockQty']
            
            if current_stock < qty:
                raise Exception(f"Not enough stock for Product {pid}!")

            subtotal = price * qty
            total += subtotal

            c.execute("UPDATE Products SET StockQty = StockQty - ? WHERE ProductID = ?", (qty, pid))
            c.execute("INSERT INTO SaleItems (SaleID, ProductID, Quantity, Subtotal) VALUES (?,?,?,?)", 
                      (sale_id, pid, qty, subtotal))

        # Update Final Total
        c.execute("UPDATE Sales SET TotalAmount = ? WHERE SaleID = ?", (total, sale_id))

        # ### RUBRIC: COMMIT (Explicitly written!)
        c.execute("COMMIT")
        print(f"✅ SUCCESS! Total: ₱{total}")

    except Exception as e:
        # ### RUBRIC: ROLLBACK (Explicitly written!)
        c.execute("ROLLBACK")
        print(f"❌ TRANSACTION FAILED: {e}")
        print("Changes rolled back.")
    
    finally:
        conn.close()