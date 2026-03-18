import sqlite3

def create_dummy_db():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create Orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_name TEXT,
        price REAL,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')
    
    # Insert sample data
    cursor.execute("INSERT OR IGNORE INTO users (name, email) VALUES ('Alice Smith', 'alice@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (name, email) VALUES ('Bob Jones', 'bob@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (name, email) VALUES ('Charlie Brown', 'charlie@example.com')")
    
    cursor.execute("INSERT INTO orders (user_id, product_name, price) VALUES (1, 'Laptop', 1200.50)")
    cursor.execute("INSERT INTO orders (user_id, product_name, price) VALUES (2, 'Smartphone', 800.00)")
    cursor.execute("INSERT INTO orders (user_id, product_name, price) VALUES (1, 'Mouse', 25.99)")
    cursor.execute("INSERT INTO orders (user_id, product_name, price) VALUES (3, 'Keyboard', 45.00)")
    
    conn.commit()
    conn.close()
    print("Database app.db created successfully with dummy data!")

if __name__ == '__main__':
    create_dummy_db()
