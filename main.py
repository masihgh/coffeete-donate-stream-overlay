from app.config import get_login_credentials, LOGIN_URL
from app.session_manager import load_session
from app.coffeete import Coffeete

def main():
    # Load session from file if available
    cookies = load_session()

    coffeete = Coffeete(cookies=cookies)

    # If no session, log in
    if not cookies:
        print("No session file found. A fresh session will be created.")
        username, password = get_login_credentials()
        coffeete.login(LOGIN_URL, username, password)

    # Fetch and print payments
    payments = coffeete.get_all_payments()
    coffee_data = coffeete.get_coffee_and_today_donates()
    print(payments)
    print(coffee_data)

if __name__ == "__main__":
    main()
