"""
Populates the MySQL database with sample tables and data.
Uses SQLAlchemy so it works with whatever DB_URL is configured in .env.

Run with:  python setup_dummy_db.py
"""
import sys
import os

# Make sure app packages are importable
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from app.db.database import get_engine


def create_dummy_db():
    engine = get_engine()

    with engine.connect() as conn:
        # Create Users table (MySQL-compatible)
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """))

        # Create Orders table (MySQL-compatible)
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            product_name VARCHAR(255),
            price DECIMAL(10, 2),
            order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """))

        # Insert sample data — INSERT IGNORE skips duplicates on UNIQUE keys
        conn.execute(text("INSERT IGNORE INTO users (name, email) VALUES ('Alice Smith', 'alice@example.com')"))
        conn.execute(text("INSERT IGNORE INTO users (name, email) VALUES ('Bob Jones', 'bob@example.com')"))
        conn.execute(text("INSERT IGNORE INTO users (name, email) VALUES ('Charlie Brown', 'charlie@example.com')"))

        conn.execute(text("INSERT IGNORE INTO orders (user_id, product_name, price) VALUES (1, 'Laptop', 1200.50)"))
        conn.execute(text("INSERT IGNORE INTO orders (user_id, product_name, price) VALUES (2, 'Smartphone', 800.00)"))
        conn.execute(text("INSERT IGNORE INTO orders (user_id, product_name, price) VALUES (1, 'Mouse', 25.99)"))
        conn.execute(text("INSERT IGNORE INTO orders (user_id, product_name, price) VALUES (3, 'Keyboard', 45.00)"))

        conn.commit()

    print("Database populated successfully with dummy data!")


if __name__ == '__main__':
    create_dummy_db()
