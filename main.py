from app.coffeete import Coffeete
from app.session_manager import load_session
from app.config import get_login_credentials, PAYMENT_URL, LOGIN_URL


def main():
    # Fetch the login credentials from the config file
    username, password = get_login_credentials()

    # Use the credentials to create the login payload
    LOGIN_PAYLOAD = {
        'username': username,
        'password': password
    }

    # Try to load session from file
    cookies = load_session()

    # Initialize Coffeete with the loaded cookies or fresh session
    coffeete = Coffeete(cookies, PAYMENT_URL)

    if cookies:
        # If session loaded, get payments
        payments_data = coffeete.get_all_payments()
        if payments_data:
            print("Payments data fetched successfully!")
            for payment in payments_data:
                print(payment)
        else:
            print("No payments data found.")
    else:
        # If session is not found, perform login
        coffeete.login(LOGIN_URL, LOGIN_PAYLOAD)
        # After login, fetch payments data
        payments_data = coffeete.get_all_payments()
        if payments_data:
            print("Payments data fetched successfully!")
            for payment in payments_data:
                print(payment)

if __name__ == "__main__":
    main()
