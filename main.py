from app.config import get_login_credentials, LOGIN_URL
from app.session_manager import load_session
from app.coffeete import Coffeete
import json
import time


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
    print(f"Payments: {payments}")

    # Fetch coffee data and donations
    coffee_data = coffeete.get_coffee_and_today_donates()
    print(f"Today's Coffee: {coffee_data['today_coffee']}")
    print(f"All Coffee: {coffee_data['total_coffee']}")

    # Save donations to a JSON file initially
    coffeete.save_donations_to_file()

    # Check for updates periodically (e.g., every 5 minutes)
    while True:
        print("Checking for new donations...")
        coffeete.check_for_updates()
        time.sleep(5)  # Check every 5 minutes


if __name__ == "__main__":
    main()
