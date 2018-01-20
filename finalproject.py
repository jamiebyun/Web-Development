import urllib, urllib2, json, webapp2, jinja2, os,logging

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'], autoescape=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        # logging.info("In MainHandler")
        template_values = {}
        template_values['page_title'] = "Real time stock price checker!"
        template = JINJA_ENVIRONMENT.get_template('stock.html')
        self.response.write(template.render(template_values))


def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def safeGet(url):
    try:
        return urllib2.urlopen(url)
    except urllib2.HTTPError as e:
        print("The server couldn't fulfill the request.")
        print("Error code: ", e.code)
    except urllib2.HTTPError as e:
        print("We failed to reach a server")
        print("Reason: ", e.reason)
        return None

def stockREST(symbol):
    baseurl='https://www.alphavantage.co/query?'
    function='TIME_SERIES_DAILY'
    api_key='JIK548KD6K5HRL55'
    params = {}
    params['function'] = function
    params['apikey'] = api_key
    #Please get your api key for testing at https://www.alphavantage.co/support/#api-key
    params['symbol'] = symbol
    url = baseurl + urllib.urlencode(params)
    print("Call made: " + url)
    return safeGet(url)

def getStock(symbol):
    result = stockREST(symbol)
    jsonresult = result.read()
    #logging.info(jsonresult)
    data = json.loads(jsonresult)
    if "Error Message" in data.keys():
      print("ERROR with symbol " + symbol + ": " + data["Error Message"])
      exit()
    return data

def getStockBySymbolAndDate(symbol, date):
    # print("Stock price for " + symbol + " on " + date)
    data = getStock(symbol)
    # print(data)
    if date not in data["Time Series (Daily)"].keys():
        print("Invalid date: " + date + ". Please choose one of these dates: " + str(data["Time Series (Daily)"].keys()))
        exit()
    result = data["Time Series (Daily)"][date]
    return result


class SearchOuputHandlr(webapp2.RequestHandler):
    def post(self):
        vals={}
        vals['page_title']="Stock App - Real Time Stock Checker "
        name = self.request.get('company')
        date = self.request.get('date')
        go = self.request.get('gobtn')
        logging.info(name)
        logging.info(go)
        logging.info(date)
        try:
            result = getStockBySymbolAndDate(name, date)
            high = result["2. high"]
            open = result["1. open"]
            low = result["3. low"]
            close = result["4. close"]
            volume = result["5. volume"]
            vals["highprice"] = high
            vals["openprice"] = open
            vals["lowprice"] = low
            vals["closeprice"] = close
            vals["volume"] = volume
            vals["company"] = name
            vals["date"] = date
            template = JINJA_ENVIRONMENT.get_template('stockoutput.html')
            self.response.write(template.render(vals))
        except:
            vals["prompt"] = "* Type in a right format ex) MICROSOFT -> MSFT & DATE -> 2017-12-10 *"
            template = JINJA_ENVIRONMENT.get_template('stock.html')
            self.response.write(template.render(vals))


def getStockBySymbolsAndDates(symbols, dates):
    print("Stock price for " + str(symbols) + " on " + str(dates))
    result = {}
    for symbol in symbols:
        result[symbol] = {}
        data = getStock(symbol)
        for date in dates:
            result[symbol][date] = data["Time Series (Daily)"][date]["4. close"]
    return result


class SearchTwoOuputHandlr(webapp2.RequestHandler):
    def post(self):
        vals={}
        vals['page_title']="Stock App - Check the price"
        nameOne = self.request.get('company1')
        nameTwo= self.request.get('company2')
        nameThree = self.request.get('company3')
        companies = [nameOne, nameTwo, nameThree]
        date = self.request.get('date')
        button = self.request.get('gobtn')
        logging.info(nameOne)
        logging.info(nameTwo)
        logging.info(nameThree)
        logging.info(button)
        logging.info(date)
        try:
            logging.info("in the try block")
            outcome = getStockBySymbolsAndDates(companies, [date])
            vals["comparison"] = outcome
            logging.info(vals["comparison"])
            template = JINJA_ENVIRONMENT.get_template('stocktwo.html')
            self.response.write(template.render(vals))
        except:
            logging.info("in the except block")
            vals["prompt"] = "SEARCH ERROR: Type in a right format ex) MICROSOFT -> MSFT & DATE -> 2017-12-10 *"
            template = JINJA_ENVIRONMENT.get_template('stock.html')
            self.response.write(template.render(vals))

application = webapp2.WSGIApplication([ \
    ('/stock', SearchOuputHandlr),
    ('/stocktwo', SearchTwoOuputHandlr),
    ('/.*', MainHandler)
],
    debug=True)