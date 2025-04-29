import configparser

# Path to the configuration file
CONFIG_FILE = 'config.ini'

PAYMENT_URL = "https://www.coffeete.ir/UserPanel/payment/DonateBe?page=1"
LOGIN_URL = "https://www.coffeete.ir/login"

def get_login_credentials():
    """Reads the login credentials from the config.ini file."""
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    username = config.get('login', 'username', fallback=None)
    password = config.get('login', 'password', fallback=None)

    if username and password:
        return username, password
    else:
        raise ValueError("Username or password not found in the config file.")


# Example of using the function
if __name__ == "__main__":
    username, password = get_login_credentials()
    print(f"Username: {username}, Password: {password}")
