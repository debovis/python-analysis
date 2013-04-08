from pymongo import Connection
from pattern.web import URL, Node, Element, DOM, plaintext


class scrape():

	def __init__(self):
		self.conn = Connection()['citypaper']
		self.xmlUrl = "URL here"


	def getResturants(self):
		# get all resturants and urls
		for page in range(1,48):
			params["page"] = page
			request = DOM(URL(url, query=params).download())
			searchResults = request.by_id('searchResults')
			pageResults = searchResults.by_class('locationListing clearfix')
			for item in pageResults:
				link = item.by_tag('h4')[0].by_tag('a')[-1]
				name = plaintext(link.content)
				address = link.attributes['href']
				resturant = { 'name' : name, 'url' : address}
				conn['resturants'].insert(resturant)

	def getTextAboutResturants(self):
		# get text about resturants
		i=0
		for rs in self.conn.resturants.find():
			if not rs.get('information'):
				information = {}
				request = DOM(URL(rs['url']).download())
				# Tags
				if request.by_id('LocationMetaData'):
					source = str(request.by_id('LocationMetaData').source.encode('cp1252', 'ignore'))
					tags = Element(source[source.find('<b>Tags: </b>'):]).by_tag('a')
					if tags:
						information['parsedTags'] = [ (tag.attributes['href'], tag.content) for tag in tags]
				# Review 
				if request.by_id('LocationDescription'):
					information["review"] = plaintext(request.by_id('LocationDescription').content)
				# Details
				if request.by_id('LocationRestaurantDetails'):
					information["details"] = request.by_id('LocationRestaurantDetails').by_tag('p')[0].content
				rs['details'] = information
				print information
				self.conn.resturants.save(rs)
			else:
				print i, rs['name']

			i +=1

	def getReviews(self):
		params = {
			'id' : "comments",
			'oid' : 0,
			'showAll' : 'yes'
		}
		reviews = []

		i=0
		for rs in self.conn.resturants.find():
			reviews = []
			if not rs.get('reviews'):
				oid = str(rs['url']).split('=')[1]
				params['oid'] = oid
				req = DOM(URL(self.xmlUrl, query=params).download())
				for item in req.by_tag('item'):
					if item.by_tag('description'):
						content = plaintext(item.by_tag('description')[0].content)
						reviews.append(self.parseReview(content))
				
				# print reviews[0:3]
				rs['reviews'] = reviews
				self.conn.resturants.save(rs)
				print 'saved reviews for', rs['name']	
			else:
				print 'already have reviews for', rs['name']			
			# i += 1
			# if i>10:
			# 	break

	def parseReview(self,review):
		content = "".join(i for i in review if ord(i)<128)
		splitContent = str(content).split('<br />')
		reviewText = str(plaintext(splitContent[0].strip('<![CDATA'))).replace('\n',' ')
		# has rating or not
		urlPosition = 1 if len(splitContent) == 2 else 4
		rating = None
		oid = None
		person = None

		if len(splitContent) == 5:
			ratingText = str(splitContent[3])
			ratingTextStart = ratingText.find('Rating:') + len('Rating: ')
			ratingTextStop = ratingText.find('Star')
			rating = ratingText[ratingTextStart:ratingTextStop]

		tag = Element(splitContent[urlPosition]).by_tag('a')
		if tag:
			el = tag[0]
			person = el.content
			oid = str(el.attributes['href']).split('=')[1]
		review = {
			'text' : reviewText,
			'name' : person,
			'rating' : rating,
			'oid' : oid
		}
		return review



if __name__ == '__main__':
	scrape().getReviews()


