import os
import requests

def get_stock_price(ticker):
    # Set the API key and stock symbol
    API_KEY = os.getenv('VANTAGE_API_KEY')

    # API endpoint URL
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={API_KEY}'

    # Send a GET request to the API
    response = requests.get(url)

    # Parse the response JSON
    data = response.json()

    # Extract the relevant stock data
    price = data['Global Quote']['05. price']
    change = data['Global Quote']['09. change']

    return float(price), float(change)