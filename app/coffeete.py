import os
import json
import requests
from bs4 import BeautifulSoup
from app.session_manager import save_session
from app.payment_processor import PaymentProcessor

class Coffeete:
    def __init__(self, cookies=None, payment_url='https://www.coffeete.ir/UserPanel/payment/DonateBe?page=1', home_url='https://www.coffeete.ir/UserPanel/Home', donate_file='donates.json'):
        self.payment_url = payment_url
        self.home_url = home_url
        self.donate_file = donate_file  # Path to store donations in a JSON file
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        if cookies:
            self.session.cookies.update(cookies)
        else:
            print("Starting a fresh session...")

    def load_donates(self):
        """Load existing donations from the JSON file."""
        if os.path.exists(self.donate_file):
            with open(self.donate_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_donates(self, donations):
        """Save the current donations list back to the JSON file."""
        with open(self.donate_file, 'w', encoding='utf-8') as f:
            json.dump(donations, f, ensure_ascii=False, indent=4)

    def append_new_donates(self, new_donates):
        """Append new donations to the JSON file."""
        donations = self.load_donates()
        donations.extend(new_donates)
        self.save_donates(donations)

    def get_coffee_and_today_donates(self):
        """Scrape and return the number of coffees and today's donation."""
        response = self.session.get(self.home_url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the elements for today's coffee and all coffee donations
        today_coffee_element = soup.select_one("#wrapper > div:nth-child(3) > div > div > div:nth-child(2) > div:nth-child(3) > div > div > div:nth-child(2) > h3")
        all_coffee_element = soup.select_one("#wrapper > div:nth-child(3) > div > div > div:nth-child(2) > div:nth-child(2) > div > div > div:nth-child(2) > h3")

        today_coffee = today_coffee_element.text.strip() if today_coffee_element else "0"
        all_coffee = all_coffee_element.text.strip() if all_coffee_element else "0"

        return {
            "today_coffee": today_coffee,
            "all_coffee": all_coffee
        }

    def get_biggest_coffee_donate(self):
        """Get the biggest coffee donation."""
        donations = self.load_donates()
        if not donations:
            return None
        biggest_donate = max(donations, key=lambda x: x['amount'], default=None)
        return biggest_donate

    def get_latest_coffee_donate(self):
        """Get the latest coffee donation."""
        donations = self.load_donates()
        if not donations:
            return None
        latest_donate = max(donations, key=lambda x: x['date'], default=None)
        return latest_donate

    def get_latest_20_donates(self):
        """Get the 20 latest donations."""
        donations = self.load_donates()
        donations_sorted = sorted(donations, key=lambda x: x['date'], reverse=True)  # Sorting by date (newest first)
        return donations_sorted[:20]

    def get_all_payments(self):
        """Fetch all pages of payments."""
        payments = []
        current_page_url = self.payment_url
        payment_processor = PaymentProcessor(self.session)

        while current_page_url:
            print(f"Fetching data from {current_page_url}")
            response = self.session.get(current_page_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            page_data = payment_processor.extract_payments(soup)
            if page_data:
                payments.extend(page_data)

            # Find next page URL
            next_page = soup.select_one("ul.pagination li:not(.active) a.btn-paging[href]")

            if next_page:
                current_page_url = 'https://www.coffeete.ir' + next_page['href']
            else:
                current_page_url = None  # No more pages to fetch

        # After fetching payments, append them to the JSON file
        self.append_new_donates(payments)
        return payments
