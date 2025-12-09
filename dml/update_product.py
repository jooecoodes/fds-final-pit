from setup.config import get_db

def update_product_price():
    """Shows UPDATE and WHERE."""
    p_id = input("Enter Product ID to update price: ")
    new_price = input("Enter new price: ")
    
    conn = get_db()
    try:
        # ### RUBRIC: UPDATE, WHERE
        conn.execute("UPDATE Products SET Price = ? WHERE ProductID = ?", (new_price, p_id))
        conn.commit()
        print("Price updated successfully.")
    except Exception as e:
        print(e)
    finally:
        conn.close()