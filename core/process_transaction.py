from config import get_db

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
    c = conn.cursor()
    
    # ### RUBRIC: TRANSACTION START
    try:
        print("Attempting Transaction...")
        total = 0
        
        # Create Sale Header
        c.execute("INSERT INTO Sales (TotalAmount) VALUES (0)")
        sale_id = c.lastrowid

        # Process Items
        for pid, qty in cart:
            # Check Price & Stock
            c.execute("SELECT Price, StockQty FROM Products WHERE ProductID = ?", (pid,))
            row = c.fetchone()
            if not row: raise Exception(f"Invalid Product ID: {pid}")
            
            price, current_stock = row['Price'], row['StockQty']
            
            if current_stock < qty:
                # This triggers the ROLLBACK
                raise Exception(f"Not enough stock for Product {pid}! (Have: {current_stock}, Need: {qty})")

            subtotal = price * qty
            total += subtotal

            # Deduct Stock
            c.execute("UPDATE Products SET StockQty = StockQty - ? WHERE ProductID = ?", (qty, pid))
            
            # Add Line Item
            c.execute("INSERT INTO SaleItems (SaleID, ProductID, Quantity, Subtotal) VALUES (?,?,?,?)", 
                      (sale_id, pid, qty, subtotal))

        # Update Final Total
        c.execute("UPDATE Sales SET TotalAmount = ? WHERE SaleID = ?", (total, sale_id))

        # ### RUBRIC: COMMIT (Save changes permanently)
        conn.commit()
        print(f"✅ SUCCESS! Total: ₱{total}")

    except Exception as e:
        # ### RUBRIC: ROLLBACK (Undo everything if error)
        conn.rollback()
        print(f"❌ TRANSACTION FAILED: {e}")
        print("Changes rolled back.")
    
    finally:
        conn.close()