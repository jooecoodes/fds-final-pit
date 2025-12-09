import sqlite3

from setup.config import get_db

def delete_product():
    """Shows DELETE (and triggers the TRIGGER if item was sold)."""
    p_id = input("Enter Product ID to delete: ")
    
    conn = get_db()
    try:
        # ### RUBRIC: DELETE
        conn.execute("DELETE FROM Products WHERE ProductID = ?", (p_id,))
        conn.commit()
        print("Product deleted.")
    except sqlite3.IntegrityError as e:
        print(f"❌ BLOCKED BY TRIGGER: {e}") 
    except Exception as e:
        print(e)
    finally:
        conn.close()