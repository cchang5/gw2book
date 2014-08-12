#Keeps track of trading post
import yaml, urllib2, json
import numpy as np
import locale, sys
locale.setlocale(locale.LC_NUMERIC, "")

############################################################################
#Copied directly from https://github.com/tynril/pygw2spidy
class Gw2Spidy:
    """This utility class allows easy access to the GW2Spidy data."""
    headers = {'User-Agent': 'gw2spidy.py'}
    @staticmethod
    def getItemData(itemId):
        """Get the data of a particular item. High frequency of update."""
        return Gw2Spidy._request('item', str(itemId))['result']
    @staticmethod
    def _request(*args):
        """Makes a request on the GW2Spidy API."""
        url = 'http://www.gw2spidy.com/api/v0.9/json/' + '/'.join(args)
	r = urllib2.Request(url, headers=Gw2Spidy.headers)
	if 'Cookie' not in Gw2Spidy.headers:
	    resp = urllib2.urlopen(r)
	    if 'set-cookie' in resp.headers:
		Gw2Spidy.headers['Cookie'] = resp.headers['set-cookie'].split(';', 1)[0]
	    return json.loads(resp.read())
        return json.loads(urllib2.urlopen(r).read())
############################################################################
#Taxes
def taxes(sell_price):
	return sell_price*0.85
############################################################################
#Pretty tables
def format_num(num):
    """Format a number according to given places.
    Adds commas, etc. Will truncate floats into ints!"""
    try:
        inum = int(num)
        return locale.format("%.*f", (0, inum), True)

    except (ValueError, TypeError):
        return str(num)
def get_max_width(table, index):
    """Get the maximum width of the given column index"""
    return max([len(format_num(row[index])) for row in table])
def pprint_table(out, table):
    """Prints out a table of data, padded for alignment
    @param out: Output stream (file-like object)
    @param table: The table to print. A list of lists.
    Each row must have the same number of columns. """
    col_paddings = []

    for i in range(len(table[0])):
        col_paddings.append(get_max_width(table, i))

    for row in table:
        # left col
        print >> out, row[0].ljust(col_paddings[0] + 1),
        # rest of the cols
        for i in range(1, len(row)):
            col = format_num(row[i]).rjust(col_paddings[i] + 2)
            print >> out, col,
        print >> out
##############################################################################
#int to gold
def int2gold(num):
	num = int(num)
	copper = num%100
	num = num/100
	silver = num%100
	num = num/100
	gold = num
	return str(gold)+'g '+str(silver)+'s '+str(copper)+'c'
##############################################################################

#Link to trans.yml
libpath = './book.yml'

file = open(libpath,'r')
buylist=yaml.load(file)
file.flush()
file.close()

itemlist = buylist.keys()
gw = Gw2Spidy()
table = [['ITEM', 'BUY_PRICE', 'MIN_SALE', 'PROFIT(POST-TAX)', 'MAX_OFFER', 'PROFIT(POST-TAX)']]
total_sale=0
total_offer=0
for item in itemlist:
	get_item = gw.getItemData(item)
	name = get_item['name']
	min_sale = get_item['min_sale_unit_price']
	max_offer = get_item['max_offer_unit_price']
	buy_price = buylist[item]['buy']
	sale_profit = taxes(min_sale)-buy_price
	offer_profit = taxes(max_offer)-buy_price
	total_sale+=sale_profit
	total_offer+=offer_profit
	buy_price = int2gold(buy_price)
	min_sale = int2gold(min_sale)
	sale_profit = int2gold(sale_profit)
	max_offer = int2gold(max_offer)
	offer_profit = int2gold(offer_profit)
	table.append([name, buy_price, min_sale, sale_profit, max_offer, offer_profit])
table.append(['TOTAL_PROFIT', 'N/A', 'N/A', int2gold(total_sale), 'N/A', int2gold(total_offer)])
out = sys.stdout
pprint_table(out, table)

