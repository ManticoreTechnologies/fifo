import sqlite3
from Order import Order
class Database:
    def __init__(self, db_name="market.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self):
        # Create tables for market, orders, and prices
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS market (
                symbol TEXT PRIMARY KEY
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                user_address TEXT,
                symbol TEXT,
                side TEXT,
                price INTEGER,
                quantity INTEGER,
                quantity_filled INTEGER,
                created_at TEXT,
                status TEXT,
                order_type TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS prices (
                price INTEGER PRIMARY KEY,
                symbol TEXT,
                total_quantity INTEGER
            )
        ''')
        self.connection.commit()

    def save_order(self, order):
        # Save or update an order in the database
        self.cursor.execute('''
            INSERT OR REPLACE INTO orders (order_id, user_address, symbol, side, price, quantity, quantity_filled, created_at, status, order_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (order.order_id, order.user_address, order.symbol, order.side, order.price, order.quantity, order.quantity_filled, order.created_at, order.status, order.order_type))
        self.connection.commit()

    def save_price(self, price, symbol, total_quantity):
        # Save or update a price level in the database
        self.cursor.execute('''
            INSERT OR REPLACE INTO prices (price, symbol, total_quantity)
            VALUES (?, ?, ?)
        ''', (price, symbol, total_quantity))
        self.connection.commit()

    def close(self):
        self.connection.close()

    def load_orders(self, symbol):
        # Load orders from the database for a specific symbol
        self.cursor.execute('''
            SELECT order_id, user_address, symbol, side, price, quantity, quantity_filled, created_at, status, order_type
            FROM orders
            WHERE symbol = ?
        ''', (symbol,))
        orders = self.cursor.fetchall()
        return [
            Order(
                user_address=order[1],
                symbol=order[2],
                side=order[3],
                price=order[4],
                quantity=order[5],
                order_id=order[0],
                order_type=order[9],
                quantity_filled=order[6],
                created_at=order[7],
                status=order[8]
            )
            for order in orders
        ]
