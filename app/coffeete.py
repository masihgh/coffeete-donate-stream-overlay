import requests
from bs4 import BeautifulSoup
import json
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

        # Initialize payment processor
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
        """Extract today's and total coffee donations."""
        coffee_data = {'today_coffee': None, 'total_coffee': None}

        home_url = "https://www.coffeete.ir/UserPanel/Home"
        response = self.session.get(home_url, headers=self.headers)

        if response.status_code != 200:
            print(f"Failed to fetch the home page with status code {response.status_code}")
            return coffee_data

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract today's coffee donation
        today_coffee_element = soup.select_one("#wrapper > div:nth-child(3) > div > div > div:nth-child(2) > div:nth-child(3) > div > div > div:nth-child(2) > h3")
        if today_coffee_element:
            coffee_data['today_coffee'] = int(today_coffee_element.get_text(strip=True).replace(',', ''))

        # Extract total coffee donation
        total_coffee_element = soup.select_one("#wrapper > div:nth-child(3) > div > div > div:nth-child(2) > div:nth-child(2) > div > div > div:nth-child(2) > h3")
        if total_coffee_element:
            coffee_data['total_coffee'] = int(total_coffee_element.get_text(strip=True).replace(',', ''))

        return coffee_data

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
                current_page_url = 'https://www.coffeete.ir' + next_page['href']
            else:
                current_page_url = None  # No more pages to fetch

        return payments

    def save_donations_to_file(self):
        """Save donations to an unencrypted JSON file."""
        donations = self.get_all_payments()

        try:
            with open('donations.json', 'r') as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = []

        # Add the new donations if not already in the existing file
        for donation in donations:
            if donation['donation_id'] not in [d['donation_id'] for d in existing_data]:
                existing_data.append(donation)

        with open('donations.json', 'w',encoding='UTF-8') as file:
            json.dump(existing_data, file, indent=4, ensure_ascii=False)

    def check_for_updates(self):
        """Check for updates in the donations and update the JSON file if necessary."""
        new_donations = self.get_all_payments()
        try:
            with open('donations.json', 'r') as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = []

        # Compare and update
        updated = False
        for donation in new_donations:
            if donation['donation_id'] not in [d['donation_id'] for d in existing_data]:
                existing_data.append(donation)
                updated = True

        if updated:
            print("New donations detected! Updating the JSON file.")
            with open('donations.json', 'w',encoding='UTF-8') as file:
                json.dump(existing_data, file, indent=4, ensure_ascii=False)
        else:
            print("No new donations found. The JSON file is up to date.")

    def get_biggest_coffee_donation(self):
        donations = self.get_all_payments()
        if donations:
            biggest = max(donations, key=lambda x: x['amount'])
            return biggest
        return None

    def get_latest_coffee_donation(self):
        donations = self.get_all_payments()
        if donations:
            return donations[0]
        return None

    def get_latest_20_donates(self):
        donations = self.get_all_payments()
        return donations[:20]
