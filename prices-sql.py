# Web scraping zinc price and us/eur currency from their
# respective websites and save them to .sql query file. 
# Author      : Bairaktaris Emmanuel
# Date        : November 26, 2019
# Last version: October 27, 2020
# Link        : http://repairmypc.net

# Import libraries
from datetime import date
import holidays
import requests
from bs4 import BeautifulSoup
import uuid
import datetime
import time
import os

# Get yesterday date
today = datetime.date.today()
mydate = today - datetime.timedelta(days = 1)
mm = mydate.strftime("%d %B %Y")

# Delete sql file before create the new one
# endor
if os.path.exists('C:/tools/zinc/data/export_zinc_prices.sql'):
  os.remove('C:/tools/zinc/data/export_zinc_prices.sql')
  print('File deleted')
else:
  print('File does not exist')
time.sleep(5)

# Check for public day of zinc prices
in_holidays = holidays.HolidayBase()

# append custom dates to holiday
in_holidays.append(['10-04-2020', '13-04-2020', '08-05-2020', '25-05-2020', '31-08-2020', '25-12-2020', '28-12-2020']) 

# check condition and run script or stop script
if mydate.strftime('%d-%m-%Y') in in_holidays:
    print('it is holidays date :)')
    quit()
else:
    # Get the headers
    headers = { 
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:82.0) Gecko/20100101 Firefox/82.0', 
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
    'Accept-Language' : 'en-US,en;q=0.5', 
    'Accept-Encoding' : 'gzip', 
    'DNT' : '1', # Do Not Track Request Header 
    'Connection' : 'close' }
    
    # Get the links to be scraped
    zinc = requests.get('https://www.lme.com', headers=headers)
    xchange = requests.get('https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/eurofxref-graph-usd.en.html', headers=headers)

    # Declare scrape type for each website with BeautifulSoup
    soup_zinc = BeautifulSoup(zinc.content, 'html.parser')
    soup_xchange = BeautifulSoup(xchange.text, 'html.parser')

    # Extract the zinc price from the table element
    zincdollar = soup_zinc.select_one('th:contains("LME Zinc") + td').text.strip()
    print(zincdollar)
    # Extraxt text of currency price
    currencyxchange = soup_xchange.find(class_='stats-table-points').get_text()
    print(currencyxchange)
    # Extract webpage date
    lmeDate = soup_zinc.select_one('th').text.strip()
    print("Date shown from website  : " + lmeDate)

    # Convert string to floats  
    lastdollar = float(zincdollar.replace(',',''))
    exchangerate = float(currencyxchange)
    lasteuro = float(lastdollar) /float(exchangerate) # Division of dollar zinc price by currency to get zinc price in euros
    print(lasteuro)

    if(lmeDate == mm):
        print("Date is same from website")
        # Create file with entries into .sql statement format insert query
        f = open('C:/tools/zinc/data/' + str(datetime.date.today()) + '_export_zinc_prices_' + str(uuid.uuid1()) + '.sql', 'w') # the file name contains the current date of execution and unique id number(uuid)
        f.write('Insert into metal (lastdollar, lasteuro, mydate, exchangerate) VALUES (' + str(lastdollar) + ', ' + str('%.4f' %lasteuro) + ', ' + '\'' + str(mydate) + '\'' + ' ,' +  str(exchangerate) + ')')
        f.close()
        # Create a file with all prices
        f = open('C:/tools/zinc/data/export_zinc_prices_all.sql', 'a')
        f.write('Insert into metal (lastdollar, lasteuro, mydate, exchangerate) VALUES (' + str(lastdollar) + ', ' + str('%.4f' %lasteuro) + ', ' + '\'' + str(mydate) + '\'' + ' ,' +  str(exchangerate) + ')' + '\n')
        f.close()
        # Create a file with prices to be inserted with sqlcecmd command script
        f = open('C:/tools/zinc/data/export_zinc_prices.sql', 'w')
        f.write('Insert into metal (lastdollar, lasteuro, mydate, exchangerate) VALUES (' + str(lastdollar) + ', ' + str('%.4f' %lasteuro) + ', ' + '\'' + str(mydate) + '\'' + ' ,' +  str(exchangerate) + ')')
        f.close()
    else:
        print("Date is different from website")
