import requests
from bs4 import BeautifulSoup
from app.session_manager import save_session, load_session
from app.payment_processor import PaymentProcessor
import json


class Coffeete:
    def __init__(self, cookies=None, payment_url='https://www.coffeete.ir/UserPanel/payment/DonateBe?page=1', donations_file='donations.json', home_url='https://www.coffeete.ir/UserPanel/Home'):
        self.payment_url = payment_url
        self.home_url = home_url
        self.donations_file = donations_file
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        if cookies:
            self.session.cookies.update(cookies)
        else:
            print("Starting a fresh session...")

        # Initialize PaymentProcessor
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

    def get_coffee_and_today_donates(self):
        """Fetch data from the home page for today's coffee and total coffee."""
        response = self.session.get(self.home_url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract today's coffee count
        today_coffee = soup.select_one("#wrapper > div:nth-child(3) > div > div > div:nth-child(2) > div:nth-child(3) > div > div > div:nth-child(2) > h3")
        total_coffee = soup.select_one("#wrapper > div:nth-child(3) > div > div > div:nth-child(2) > div:nth-child(2) > div > div > div:nth-child(2) > h3")

        today_coffee_count = today_coffee.get_text(strip=True) if today_coffee else "N/A"
        total_coffee_count = total_coffee.get_text(strip=True) if total_coffee else "N/A"

        return {
            "today_coffee": today_coffee_count.replace(',',''),
            "total_coffee": total_coffee_count.replace(',','')
        }

    def get_all_payments(self):
        """Fetch all pages of payments and return them."""
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

    def load_donates(self):
        """Load donations from the JSON file."""
        try:
            with open(self.donations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_donates(self, donations):
        """Save donations to the JSON file."""
        with open(self.donations_file, 'w', encoding='utf-8') as f:
            json.dump(donations, f, ensure_ascii=False, indent=4)

    def append_new_donates(self, new_donates):
        """Append new donations to the JSON file without duplicating."""
        donations = self.load_donates()

        # Remove duplicates based on donation ID
        existing_donates = {d['id']: d for d in donations}

        # Adding new donations, ensuring no duplicates based on ID
        for donate in new_donates:
            if donate['id'] not in existing_donates:
                existing_donates[donate['id']] = donate

        # Save the unique donations back to the file
        self.save_donates(list(existing_donates.values()))

    def get_biggest_coffee_donate(self):
        """Return the biggest donation."""
        donations = self.load_donates()
        if donations:
            return max(donations, key=lambda x: x['amount'])
        return None

    def get_latest_coffee_donate(self):
        """Return the latest donation."""
        donations = self.load_donates()
        if donations:
            return donations[-1]
        return None

    def get_20_latest_donates(self):
        """Return the 20 latest donations."""
        donations = self.load_donates()
        return donations[-20:] if donations else []
