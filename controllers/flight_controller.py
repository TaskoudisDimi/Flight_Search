from flask import Blueprint, request, jsonify, render_template
from services.flight_service import search_flights
from amadeus import Client, ResponseError
import json
from flask_paginate import Pagination, get_page_parameter,get_page_args
import logging

bp = Blueprint('flight_controller', __name__)


priceList = []
AirCodes = []
Date = []
Stops = []
numberOfBookableSeats = []
cabin = []

ShowPrice = True
ShowCode = True
ShowStops = True
ShowDate = True

ShowMoreColumns = True

# Load the JSON data once when the app starts
with open('countries.json', 'r') as json_file:
    data = json.load(json_file)

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

#Route basic HTMLs
@bp.route('/getCountryCodes', methods=['GET', 'POST'])
def getCountryCodes():
    search_term = request.form.get('search_term', '')

    # Filter the data based on the search term
    filtered_data = [entry for entry in data if search_term.lower() in entry['country_name'].lower()]

    return render_template('CountryCodes.html', data=filtered_data, search_term=search_term)

    


# Display Data Region
@bp.route('/', methods=['GET', 'POST'])
def getData():
    try:
        if request.method == "POST":
            Start_Code = request.form.get("StartCode")
            date = request.form.get("StartDate")  
            Dest_Code = request.form.get("DestCode")
           
            response = search_flights(Start_Code, Dest_Code, date)
            print("Response from API:", response)
            
            length = len(response.data)
            print("length of data is : " + str(length))
           
            for x in range(0,length):
                priceList.bpend(response.data[int(x)]['price']['grandTotal'])
                AirCodes.bpend(response.data[int(x)]['validatingAirlineCodes'])
                Date.bpend(response.data[int(x)]['lastTicketingDate'])
                Stops.bpend(str(response.data[int(x)]['itineraries'][0]['segments'][0]['numberOfStops']))
                numberOfBookableSeats.bpend(response.data[0]['numberOfBookableSeats'])
                cabin.bpend(response.data[0]['travelerPricings'][0]['fareDetailsBySegment'][0]['cabin'])
            
            return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
        else:
            return render_template('Home.html')
    except ResponseError as error:
        error_message = None
        try:
            error_message = json.loads(error.response.body)['errors'][0]['detail']
        except:
            error_message = str(error)

        print("Error from API:", error_message)  # Optional: debug log
        return render_template('NotFound.html', error_message=error_message)



        

#PAGING
def get_paging_prices(offset, per_page):
    return priceList[offset:offset + per_page]

def get_paging_airCodes(offset, per_page):
    return AirCodes[offset:offset + per_page]

def get_paging_Date(offset, per_page):
    return Date[offset:offset + per_page]

def get_paging_Stops(offset, per_page):
    return Stops[offset:offset + per_page]

def get_paging_Cabin(offset, per_page):
    return cabin[offset:offset + per_page]

def get_paging_Seats(offset, per_page):
    return numberOfBookableSeats[offset:offset + per_page]

@bp.route('/paging', methods=['GET', 'POST'])
def paging():
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    
    total = len(priceList)
    pagination = Pagination(page=page, per_page=per_page, total=total)
    pagination_prices = get_paging_prices(offset=offset, per_page=20)
    pagination_airCodes = get_paging_airCodes(offset=offset, per_page=20)
    pagination_Date = get_paging_Date(offset=offset, per_page=20)
    pagination_Stops = get_paging_Stops(offset=offset, per_page=20)
    pagination_Cabin = get_paging_Cabin(offset=offset, per_page=20)
    pagination_Seats = get_paging_Seats(offset=offset, per_page=20)
    if(ShowMoreColumns):
        return render_template('Results.html', pricelist=pagination_prices, airCodes=pagination_airCodes , date = pagination_Date, stops = pagination_Stops, page=page, per_page=per_page, pagination=pagination,seats = pagination_Seats, cabins= pagination_Cabin, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = True)
    else:
        return render_template('Results.html', pricelist=pagination_prices, airCodes=pagination_airCodes , date = pagination_Date, stops = pagination_Stops, page=page, per_page=per_page, pagination=pagination,seats = 0, cabins= 0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = False)



#Sort Region
@bp.route('/sortPrices', methods=['GET', 'POST'])
def sortPrices():
    try:
        sort = sorted(priceList)
        return render_template('Results.html', pricelist = sort, airCodes = AirCodes, date = Date, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)

@bp.route('/sortDate', methods=['GET', 'POST'])
def sortDate():
    try:
        sort = sorted(Date)
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = sort, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)

@bp.route('/sortCodes', methods=['GET', 'POST'])
def sortCodes():
    try:
        sort = sorted(AirCodes)
        return render_template('Results.html', pricelist = priceList, airCodes = sort, date = Date, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)

@bp.route('/sortStops', methods=['GET', 'POST'])
def sortStops():
    try:
        sort = sorted(Stops)
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date, stops = sort,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)

@bp.route('/sortSeats', methods=['GET', 'POST'])
def sortSeats():
    try:
        sort = sorted(numberOfBookableSeats)
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date, stops = Stops, seats = sort, cabins= cabin,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = True)
    except ResponseError as error:
        print(error)

@bp.route('/sortCabin', methods=['GET', 'POST'])
def sortCabin():
    try:
        sort = sorted(cabin)
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date, stops = Stops, seats = numberOfBookableSeats, cabins= sort,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = True)
    except ResponseError as error:
        print(error)



#More/Some DATA
@bp.route('/allData', methods=['GET', 'POST'])
def allData():
    try:
        ShowMoreColumns = True
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date, stops = Stops, seats = numberOfBookableSeats, cabins= cabin,pagination=0,page=0,per_page=0,ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True, ShowMoreColumns = True)
    except ResponseError as error:
        print(error)

@bp.route('/someData', methods=['GET', 'POST'])
def someData():
    try:
        ShowMoreColumns = False
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True, ShowMoreColumns = False)
    except ResponseError as error:
        print(error)


#HIDE COLUMNS
@bp.route('/hidePrices', methods=['GET', 'POST'])
def HidePrices():
    try:
        return render_template('Results.html', airCodes = AirCodes, date = Date, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = False, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)

@bp.route('/HideCodes', methods=['GET', 'POST'])
def HideCodes():
    try:
        return render_template('Results.html', pricelist = priceList, date = Date, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = False, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)

@bp.route('/HideStops', methods=['GET', 'POST'])
def HideStops():
    try:
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = False,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)


@bp.route('/HideDate', methods=['GET', 'POST'])
def HideDate():
    try:
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = False, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)


#SHOW COLUMNS
@bp.route('/showPrices', methods=['GET', 'POST'])
def showPrices():
    try:
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)

@bp.route('/showCode', methods=['GET', 'POST'])
def showCode():
    try:
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)

@bp.route('/showDate', methods=['GET', 'POST'])
def showDate():
    try:
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)

@bp.route('/showStops', methods=['GET', 'POST'])
def showStops():
    try:
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)


