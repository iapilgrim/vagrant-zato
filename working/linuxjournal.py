# -*- coding: utf-8 -*-

# stdlib
from datetime import datetime

# dateutil
from dateutil.parser import parse

# lxml
from lxml import etree

# Zato
from zato.common.util import grouper
from zato.server.service import Service

# Interesting namespaces treasury.gov uses for rates
NAMESPACES = {
    'd':'http://schemas.microsoft.com/ado/2007/08/dataservices',
    'm':'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata'
}

# Pattern for a Redis key to store the data under
REDIS_KEY_PATTERN = 'linuxjournal:rates:{}:{}:{}'

def get_date(input):
    now = datetime.utcnow()
    
    year = input.get('year') or now.year
    month = input.get('month') or now.month
    day = input.get('day') or now.day
    
    return year, month, day

# ##############################################################################

class UpdateCache(Service):
    """ Fetches complex XML from treasury.gov and updates the application's Redis cache.
    """
    class SimpleIO:
        input_optional = ('year', 'month')

    def handle(self):
        
        # Grab month and year from user-provided input or use defaults, i.e. current date,
        # note that day is not needed so it's discarded 
        year, month, _ = get_date(self.request.input)
        
        # Fetch connection by its name
        out = self.outgoing.plain_http.get('treasury.gov')
        
        # Build a query string the backend data source expects
        query_string = {
            '$filter': 'month(QUOTE_DATE) eq {} and year(QUOTE_DATE) eq {}'.format(month, year)
        }
        
        # Invoke the backend with query string, fetch the response as a UTF-8 string
        # and turn it into an XML object
        response = out.conn.get(self.cid, query_string)
        response = response.text.encode('utf-8')
        xml = etree.fromstring(response)
        
        # Look up all XML elements needed (date and rate) using XPath
        elements = xml.xpath('//m:properties/d:*/text()', namespaces=NAMESPACES)
        
        # elements is a flat list that needs to be turned into pairs using the 'grouper'
        # function before iterating over
        elements = grouper(2, elements)
        
        for date, rate in elements:
            
            # Create a date object out of string
            date = parse(date)
            
            # Build a key for Redis and store the data under it
            key = REDIS_KEY_PATTERN.format(date.year, str(date.month).zfill(2), str(date.day).zfill(2))
            self.logger.info("redis key : %s"%key)
            self.kvdb.conn.set(key, rate)
            
            # Leave a trace of our activity
            self.logger.info('Key %s set to %s', key, rate)
        
# ##############################################################################

class GetRate(Service):
    """ Returns the real long-term rate for a given date (defaults to today if no date is given).
    """
    class SimpleIO:
        input_optional = ('year', 'month', 'day')
        output_optional = ('rate',)
        
    def handle(self):
        # Get date needed either from input or current day
        year, month, day = get_date(self.request.input)
        
        # Build the key the data is cached under
        key = REDIS_KEY_PATTERN.format(year, month, day)
        
        # Assign the result from cache directly to response
        self.response.payload.rate = self.kvdb.conn.get(key)
        
# ##############################################################################