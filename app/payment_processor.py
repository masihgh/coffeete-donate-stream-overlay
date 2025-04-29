class PaymentProcessor:
    def __init__(self, session):
        self.session = session

    def extract_payments(self, soup):
        """Extract payments from the soup object and return a list."""
        table = soup.find('table', class_='table table-striped h4 table-hover')
        if not table:
            print("No table found on the page.")
            return []

        data = []
        for row in table.find_all('tr')[1:]:  # Skip the header row
            columns = row.find_all('td')
            if len(columns) >= 6:
                donor_name = columns[2].get_text(strip=True)
                date = columns[1].get_text(strip=True)
                amount = columns[4].get_text(strip=True)

                # Clean and convert the data
                amount = self.clean_amount(amount)
                date = self.clean_date(date)

                # Get description
                description_textarea = columns[3].find('textarea')
                description = None

                # Check if 'textarea' exists and has a 'value' attribute
                if description_textarea and 'value' in description_textarea.attrs:
                    description = description_textarea['value']

                # Get unique ID from input field
                donation_id_input = columns[5].find('input', {'class': 'show-onPage'})
                donation_id = donation_id_input['value'] if donation_id_input else None

                # Add donation with unique id
                if donation_id:
                    data.append({
                        'donor_name': donor_name,
                        'date': date,
                        'amount': amount,
                        'description': description,
                        'id': donation_id  # Include unique ID
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
