import pickle
import os

SESSION_FILE = 'session.pkl'

def save_session(cookies):
    """Save session cookies to a file."""
    with open(SESSION_FILE, 'wb') as f:
        pickle.dump(cookies, f)
    print(f"Session saved to {SESSION_FILE}")

def load_session():
    """Load session cookies from a file."""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'rb') as f:
            cookies = pickle.load(f)
        print("Session loaded successfully.")
        return cookies
    else:
        print("No session file found. A fresh session will be created.")
        return None
