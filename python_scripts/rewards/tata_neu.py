import os
import requests

# Load sensitive values from environment variables
AUTH_TOKEN = os.getenv("AUTHORIZATION_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Check that the environment variables are set
if not all([AUTH_TOKEN, CLIENT_ID, CLIENT_SECRET]):
    raise EnvironmentError("Required environment variables are not set.")

# Define headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:137.0) Gecko/20100101 Firefox/137.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Referer': 'https://www.tataneu.com/',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'anonymous_id': '790d79c6-7ae9-4f9f-8958-41d0ea091d44',
    'request_id': 'a97ee1a8-b568-4189-b394-b5fa8dca52e0',
    'store_id': 'tcp.default',
    'neu-app-version': '5.8.0',
    'content-type': 'application/json',
    'Origin': 'https://www.tataneu.com',
    'DNT': '1',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'authorization': f'Bearer {AUTH_TOKEN}',
    'Connection': 'keep-alive',
    'TE': 'trailers'
}

# URL to request
url = (
    "https://api.tatadigital.com/api/v2/np/ledger/getCustomerLedgerInfo"
    "?excludeEvents=DelayedAccrual%2CCustomerRegistration%2CManualPointsConversion%2CCustomerImport"
    "&identifierName=externalId"
    "&source=INSTORE"
    "&getCustomFields=true"
    "&getMaxConversionDetails=true"
    "&getBillDetails=true"
    "&offset=1"
)

# Make the GET request
response = requests.get(url, headers=headers)

# Print response
print(f"Status Code: {response.status_code}")
print("Response JSON:" if response.headers.get('Content-Type') == 'application/json' else "Response Text:")
print(response.json() if 'application/json' in response.headers.get('Content-Type', '') else response.text)
