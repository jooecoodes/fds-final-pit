from config import get_db

def view_products():
    """Shows SELECT, ORDER BY, and CASE."""
    conn = get_db()
    c = conn.cursor()
    print("\n--- INVENTORY LIST ---")
    
    # ### RUBRIC: SELECT, ORDER BY, CASE EXPRESSION
    c.execute('''
        SELECT ProductID, Name, Category, Price, StockQty,
        CASE 
            WHEN StockQty < 20 THEN 'CRITICAL'
            WHEN StockQty < 50 THEN 'Low'
            ELSE 'Normal'
        END as StockStatus
        FROM Products
        ORDER BY Category, Name ASC
    ''')
    
    print(f"{'ID':<4} {'Name':<15} {'Category':<10} {'Price':<8} {'Stock':<6} {'Status':<10}")
    print("-" * 60)
    for r in c.fetchall():
        print(f"{r['ProductID']:<4} {r['Name']:<15} {r['Category']:<10} {r['Price']:<8} {r['StockQty']:<6} {r['StockStatus']:<10}")
    conn.close()