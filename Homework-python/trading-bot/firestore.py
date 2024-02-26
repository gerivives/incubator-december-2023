import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin.exceptions import FirebaseError

class FirestoreDatabase:
    def __init__(self, credentials_path):
        self.credentials_path = credentials_path
        self.db = self.initialize_db()

    def initialize_db(self):
        """Initialize the Firestore database."""
        try:
            # Check if the app was already initialized
            if not firebase_admin._apps:
                cred = credentials.Certificate(self.credentials_path)
                firebase_admin.initialize_app(cred)
            return firestore.client()
        except FirebaseError as e:
            print(f"Failed to initialize Firestore: {e}")
            return None

    def user_exists(self, email):
        """Check if a user exists in the Firestore database."""
        users_ref = self.db.collection('users')
        query = users_ref.where('email', '==', email).get()
        return len(query) > 0

    def create_portfolio(self):
        """Create a new portfolio document in Firestore."""
        portfolio_ref = self.db.collection('portfolios').document()
        portfolio_ref.set({})  # Assuming an empty portfolio to start with
        return portfolio_ref

    def create_user(self, email):
        """Create a new user with a portfolio in Firestore."""
        if self.user_exists(email):
            print(f"User {email} already exists.")
            return None

        # Create a new portfolio for the user
        portfolio_ref = self.create_portfolio()

        # Create a new user document with the email and a reference to the portfolio
        user_ref = self.db.collection('users').document()
        user_data = {
            'email': email,
            'portfolio': portfolio_ref
        }
        user_ref.set(user_data)
        print(f"User {email} created with a new portfolio.")
        return user_data

    def get_user_portfolio_ref(self, email):
        """Get a reference to the user's portfolio."""
        users_ref = self.db.collection('users')
        query = users_ref.where('email', '==', email).get()
        if query:
            return query[0].to_dict()['portfolio']
        else:
            return None

    def add_stock_to_portfolio(self, email, ticker, quantity, datetime):
        """Add a stock to the user's portfolio."""
        portfolio_ref = self.get_user_portfolio_ref(email)
        if not portfolio_ref:
            print(f"No portfolio found for user {email}.")
            return None

        # Create a new stock document
        stock_ref = self.db.collection('stocks').document()
        stock_data = {
            'ticker': ticker,
            'quantity': quantity,
            'date': datetime
        }
        stock_ref.set(stock_data)

        # Add the stock reference to the user's portfolio
        portfolio_ref.update({'stocks': firestore.ArrayUnion([stock_ref])})

        print(f"Stock {ticker} added to the portfolio of user {email}.")
        return stock_ref

    def get_all_stocks_for_user(self, email):
        """Retrieve all stocks for a user identified by email."""
        # Attempt to retrieve the user document by email
        users_ref = self.db.collection('users')
        user_docs = users_ref.where('email', '==', email).stream()

        # Get the first (and should be only) user doc
        user_doc = next(user_docs, None)
        if user_doc is None:
            print(f"No user found with email {email}.")
            return None

        # Get the portfolio reference from the user document
        portfolio_ref = user_doc.to_dict().get('portfolio')
        if not portfolio_ref:
            print(f"User {email} has no portfolio.")
            return None

        # Retrieve the portfolio document
        portfolio_doc = portfolio_ref.get()
        if not portfolio_doc.exists:
            print(f"Portfolio document for user {email} does not exist.")
            return None

        # Get the stock references from the portfolio document
        stock_refs = portfolio_doc.to_dict().get('stocks', [])

        # Fetch each stock document and add it to the stocks list
        stocks = []
        for stock_ref in stock_refs:
            stock_doc = stock_ref.get()
            if stock_doc.exists:
                stock_data = stock_doc.to_dict()
                # Directly format the DatetimeWithNanoseconds object
                formatted_datetime = stock_data['date'].strftime("%d %B %Y, %I:%M %p")
                # Add formatted datetime to your stock data or use it as needed
                stock_data['formatted_date'] = formatted_datetime
                stocks.append(stock_data)

        return stocks