## **Flight Search App with Python-Flask**
It is an app that displays flights based on the user's selected **country code** and **dates**. The user has the possibility to retrieve all the codes of each country in order to search for the flight he wants.
The project is built with the **Flask Framework** and every time the user searches for a flight, the application makes API calls to Amadeus to pull the appropriate information.

## **Run app**
To run the application on Windows, you need to execute the following commands: 
* installation of all necessary libraries
```python -m venv venv```
```source venv/bin/activate   # On Windows, use `venv\Scripts\activate` ```
```pip install -r requirements.txt```
* running application 
```python Flask.py``` 
* open the following address in the browser 
http://127.0.0.1:5000/

