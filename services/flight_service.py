from amadeus import Client
from config import Config

def search_flights(start_code, dest_code, date):
    amadeus = Client(
        client_id=Config.AMADEUS_CLIENT_ID,
        client_secret=Config.AMADEUS_CLIENT_SECRET,
    )
    response = amadeus.shopping.flight_offers_search.get(
        originLocationCode=start_code,
        destinationLocationCode=dest_code,
        departureDate=date,
        adults=1
    )
    return response