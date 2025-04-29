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
    for payment in payments:
        print(payment)

    # Fetch and print coffee data
    coffee_data = coffeete.get_coffee_and_today_donates()
    print(f"Today's Coffee: {coffee_data['today_coffee']}")
    print(f"Total Coffee: {coffee_data['total_coffee']}")

    # Query the biggest coffee donation
    biggest_coffee = coffeete.get_biggest_coffee_donate()
    print(f"Biggest Coffee Donation: {biggest_coffee}")

    # Query the latest coffee donation
    latest_coffee = coffeete.get_latest_coffee_donate()
    print(f"Latest Coffee Donation: {latest_coffee}")

    # Query the 20 latest donations
    latest_20_donates = coffeete.get_20_latest_donates()
    print(f"Latest 20 Donations: {latest_20_donates}")


if __name__ == "__main__":
    main()
