import requests
from bs4 import BeautifulSoup
from .session_manager import save_session
from .payment_processor import PaymentProcessor


class Coffeete:
    def __init__(self, cookies=None, payment_url='https://www.coffeete.ir/UserPanel/payment/DonateBe?page=1'):
        self.payment_url = payment_url
        self.session = requests.Session()

        # If cookies exist, use them; else start with a new session
        if cookies:
            self.session.cookies.update(cookies)
        else:
            print("Starting a fresh session...")

    def login(self, login_url, login_payload):
        """Login to the site and store session cookies."""
        print("Logging in...")
        response = self.session.post(login_url, data=login_payload)
        if response.status_code == 200:
            print("Login successful!")
            # Save session cookies for future use
            save_session(self.session.cookies)
        else:
            print(f"Failed to log in, status code {response.status_code}")

    def get_all_payments(self):
        """Fetch all pages of payments."""
        payments = []
        current_page_url = self.payment_url
        payment_processor = PaymentProcessor(self.session)

        while current_page_url:
            print(f"Fetching data from {current_page_url}")
            page_data = payment_processor.get_page_data(current_page_url)
            if page_data:
                payments.extend(page_data)

            soup = BeautifulSoup(self.session.get(current_page_url).text, 'html.parser')
            next_page_link = soup.find('a', class_='btn-paging', href=True)
            if next_page_link and 'href' in next_page_link.attrs:
                current_page_url = 'https://www.coffeete.ir' + next_page_link['href']
            else:
                current_page_url = None

        return payments
