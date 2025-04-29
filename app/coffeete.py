import requests
from bs4 import BeautifulSoup
from app.session_manager import save_session
from app.payment_processor import PaymentProcessor

class Coffeete:
    def __init__(self, cookies=None, payment_url='https://www.coffeete.ir/UserPanel/payment/DonateBe?page=1'):
        self.payment_url = payment_url
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        if cookies:
            self.session.cookies.update(cookies)
        else:
            print("Starting a fresh session...")

        # Initialize PaymentProcessor here
        self.payment_processor = PaymentProcessor(self.session)

    def login(self, login_url, username, password):
        """Login to the site and store session cookies."""
        print("Logging in...")

        # Step 1: GET to retrieve CSRF token
        response = self.session.get(login_url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        token_input = soup.find("input", {"name": "__RequestVerificationToken"})

        if not token_input:
            raise Exception("CSRF token not found.")

        csrf_token = token_input["value"]

        # Step 2: POST login data
        login_payload = {
            "PhoneNumberOrUserName": username,
            "Password": password,
            "__RequestVerificationToken": csrf_token,
        }

        login_response = self.session.post(login_url, data=login_payload, headers=self.headers)

        if login_response.status_code == 200 and "ورود" not in login_response.text:
            print("Login successful!")
            save_session(self.session.cookies)
        else:
            raise Exception("Login failed, please check your credentials or site structure.")

    def get_all_payments(self):
        """Fetch all pages of payments."""
        payments = []
        current_page_url = self.payment_url

        while current_page_url:
            print(f"Fetching data from {current_page_url}")
            response = self.session.get(current_page_url, headers=self.headers)

            if response.status_code != 200:
                print(f"Failed to fetch {current_page_url} with status code {response.status_code}")
                break

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract payment data from the current page
            page_data = self.payment_processor.extract_payments(soup)
            if page_data:
                payments.extend(page_data)

            # Find next page URL
            next_page = soup.select_one("ul.pagination li:not(.active) a.btn-paging[href]")

            if next_page:
                # If next page exists, construct the full URL
                current_page_url = 'https://www.coffeete.ir' + next_page['href']
            else:
                current_page_url = None  # No more pages to fetch

        return payments
