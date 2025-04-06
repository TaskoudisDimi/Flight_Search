from flask import Flask, render_template, request
from amadeus import Client, ResponseError
import logging
from flask_paginate import Pagination, get_page_parameter,get_page_args
import json

app = Flask(__name__)

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

app = Flask(__name__, template_folder='templates')


#Route basic HTMLs
@app.route('/Home', methods=['GET', 'POST'])
def home():
    return render_template('Home.html') 

@app.route('/Project', methods=['GET', 'POST'])
def project():
    return render_template('Main.html') 

@app.route('/Student', methods=['GET', 'POST'])
def student():
    return render_template('Student_Details.html') 

#Route basic HTMLs
@app.route('/getCountryCodes', methods=['GET', 'POST'])
def getCountryCodes():
    search_term = request.form.get('search_term', '')

    # Filter the data based on the search term
    filtered_data = [entry for entry in data if search_term.lower() in entry['country_name'].lower()]

    return render_template('CountryCodes.html', data=filtered_data, search_term=search_term)

    


# Display Data Region
@app.route('/', methods=['GET', 'POST'])
def getData():
    try:
        if request.method == "POST":
            Start_Code = request.form.get("StartCode")
            date = request.form.get("StartDate")  
            Dest_Code = request.form.get("DestCode")
            
            amadeus = Client(
            client_id='miTq9txNAlSY1q68fGwDP8E5bFQ8OPVo', 
            client_secret='QN6hvjLj2KVFfkUG',
            log_level=logging.INFO)
            response = amadeus.shopping.flight_offers_search.get(originLocationCode=Start_Code, destinationLocationCode=Dest_Code, departureDate=date, adults=1)

            length = len(response.data)
            print("length of data is : " + str(length))
           
            for x in range(0, length):
                priceList.append(response.data[int(x)]['price']['grandTotal'])
                AirCodes.append(response.data[int(x)]['validatingAirlineCodes'])
                Date.append(response.data[int(x)]['lastTicketingDate'])
                Stops.append(str(response.data[int(x)]['itineraries'][0]['segments'][0]['numberOfStops']))
                numberOfBookableSeats.append(response.data[x]['numberOfBookableSeats'])
                cabin.append(response.data[x]['travelerPricings'][0]['fareDetailsBySegment'][0]['cabin'])

            
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

@app.route('/paging', methods=['GET', 'POST'])
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

    # Assuming these variables are set based on some conditions in your application
    ShowPrice = True
    ShowCode = True
    ShowDate = True
    ShowStops = True
    ShowMoreColumns = True

    if ShowMoreColumns:
        return render_template('Results.html', pricelist=pagination_prices, airCodes=pagination_airCodes,
                               date=pagination_Date, stops=pagination_Stops, page=page, per_page=per_page,
                               pagination=pagination, seats=pagination_Seats, cabins=pagination_Cabin,
                               ShowPrice=ShowPrice, ShowCode=ShowCode, ShowDate=ShowDate, ShowStops=ShowStops,
                               ShowMoreColumns=ShowMoreColumns)
    else:
        return render_template('Results.html', pricelist=pagination_prices, airCodes=pagination_airCodes,
                               date=pagination_Date, stops=pagination_Stops, page=page, per_page=per_page,
                               pagination=pagination, seats=0, cabins=0, ShowPrice=ShowPrice, ShowCode=ShowCode,
                               ShowDate=ShowDate, ShowStops=ShowStops, ShowMoreColumns=ShowMoreColumns)


#Sort Region
@app.route('/sortPrices', methods=['GET', 'POST'])
def sortPrices():
    try:
        sort = sorted(priceList)
        return render_template('Results.html', pricelist = sort, airCodes = AirCodes, date = Date, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)

@app.route('/sortDate', methods=['GET', 'POST'])
def sortDate():
    try:
        sort = sorted(Date)
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = sort, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)

@app.route('/sortCodes', methods=['GET', 'POST'])
def sortCodes():
    try:
        sort = sorted(AirCodes)
        return render_template('Results.html', pricelist = priceList, airCodes = sort, date = Date, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)

@app.route('/sortStops', methods=['GET', 'POST'])
def sortStops():
    try:
        sort = sorted(Stops)
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date, stops = sort,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)

@app.route('/sortSeats', methods=['GET', 'POST'])
def sortSeats():
    try:
        sort = sorted(numberOfBookableSeats)
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date, stops = Stops, seats = sort, cabins= cabin,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = True)
    except ResponseError as error:
        print(error)

@app.route('/sortCabin', methods=['GET', 'POST'])
def sortCabin():
    try:
        sort = sorted(cabin)
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date, stops = Stops, seats = numberOfBookableSeats, cabins= sort,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = True)
    except ResponseError as error:
        print(error)



#More/Some DATA
@app.route('/allData', methods=['GET', 'POST'])
def allData():
    try:
        ShowMoreColumns = True
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date, stops = Stops, seats = numberOfBookableSeats, cabins= cabin,pagination=0,page=0,per_page=0,ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True, ShowMoreColumns = True)
    except ResponseError as error:
        print(error)

@app.route('/someData', methods=['GET', 'POST'])
def someData():
    try:
        ShowMoreColumns = False
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True, ShowMoreColumns = False)
    except ResponseError as error:
        print(error)


#HIDE COLUMNS
@app.route('/hidePrices', methods=['GET', 'POST'])
def HidePrices():
    try:
        return render_template('Results.html', airCodes = AirCodes, date = Date, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = False, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)

@app.route('/HideCodes', methods=['GET', 'POST'])
def HideCodes():
    try:
        return render_template('Results.html', pricelist = priceList, date = Date, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = False, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)

@app.route('/HideStops', methods=['GET', 'POST'])
def HideStops():
    try:
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = False,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)


@app.route('/HideDate', methods=['GET', 'POST'])
def HideDate():
    try:
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = False, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)


#SHOW COLUMNS
@app.route('/showPrices', methods=['GET', 'POST'])
def showPrices():
    try:
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)

@app.route('/showCode', methods=['GET', 'POST'])
def showCode():
    try:
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)

@app.route('/showDate', methods=['GET', 'POST'])
def showDate():
    try:
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)

@app.route('/showStops', methods=['GET', 'POST'])
def showStops():
    try:
        return render_template('Results.html', pricelist = priceList, airCodes = AirCodes, date = Date, stops = Stops,pagination=0,page=0,per_page=0, ShowPrice = True, ShowCode = True, ShowDate = True, ShowStops = True,ShowMoreColumns = False)
    except ResponseError as error:
        print(error)





if __name__ == '__main__':
   app.run(debug=True)

