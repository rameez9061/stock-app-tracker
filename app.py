import os
import requests
from flask import Flask, render_template, jsonify
from datetime import datetime

app = Flask(__name__)

# Constants (API Key for Alpha Vantage)
ALPHA_VANTAGE_API_KEY = 'your_alpha_vantage_api_key'  # Replace with your actual API key
ALPHA_VANTAGE_URL = 'https://www.alphavantage.co/query'

# Binary Search Tree (BST) and Linked List implementation

class DailyStockDataNode:
    def __init__(self, timestamp, open_price, close_price, volume):
        self.timestamp = timestamp
        self.open_price = open_price
        self.close_price = close_price
        self.volume = volume
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def insert(self, timestamp, open_price, close_price, volume):
        new_node = DailyStockDataNode(timestamp, open_price, close_price, volume)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def traverse(self):
        data = []
        current = self.head
        while current:
            data.append({
                'timestamp': current.timestamp,
                'open': current.open_price,
                'close': current.close_price,
                'volume': current.volume
            })
            current = current.next
        return data

class StockNode:
    def __init__(self, symbol, daily_data):
        self.symbol = symbol
        self.data = daily_data
        self.left = None
        self.right = None

class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, symbol, daily_data):
        new_node = StockNode(symbol, daily_data)
        if self.root is None:
            self.root = new_node
        else:
            self._insert(self.root, new_node)

    def _insert(self, root, new_node):
        if new_node.symbol < root.symbol:
            if root.left is None:
                root.left = new_node
            else:
                self._insert(root.left, new_node)
        else:
            if root.right is None:
                root.right = new_node
            else:
                self._insert(root.right, new_node)

    def search(self, symbol):
        return self._search(self.root, symbol)

    def _search(self, root, symbol):
        if root is None or root.symbol == symbol:
            return root
        if symbol < root.symbol:
            return self._search(root.left, symbol)
        return self._search(root.right, symbol)

    def get_all_symbols(self):
        symbols = []
        self._in_order_traversal(self.root, symbols)
        return symbols

    def _in_order_traversal(self, root, symbols):
        if root:
            self._in_order_traversal(root.left, symbols)
            symbols.append(root.symbol)
            self._in_order_traversal(root.right, symbols)

# Initialize the BST for stock symbols
stock_bst = BinarySearchTree()

# Function to fetch stock data using Alpha Vantage API
def fetch_stock_data(symbol):
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    response = requests.get(ALPHA_VANTAGE_URL, params=params)
    data = response.json()
    if 'Time Series (Daily)' in data:
        time_series = data['Time Series (Daily)']
        daily_data = []
        for date, values in time_series.items():
            timestamp = date
            open_price = float(values['1. open'])
            close_price = float(values['4. close'])
            volume = int(values['5. volume'])
            daily_data.append({'timestamp': timestamp, 'open': open_price, 'close': close_price, 'volume': volume})
        return daily_data
    return None

# Flask Routes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_stock/<symbol>', methods=['GET'])
def add_stock(symbol):
    stock_data = fetch_stock_data(symbol)
    if stock_data:
        daily_data = LinkedList()
        for data_point in stock_data:
            daily_data.insert(data_point['timestamp'], data_point['open'], data_point['close'], data_point['volume'])
        stock_bst.insert(symbol, daily_data)  # Insert into BST
        return jsonify({"message": f"Stock {symbol} added successfully."}), 200
    return jsonify({"message": f"Failed to add stock {symbol}."}), 400

@app.route('/get_stock_data/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    stock_node = stock_bst.search(symbol)  # Search the BST for the stock symbol
    if stock_node:
        data = stock_node.data.traverse()  # Get data from the linked list
        return jsonify({"stock_data": data}), 200
    return jsonify({"message": f"Stock {symbol} not found."}), 404

@app.route('/get_symbols', methods=['GET'])
def get_symbols():
    # Fetch all stock symbols from the BST and return them as a JSON list
    symbols = stock_bst.get_all_symbols()
    return jsonify(symbols), 200

if __name__ == '__main__':
    app.run(debug=True)
