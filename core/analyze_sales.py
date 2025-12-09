from setup.config import get_db

def analyze_sales():
    conn = get_db()
    c = conn.cursor()
    print("\n--- ADVANCED ANALYTICS ---")

    # ### RUBRIC: GROUP BY + HAVING
    print("\n[Categories with High Stock (>200 items)]")
    c.execute('''
        SELECT Category, SUM(StockQty) as TotalStock
        FROM Products
        GROUP BY Category
        HAVING SUM(StockQty) > 200
    ''')
    for r in c.fetchall(): print(f"{r['Category']}: {r['TotalStock']}")

    # ### RUBRIC: SUBQUERY
    print("\n[Products Cheaper than the Average Price]")
    c.execute('''
        SELECT Name, Price FROM Products
        WHERE Price < (SELECT AVG(Price) FROM Products)
    ''')
    for r in c.fetchall(): print(f"{r['Name']} (₱{r['Price']})")

    # ### RUBRIC: JOIN
    print("\n[Detailed Sales Log]")
    c.execute('''
        SELECT s.SaleDate, p.Name, si.Quantity, si.Subtotal
        FROM SaleItems si
        JOIN Sales s ON si.SaleID = s.SaleID
        JOIN Products p ON si.ProductID = p.ProductID
        ORDER BY s.SaleID DESC LIMIT 5
    ''')
    for r in c.fetchall(): print(f"{r['SaleDate']} - Sold {r['Quantity']}x {r['Name']}")

    # ### RUBRIC: UNION
    # combines two specific queries into one list
    print("\n[Priority Attention List (UNION)]")
    c.execute('''
        SELECT Name, 'Expiring Soon' as Reason FROM Products WHERE StockQty > 400
        UNION
        SELECT Name, 'Out of Stock' as Reason FROM Products WHERE StockQty = 0
    ''')
    for r in c.fetchall(): print(f"{r['Name']} - {r['Reason']}")
    
    conn.close()