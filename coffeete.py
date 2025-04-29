import requests
from bs4 import BeautifulSoup
from app.session_manager import save_session


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

    def get_page_data(self, page_url):
        """Fetch the data from a single page and return the extracted information."""
        response = self.session.get(page_url)
        if response.status_code != 200:
            print(f"Failed to fetch {page_url} with status code {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='table table-striped h4 table-hover')
        if not table:
            print("No table found on the page.")
            return None

        data = []
        for row in table.find_all('tr')[1:]:  # Skip the header row
            columns = row.find_all('td')
            if len(columns) >= 6:
                # Extract the data from the row
                donor_name = columns[2].get_text(strip=True)
                date = columns[1].get_text(strip=True)
                amount = columns[4].get_text(strip=True)

                # Clean and convert the data
                amount = self.clean_amount(amount)
                date = self.clean_date(date)

                # Safely get the description if available
                description_textarea = columns[3].find('textarea')
                description = description_textarea[
                    'value'] if description_textarea and 'value' in description_textarea.attrs else None

                data.append({
                    'donor_name': donor_name,
                    'date': date,
                    'amount': amount,
                    'description': description
                })

        return data

    def clean_amount(self, amount_str):
        """Clean and convert the amount from string to integer."""
        amount_str = amount_str.replace(',', '').replace('تومان', '').strip()
        return int(amount_str) if amount_str.isdigit() else 0

    def clean_date(self, persian_date):
        """Convert Persian date to a format: 'YYYY-MM-DD'."""
        month_mapping = {
            'فروردین': '1', 'اردیبهشت': '2', 'خرداد': '3', 'تیر': '4', 'مرداد': '5', 'شهریور': '6',
            'مهر': '7', 'آبان': '8', 'آذر': '9', 'دی': '10', 'بهمن': '11', 'اسفند': '12'
        }

        for month_name, month_number in month_mapping.items():
            persian_date = persian_date.replace(month_name, month_number)

        try:
            parts = persian_date.split('-')
            if len(parts) == 3:
                day = int(parts[0])
                month = int(parts[1])
                year = int(parts[2])
                return f"{year}-{month:02d}-{day:02d}"
        except ValueError:
            print(f"Error parsing the date: {persian_date}")
        return None

    def get_all_payments(self):
        """Fetch all pages of payments."""
        payments = []
        current_page_url = self.payment_url

        while current_page_url:
            print(f"Fetching data from {current_page_url}")
            page_data = self.get_page_data(current_page_url)
            if page_data:
                payments.extend(page_data)

            soup = BeautifulSoup(self.session.get(current_page_url).text, 'html.parser')
            next_page_link = soup.find('a', class_='btn-paging', href=True)
            if next_page_link and 'href' in next_page_link.attrs:
                current_page_url = 'https://www.coffeete.ir' + next_page_link['href']
            else:
                current_page_url = None

        return payments
