

"""

Script to prep for brewvival.com!

"""

# BAscore_big 1 = BA Score
# BAscore_big 2 = BA Score
from pattern.web import *
import feedparser, random, xlwt, xlrd
from pattern.web import *
from xlutils.copy import copy

def getRssData():
	req = feedparser.parse(URL('http://brewvival.com/beer/rss').download())
	entries = req.entries
	beers = []
	for entry in entries:
		beer = {
			'brewery' : None,
			'title' : None,
			'description' : None,
			'style' : None,
			'abv' : None,
			'location' : None,
			'website' : None,
			'ratebeer' : None,
			'ba' : None
		}
		values = []
		beerLinks = []
		for item in DOM(entry['summary']).by_class('*.odd'):
			el = Element(item.source).by_tag('div')[0].content
			values.append(str(plaintext(el).encode('ascii','replace')).split('\n'))
			for val in item.by_tag('a'):
				beerLinks.append(val.attributes['href'])
		beer['title'] = entry['title']
		beer['brewery'] = values[0][0]
		beer['description'] = values[1][0]
		beer['style'] = values[2][2]
		beer['abv'] = values[3][2]
		try:
			beer['location'] = values[4][2]
			beer['website'] = values[5][2]
			beer['ba'] = beerLinks[1]
			beer['ratebeer'] = beerLinks[2]
		except Exception,e:
			pass
			#print values[3:],beerLinks
		beers.append(beer)


	workbook = xlwt.Workbook()
	beerSheet = workbook.add_sheet('beers')

	titles = ["Title", "Brewery", "Style", "ABV", "Location", "Ratebeer", "BeerAdvocate", "Description", "Website"]
	column = 0
	for title in titles:
		beerSheet.write(0,column,title)
		column += 1

	row, column = 1,0
	for beer in beers:
		beerSheet.write(row,0,beer['title'])
		beerSheet.write(row,1,beer['brewery'])
		beerSheet.write(row,2,beer['style'])
		beerSheet.write(row,3,beer['abv'])
		beerSheet.write(row,4,beer['location'])
		beerSheet.write(row,5,beer['ratebeer'])
		beerSheet.write(row,6,beer['ba'])
		beerSheet.write(row,7,beer['description'])
		beerSheet.write(row,8,beer['website'])
		row +=1

	workbook.save('test.xls')


def getBeerReviews():

	workbook = xlrd.open_workbook('test.xls')

	beerSheet = workbook.sheet_by_name('beers')

	baDict = { }
	ratebeerDict = {}

	wb = xlwt.Workbook()
	beerSheet2 = wb.add_sheet('beers')

	for rowIndex in range(1,beerSheet.nrows-1):
		row =  beerSheet.row(rowIndex)
		ratebeer = beerSheet.cell_value(rowIndex,10)
		ba = beerSheet.cell_value(rowIndex,11)
		if ratebeer:
			try:
				ratebeerDom = DOM(URL(str(ratebeer)).download()).by_attribute(style="background-color: #036; width: 130px;")[0].content
				items =  str(plaintext(ratebeerDom)).split('\n')
				overall = items[1].split(' ')[0]
				style = items[1].split(' ')[1]
				beerSheet2.write(rowIndex,7,overall)
				beerSheet2.write(rowIndex,8,style)
			except:
				pass
		if ba:
			try:
				baDom = DOM(URL(str(ba)).download()).by_class('BAscore_big')
				baDict[ba] = (baDom[0].content, baDom[1].content)
				beerSheet2.write(rowIndex,5,baDom[0].content)
				beerSheet2.write(rowIndex,5,baDom[1].content)
			except:
				pass
	wb.save('test1.xls')

if __name__ == '__main__':
	getBeerReviews()





