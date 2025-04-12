from flask import Blueprint, request, jsonify, render_template
from services.flight_service import search_flights
from amadeus import Client, ResponseError
import json
from flask_paginate import Pagination, get_page_parameter,get_page_args
import logging
import csv


bp = Blueprint('flight_controller', __name__)


priceList = []
Date = []
Stops = []
numberOfBookableSeats = []
cabin = []


airports_list = []

# Constants for paging
ITEMS_PER_PAGE = 3  # Change this to whatever number of items you want per page

with open('airports.dat', encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        iata = row[4].strip()
        city = row[2].strip()
        country = row[3].strip()

        if iata and len(iata) == 3:  # filter only valid IATA codes
            airports_list.append({
                "city": city,
                "country": country,
                "iata_code": iata
            })

# Save to JSON file
with open('airports.json', 'w', encoding='utf-8') as json_file:
    json.dump(airports_list, json_file, indent=4)

with open('airports.json', 'r', encoding='utf-8') as file:
    airports_data = json.load(file)



#Route basic HTMLs
@bp.route('/Home', methods=['GET', 'POST'])
def home():
    return render_template('Home.html') 

@bp.route('/Project', methods=['GET', 'POST'])
def project():
    return render_template('Main.html') 

@bp.route('/Student', methods=['GET', 'POST'])
def student():
    return render_template('Student_Details.html') 


@bp.route('/airports', methods=['GET'])
def list_airports():
    search_term = request.args.get('search_term', '').strip().lower()

    # Just get unique combinations
    seen = set()
    table_data = []

    for entry in airports_data:
        key = (entry['city'], entry['country'], entry['iata_code'])
        if key not in seen:
            seen.add(key)

            # Check if search term matches any field
            if search_term:
                if (search_term in entry['city'].lower() or
                    search_term in entry['country'].lower() or
                    search_term in entry['iata_code'].lower()):
                    table_data.append({
                        'city': entry['city'],
                        'country': entry['country'],
                        'iata_code': entry['iata_code']
                    })
            else:
                table_data.append({
                    'city': entry['city'],
                    'country': entry['country'],
                    'iata_code': entry['iata_code']
                })

    # Sort the data based on the search term
    if search_term:
        # Check if search term is a country, city, or IATA code
        if search_term.isalpha():  # If the search term consists of alphabets, assume it's country or city
            table_data.sort(key=lambda x: (x['city'].lower(), x['country'].lower(), x['iata_code'].lower()))
        else:  # If the search term is alphanumeric, assume it's IATA code
            table_data.sort(key=lambda x: x['iata_code'].lower())

    return render_template('AirportsList.html', airports=table_data, search_term=search_term)



# Helper to get all template data (without sorting or toggling columns)
def get_template_data(page=1, per_page=10):
    offset = (page - 1) * per_page  # Calculate the offset for the current page
    return {
        'pricelist': priceList[offset:offset + per_page],
        'date': Date[offset:offset + per_page],
        'stops': Stops[offset:offset + per_page],
        'seats': numberOfBookableSeats[offset:offset + per_page],
        'cabins': cabin[offset:offset + per_page],
        'pagination': Pagination(page=page, per_page=per_page, total=len(priceList)),
        'page': page,
        'per_page': per_page,
    }
@bp.route('/paging', methods=['GET'])
def paging():
    # Get the page and per_page values from the query parameters (or default to 1 and 10)
    page = int(request.args.get('page', 1))  # Default to page 1
    per_page = int(request.args.get('per_page', 10))  # Default to 10 items per page

    # Call the function to get pagination data, passing page and per_page
    pagination_data = get_pagination_data(page, per_page)

    # Only render pagination if there are more than 15 items
    if len(priceList) <= 15:
        pagination_data['pagination'] = None  # Hide pagination if no need for it
    else:
        # Ensure the next and previous buttons work properly
        if page * per_page >= len(priceList):  # If we're on the last page
            pagination_data['pagination'] = None  # Hide pagination buttons
        else:
            pagination_data['pagination'] = Pagination(page=page, per_page=per_page, total=len(priceList))

    return render_template('Results.html', **pagination_data)


# Route to handle the initial data loading
@bp.route('/', methods=['GET', 'POST'])
def getData():
    try:
        if request.method == "POST":
            date = request.form.get("StartDate")
            start_city = request.form.get("StartCode", "").strip().lower()
            dest_city = request.form.get("DestCode", "").strip().lower()

            # Look up IATA codes based on city names
            start_code = next((entry['iata_code'] for entry in airports_data if entry['city'].lower() == start_city), None)
            dest_code = next((entry['iata_code'] for entry in airports_data if entry['city'].lower() == dest_city), None)

            if not start_code or not dest_code:
                return render_template('NotFound.html', error_message="City not found or not supported. Please check your input.")

            # Call Amadeus API
            response = search_flights(start_code, dest_code, date)

            # Clear previous data before appending new results
            priceList.clear()
            Date.clear()
            Stops.clear()
            numberOfBookableSeats.clear()
            cabin.clear()

            length = len(response.data)

            for x in range(length):
                offer = response.data[x]
                priceList.append(offer['price']['grandTotal'])
                Date.append(offer['lastTicketingDate'])
                Stops.append(str(offer['itineraries'][0]['segments'][0]['numberOfStops']))
                numberOfBookableSeats.append(offer['numberOfBookableSeats'])
                cabin.append(offer['travelerPricings'][0]['fareDetailsBySegment'][0]['cabin'])

            return render_template(
                'Results.html',
                **get_template_data(page=1, per_page=10)  # Return paginated data from the start
            )
        else:
            return render_template('Home.html')

    except ResponseError as error:
        error_message = None
        try:
            error_message = json.loads(error.response.body)['errors'][0]['detail']
        except:
            error_message = str(error)

        return render_template('NotFound.html', error_message=error_message)

@bp.route('/sort/<column>', methods=['POST'])
def sort_column(column):
    # Map each column to the relevant data list
    data_map = {
        'prices': priceList,
        'stops': Stops,
        'date': Date,
        'seats': numberOfBookableSeats,
        'cabin': cabin,
    }

    # Get the data corresponding to the column being sorted
    data = data_map.get(column.lower())

    if data:
        # Check if the sorting should be reversed (toggle sorting order)
        reverse = False
        if request.args.get('reverse') == 'true':
            reverse = True
        
        # Sort the data and return the updated template with sorted data
        sorted_data = get_sorted_data(data, column, reverse)
        
        # Define pagination values
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 15))  # Get the per_page value dynamically
        
        # Get pagination data
        pagination_data = get_pagination_data(page, per_page, sorted_data)
        
        # Return the rendered template with sorted data and pagination
        return render_template(
            'Results.html', 
            **pagination_data
        )

    return "Invalid column", 400


from datetime import datetime
def get_pagination_data(page, per_page, sorted_data=None):
    # If sorted_data is not passed, use the original data
    if not sorted_data:
        sorted_data = {
            'pricelist': priceList,
            'stops': Stops,
            'date': Date,
            'seats': numberOfBookableSeats,
            'cabins': cabin
        }

    # Calculate the offset for the current page
    offset = (page - 1) * per_page

    # Extract the paginated data from sorted_data
    paginated_data = {
        'pricelist': sorted_data['pricelist'][offset:offset + per_page],
        'stops': sorted_data['stops'][offset:offset + per_page],
        'date': sorted_data['date'][offset:offset + per_page],
        'seats': sorted_data['seats'][offset:offset + per_page],
        'cabins': sorted_data['cabins'][offset:offset + per_page]
    }

    # Calculate total items and total pages
    total_items = len(priceList)
    total_pages = (total_items // per_page) + (1 if total_items % per_page != 0 else 0)

    # Create the pagination object only if there are more than one page
    pagination = None
    if total_items > per_page:
        pagination = Pagination(page=page, per_page=per_page, total=total_items)

    return {
        'pricelist': paginated_data['pricelist'],
        'stops': paginated_data['stops'],
        'date': paginated_data['date'],
        'seats': paginated_data['seats'],
        'cabins': paginated_data['cabins'],
        'pagination': pagination,
        'page': page,
        'per_page': per_page
    }



def get_sorted_data(data, column, reverse=False):
    # Combine all data into a single list of tuples
    combined_data = list(zip(priceList, Stops, Date, numberOfBookableSeats, cabin))

    # Determine which column to sort by
    if column == 'prices':
        # Sort by the price column (index 0 of the tuple)
        combined_data.sort(key=lambda x: x[0], reverse=reverse)
    elif column == 'stops':
        # Sort by the stops column (index 1 of the tuple)
        combined_data.sort(key=lambda x: x[1], reverse=reverse)
    elif column == 'date':
        # Sort by the date column (index 2 of the tuple)
        combined_data.sort(key=lambda x: datetime.strptime(x[2], '%Y-%m-%d'), reverse=reverse)
    elif column == 'seats':
        # Sort by the seats column (index 3 of the tuple)
        combined_data.sort(key=lambda x: x[3], reverse=reverse)
    elif column == 'cabin':
        # Sort by the cabin column (index 4 of the tuple)
        combined_data.sort(key=lambda x: x[4], reverse=reverse)

    # Unzip the combined data back into individual lists
    sorted_pricelist, sorted_stops, sorted_date, sorted_seats, sorted_cabins = zip(*combined_data)

    # Return the sorted data in a dictionary
    return {
        'pricelist': list(sorted_pricelist),
        'stops': list(sorted_stops),
        'date': list(sorted_date),
        'seats': list(sorted_seats),
        'cabins': list(sorted_cabins)
    }
