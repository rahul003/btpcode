import MySQLdb as mdb
import re
from sets import Set
import numpy as np
from bs4 import BeautifulSoup
import operator
import string
import nltk
from nltk import stem
from nltk import word_tokenize
from nltk.stem.lancaster import LancasterStemmer
from collections import defaultdict
from nltk import PorterStemmer
weatherwords = defaultdict()
pitchwords = defaultdict()
porter = PorterStemmer()
snowstem = stem.snowball.SnowballStemmer("english")
wnl = nltk.WordNetLemmatizer()

#weatherwords = Set()
#weatherwordsdict = {}

# pitchwords = Set()
# pitchwordsdict = {}

def loadwords():
	for line in open('weatherwords.txt'):
		collection = line.rstrip('\n').split(',')
		weatherwords[collection[0]] = {collection[0]:0}
		count = 0
		for word in collection:
			count+=1
			if count ==1:
				continue
			weatherwords[collection[0]][word]=0
			#weatherwordsdict[word]=0
	
	for line in open('pitchwords.txt'):
		collection = line.rstrip('\n').split(',')
		pitchwords[collection[0]] = {collection[0]:0}
		count = 0
		for word in collection:
			count+=1
			if count ==1:
				continue
			pitchwords[collection[0]][word]=0
	
	print weatherwords
	print	
	print pitchwords
	
loadwords()

for collection in weatherwords:
	for word in weatherwords[collection].keys():
		print word, LancasterStemmer().stem(word), porter.stem(word)
for collection in pitchwords:
	for word in pitchwords[collection].keys():
		print word, LancasterStemmer().stem(word), porter.stem(word)

print porter.stem('dried')
#print LancasterStemmer().stem('spins'), porter.stem('cracks')
# tokens = weatherwords.keys()
# ttokens = [token.keys() for token in tokens]
# print ttokens
# Lanctokens = [LancasterStemmer().stem(t) for t in tokens]
#wnltokens = [wnl.lemmatize(t) for t in tokens]
#snowtokens = [snowstem.stem(t) for t in tokens]
# print tokens
# print Lanctokens
#print wnltokens
#print snowtokens

# print 

# tokens = pitchwordsdict.keys()
# Lanctokens = [LancasterStemmer().stem(t) for t in tokens]
# #wnltokens = [wnl.lemmatize(t) for t in tokens]
# #snowtokens = [snowstem.stem(t) for t in tokens]
# print tokens
# print Lanctokens
#print wnltokens
#print snowtokens

#looks like LancasterStemmer is the ebst