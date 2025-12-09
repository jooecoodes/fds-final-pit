import sqlite3

def initialize_database():
    conn = sqlite3.connect('pos_system.db')
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = ON;")

    # ### RUBRIC: CREATE TABLE (Physical Database)
    c.executescript('''
        CREATE TABLE IF NOT EXISTS Products (
            ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            Category TEXT,
            Price REAL NOT NULL,
            StockQty INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS Sales (
            SaleID INTEGER PRIMARY KEY AUTOINCREMENT,
            SaleDate DATE DEFAULT CURRENT_DATE,
            TotalAmount REAL
        );

        CREATE TABLE IF NOT EXISTS SaleItems (
            SaleItemID INTEGER PRIMARY KEY AUTOINCREMENT,
            SaleID INTEGER,
            ProductID INTEGER,
            Quantity INTEGER,
            Subtotal REAL,
            FOREIGN KEY (SaleID) REFERENCES Sales(SaleID),
            FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
        );
    ''')

    # ### RUBRIC: INDEX
    c.execute("CREATE INDEX IF NOT EXISTS idx_product_category ON Products(Category);")

    # ### RUBRIC: VIEW
    # Creates a virtual table for daily revenue summary
    c.execute('''
        CREATE VIEW IF NOT EXISTS v_DailyRevenue AS
        SELECT SaleDate, COUNT(SaleID) as TransCount, SUM(TotalAmount) as Revenue
        FROM Sales
        GROUP BY SaleDate;
    ''')

    # ### RUBRIC: TRIGGER
    # Prevents deleting a product if it has sales history (Data Integrity)
    c.execute('''
        CREATE TRIGGER IF NOT EXISTS PreventProductDelete
        BEFORE DELETE ON Products
        BEGIN
            SELECT RAISE(ABORT, 'ERROR: Cannot delete product. It has existing sales records!')
            WHERE EXISTS (SELECT 1 FROM SaleItems WHERE ProductID = OLD.ProductID);
        END;
    ''')

    # ### RUBRIC: 20 SAMPLE ROWS (Seed Data)
    c.execute("SELECT COUNT(*) FROM Products")
    if c.fetchone()[0] == 0:
        print("Seeding database with 20 sample items...")
        samples = [
            ('Coca Cola', 'Beverage', 25.00, 100), ('Pepsi', 'Beverage', 25.00, 100),
            ('Sprite', 'Beverage', 25.00, 80), ('Royal', 'Beverage', 25.00, 80),
            ('Nature Spring', 'Beverage', 15.00, 200), ('Gatorade', 'Beverage', 45.00, 50),
            ('Piattos', 'Snack', 35.00, 60), ('Nova', 'Snack', 35.00, 60),
            ('V-Cut', 'Snack', 38.00, 40), ('Chippy', 'Snack', 30.00, 75),
            ('Skyflakes', 'Biscuit', 8.00, 500), ('Fita', 'Biscuit', 9.00, 300),
            ('Oreo', 'Biscuit', 12.00, 250), ('Magic Flakes', 'Biscuit', 7.00, 400),
            ('Safeguard', 'Hygiene', 45.00, 30), ('Palmolive', 'Hygiene', 12.00, 150),
            ('Colgate', 'Hygiene', 85.00, 40), ('Alcohol 70%', 'Hygiene', 55.00, 25),
            ('Ballpen', 'School', 10.00, 100), ('Notebook', 'School', 25.00, 100)
        ]
        c.executemany("INSERT INTO Products (Name, Category, Price, StockQty) VALUES (?,?,?,?)", samples)
        conn.commit()

    conn.close()