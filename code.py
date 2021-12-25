#!/usr/bin/python
'''
Things I'd like to do with the data.

- Chart the price of the cheapest ticket over time.
- See how many tickets are priced below a certain threshold.
'''

import re, datetime, time, os
import argparse
from selenium import webdriver


URL_LIST_PATH = 'urls.txt'


###########################
# Scraping StubHub
###########################

def getPageSource( url ):
   '''
   Open the URL in Safari. Then fetch and return the page source.
   This is useful when certain sites don't let you easily scrape them using
   cURL or urllib.
   '''
   driver = webdriver.Safari()
   driver.get( url )
   time.sleep( 5 )
   pageSource = driver.page_source
   driver.close()
   return pageSource

def savePageSourceToFile( url, filePath ):
   pageSource = getPageSource( url )
   pageSourceAscii = pageSource.encode( 'ascii', 'ignore' )
   with open( filePath, 'w' ) as f:
      f.write( pageSourceAscii )

def urlToFolderPath( url ):
   m = re.findall(  'https://www.stubhub.com/twice-(.+)-tickets-(.+)/event', url )
   city = m[ 0 ][ 0 ]
   date = m[ 0 ][ 1 ]
   return '%s-%s' % ( date, city )

def scrapeStubHub():
   urlList = []
   with open( URL_LIST_PATH, 'r' ) as f:
      urlList = f.readlines()
   urlList = [ url.strip() for url in urlList ]
   for url in urlList:
      folder = urlToFolderPath( url )
      fileName = "%s.html" % datetime.datetime.today().strftime( '%Y-%m-%d' )
      filePath = '%s/%s' % ( folder, fileName )
      savePageSourceToFile( url, filePath )

###########################
# Scraping StubHub
###########################
def getPriceList( date ):
   '''
   Reads the StubHub site's HTML for the given date,
   and extracts the ticket prices from that date into a list.

   Params:
      date - String of the form "yyyy-mm-dd"

   Returns:
      A list of floats.
   '''
   filename = '%s.html' % date
   with open( filename, 'r' ) as f:
      text = f.read()
   lines = text.split( 'AdvisoryPriceDisplay__content">$' )[ 1:-2 ]
   prices = []
   for line in lines:
      matches = re.findall( "(\d+)</div", line )
      prices.append( int( matches[ 0 ] ) )
   return prices


###########################
# Parsing and analyzing the data
###########################

def getPriceTimeSeries( startDate, endDate, statFunc ):
   '''
   For each date between startDate and endDate inclusive, 
   gather the price data from that date (if it exists).
   Then compute a certain statistic from that price data and build up a time series.

   Params:
      startDate - String of the form "yyyy-mm-dd"
      endDate   - String of the form "yyyy-mm-dd"
      statFunc  - a function that takes in a list of floats 
                 and returns a statistic computed from the floats.

   Returns:
      A list of floats.
   '''
   startDatetime = datetime.datetime.strptime( startDate, '%Y-%m-%d' ) 
   endDatetime = datetime.datetime.strptime( endDate, '%Y-%m-%d' )
   currDatetime = startDatetime
   timeSeries = []
   value = 0
   while currDatetime <= endDatetime:
      currDate = currDatetime.strftime( '%Y-%m-%d' )
      try:
         priceList = getPriceList( currDate )
         value = statFunc( priceList )
      except IOError as e:
         pass
      timeSeries.append( value )         
      currDatetime += datetime.timedelta( days=1 )
   return timeSeries

def getMinPriceTimeSeries( startDate, endDate ):
   return getPriceTimeSeries( startDate, endDate, min )


if __name__ == '__main__':
   parser = argparse.ArgumentParser()
   parser.add_argument( '--scrape', action='store_true' )
   args = parser.parse_args()

   if args.scrape:
      print "Scraping StubHub..."
      scrapeStubHub()
   
   startDate = '2021-12-25'
   endDate = datetime.datetime.today().strftime( '%Y-%m-%d' )

   directoryContents = os.listdir( '.' )
   subdirectories = [ d for d in directoryContents if os.path.isdir( d ) ]
   for directory in subdirectories:
      os.chdir( directory )
      print "*** %s ***" % directory
      print getMinPriceTimeSeries( startDate, endDate )
      print 
      os.chdir( '..' )
