import sqlite3
import requests

def get_domain_price(provider, domain):
    # Extract the TLD from the domain
    tld = domain.split('.')[-1]

    # Connect to the database
    conn = sqlite3.connect('domain_prices.db')
    c = conn.cursor()

    # Check if the TLD price is in the database
    c.execute('SELECT price FROM prices WHERE provider = ? AND tld = ?', (provider, tld))
    row = c.fetchone()

    if row is not None:
        # If the price is already in the database, return it
        price = row[0]
    else:
        # If the price is not in the database, query the provider's API
        price = get_provider_price(provider, tld)

        # Insert the new price into the database
        c.execute('INSERT INTO prices (provider, tld, price) VALUES (?, ?, ?)', (provider, tld, price))
        conn.commit()

    # Close the database connection and return the price
    conn.close()
    return price

def get_provider_price(provider, tld):
    # Make API call to the provider to get the price for the TLD
    # You will need to replace this with the actual API call for the provider you're using
    api_key = 'your_api_key_here'
    user_name = 'your_namecheap_username_here'
    url = f'https://api.namecheap.com/xml.response?ApiUser={user_name}&ApiKey={api_key}&UserName={user_name}&Command=namecheap.domains.getTldList'
    response = requests.get(url)
    data = response.text
    tld_price = None

    # Parse the API response to get the price for the TLD
    # You will need to replace this with the actual parsing logic for the provider you're using
    # This example assumes the provider returns the price in a "price" field in a JSON object
    response_data = json.loads(data)
    tld_price = response_data['price']

    if tld_price is None:
        raise Exception(f'Unable to retrieve price for {tld} from {provider}')

    return tld_price
