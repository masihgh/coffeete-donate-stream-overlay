import pickle
import os

# File to store session cookies
SESSION_FILE = "session.pkl"

def save_session(cookies):
    """Save the session cookies to a file."""
    with open(SESSION_FILE, 'wb') as f:
        pickle.dump(cookies, f)
    print("Session saved successfully.")

def load_session():
    """Load the session cookies from a file."""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'rb') as f:
            cookies = pickle.load(f)
        print("Session loaded successfully.")
        return cookies
    else:
        print("No session file found. Please log in.")
        return None
