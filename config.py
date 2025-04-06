import os


class Config:
    AMADEUS_CLIENT_ID = os.environ.get('AMADEUS_CLIENT_ID', 'your_client_id')
    AMADEUS_CLIENT_SECRET = os.environ.get('AMADEUS_CLIENT_SECRET', 'your_client_secret')