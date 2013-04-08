from pymongo import Connection
from sklearn.cross_validation import train_test_split


import logging
import numpy as np
from optparse import OptionParser
import sys
from time import time
import pylab as pl
from collections import Counter

from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.linear_model import RidgeClassifier
from sklearn.svm import LinearSVC
from sklearn.utils.extmath import density
from sklearn import metrics


class analyze():
	def __init__(self):
		self.conn = Connection()['citypaper']

	def classify(self,X,Y):
		# create transformed train/test with tfidfvectorizer to go from string to float
		vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5,stop_words='english')
		X_transformed = vectorizer.fit_transform(X)

		# split test/train
		X_train, X_test, Y_train, Y_test = train_test_split(X_transformed, Y, test_size=0.33, random_state=42)

		print X_train.shape, X_test.shape

		feature_names = np.asarray(vectorizer.get_feature_names())
		categories = ["1","2","3","4","5"]

		# create classifier
		clf = LinearSVC(penalty="l1", dual=False, tol=1e-3)


		print '_' * 80
		print "Training: "
		print clf
		t0 = time()
		clf.fit(X_train, Y_train)
		train_time = time() - t0
		print "train time: %0.3fs" % train_time

		t0 = time()
		pred = clf.predict(X_test)
		test_time = time() - t0
		print "test time:  %0.3fs" % test_time

		# score = metrics.f1_score(Y_test, pred)
		# print "f1-score:   %0.3f" % score

		if hasattr(clf, 'coef_'):
		    print "dimensionality: %d" % clf.coef_.shape[1]
		    print "density: %f" % density(clf.coef_) 

		    if feature_names is not None:
		        print "top 10 keywords per class:"
		        for i, category in enumerate(categories):
		            top10 = np.argsort(clf.coef_[i])[-10:]
		            print "%s: %s" % (category, " ".join(feature_names[top10]))

		print "classification report:" 
		print metrics.classification_report(Y_test, pred,target_names=categories)


		print "confusion matrix:"
		print metrics.confusion_matrix(Y_test, pred)

		print 
		clf_descr = str(clf).split('(')[0]
		print clf_descr, train_time, test_time

	def svcAllTags(self, acceptedTags = ['Music Venue', 'Bar']):

		totalReviews = 0
		restaurantsWithReviews = 0
		rests = {}
		restsMatrix = []

		for rest in self.conn.restaurants.find():
			oid = rest.get('url').split('?')[1].split('=')[1]
			rests[oid] = { 'x' : [], 'y': []}
			tags = [ tag[1].encode('ascii', 'ignore')	for tag in rest['details'].get('parsedTags')]

			# does the rest have the tags we are interested in
			if list( set(tags) & set(acceptedTags) ):
				if rest.get('reviews'):
					for review in rest['reviews']:
						if review.get('rating'):
							rests[oid]['x'].append( review.get('text'))
							rests[oid]['y'].append( int(review.get('rating')))

		X = []
		Y = []
		for k,item in rests.iteritems():
			[ X.append( review ) for review in item['x'] ]
			[ Y.append( rating ) for rating in item['y'] ]

		print X[:4], Y[:4]
		self.classify(X,Y)
		

	def findAllTags(self):
		tagSet = []
		for rest in self.conn['restaurants'].find():
			tags = rest['details'].get('parsedTags')
			s = []
			for tag in tags:
				finalTag =  tag[1]
				s.append(finalTag)
				tagSet.append(finalTag.encode('ascii', 'ignore') )
			print rest['name'],s
		
		# for (name,count) in  Counter(tagSet).most_common():
		# 	print "{0},{1}".format(name,count)

	def svcSubset(self, tags=['Mexican']):
		for rest in self.conn['restaurants'].find():
			tagsDB = rest['details'].get('parsedTags')
			s = [ tag[1].encode('ascii', 'ignore')	for tag in tagsDB]
			# s = [ tag[1].encode('ascii', 'ignore')	for tag in tagsDB if tag[1].encode('ascii', 'ignore') in tags]
			if s and 'American' in s:
				print rest['name'],s


if __name__ == '__main__':
	analyze().svcAllTags()











