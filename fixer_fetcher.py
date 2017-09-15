#!/usr/bin/python

#script that populate the data with the data from fixer.io from the last year.
# https://pypi.python.org/pypi/fixerio/0.1.1 >> Nice Dependency

from datetime import date, datetime, timedelta
import sqlite3
import sys, time
import requests

base_url = 'http://api.fixer.io/'
conn = sqlite3.connect('currencies.db')


#function to provide daily exchange rates, parameter = dateformat 'YYY-MM-DD'
def get_daily_rate(date):
    query = base_url + str(date)
    try:
        response = requests.get(query)
        #print("[%s] %s" % (response.status_code, response.url))
        if response.status_code == 429:
            print ("API Error 429 - Too Many Requests.. waiting to proceed")
            time.sleep(5)
            return None, None
        elif response.status_code != 200:
            print ("Something Wrong : " + str(response) )
            return None, None
        else:
            rates = response.json()
            timestamp = datetime.strptime(rates["date"], "%Y-%m-%d").timestamp()
            daily_rates = rates["rates"]
            daily_rates.update({'EUR' : 1.00 } )
            return timestamp, daily_rates
    except requests.ConnectionError as error:
        print (error)
        return None, None

#Create our DB table for the first time
def create_DB_Table():
    c = conn.cursor()
    try:
        c.execute('''
        CREATE TABLE exchangeRates 
        (TIMESTAMP DATETIME PRIMARY KEY,
        BASECURRENCY TEXT,
        RATES TEXT
        )
        ''')
    except sqlite3.OperationalError as Error:
        print ("Table already exists")
        return
    else:
        conn.commit()

#Refresh table if necessary
def drop_DB_Table():
    c = conn.cursor()
    try:
        c.execute('''DROP TABLE exchangeRates ''')
    except sqlite3.OperationalError:
        #No Db exists yet
        pass
    conn.commit()

#Save daily rates in database
def save_Daily_Rate(timestamp, rates):
    c = conn.cursor()
    # Create table
    try : 
        c.execute("""INSERT INTO exchangeRates (TIMESTAMP, BASECURRENCY, RATES) VALUES (?, 'EUR', ?)""", (timestamp, str(rates)))
    except sqlite3.IntegrityError :
        pass

def main():
    drop_DB_Table()
    create_DB_Table()

    #Get data for full year of 2016
    initial_date = date(2016, 1, 1)
    final_date = date(2016, 12, 31)
    diff = final_date-initial_date

    for i in range(diff.days + 1):
        day_date = initial_date + timedelta(days=i)
        time, rates = get_daily_rate(day_date)
        if time is None :
            time, rates = get_daily_rate(day_date)
        save_Daily_Rate(time, rates)

    conn.commit()

if __name__ == '__main__':
    main()
