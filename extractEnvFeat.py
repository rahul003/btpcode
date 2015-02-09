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
from nltk import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from collections import defaultdict

weatherwords = defaultdict()
pitchwords = defaultdict()
stopwords = Set()
weather = Set()
pitch = Set()
negationList = ['not','little','less','low','hardly']
#stemmer = LancasterStemmer()
stemmer = PorterStemmer()
reversecollection = {}

def loadStopwords():
	for line in open('stop/stopwords.txt'):
		stopwords.add(line.rstrip('\n'))
	for line in open('stop/playernames.txt'):
		stopwords.add(line.rstrip('\n'))
	for line in open('stop/venue.txt'):
		stopwords.add(line.rstrip('\n'))

def loadwords():
	for line in open('weatherwords.txt'):
		collection = line.strip().split(',')
		#print collection
		w = stemmer.stem(collection[0])
		weather.add(w)
		weatherwords[w] = {w:0}
		#print collection[0]
		reversecollection[w] = w
		#print reversecollection
		count = 0
		for word in collection:
			w = stemmer.stem(word)
			weather.add(w)
			reversecollection[w]=stemmer.stem(collection[0])
			count+=1
			if count ==1:
				continue
			weatherwords[stemmer.stem(collection[0])][w]=0


	for line in open('pitchwords.txt'):
		collection = line.strip().split(',')
		w = stemmer.stem(collection[0])
		pitch.add(w)
		pitchwords[w] = {w:0}
		#print collection[0]
		reversecollection[w] = w
		#print reversecollection
		count = 0
		for word in collection:
			w = stemmer.stem(word)
			pitch.add(w)
			reversecollection[w]=stemmer.stem(collection[0])
			count+=1
			if count ==1:
				continue
			pitchwords[stemmer.stem(collection[0])][w]=0
	
def initddict():
	for collection in weatherwords:
		for word in weatherwords[collection].keys():
			weatherwords[collection][word]=0
	for collection in pitchwords:
		for word in pitchwords[collection].keys():
			pitchwords[collection][word]=0

def isEmpty(doubld):
	sumval = 0
	for key in doubld.keys():
		for word in doubld[key].keys():
			sumval+=doubld[key][word]
	
	if sumval==0:
		return 1
	else:
		return 0

def getOpp(clas):
	if clas in ['bounc','pace']:
		#print clas,' opp:','slow'
		return 'slow'
	elif clas in ['swing']:
		#print clas,' opp:','dri'
		return 'dri'
	elif clas in ['grass']:
		#print clas,' opp:','flat'
		return 'flat'
	else:
		#print ''
		return None

def fixSpin():
	query = "select * from pitch_new where spin>0"
	cursor.execute(query)
	results=cursor.fetchall()
	for r in results:
		testid=r[0]
		day = r[1]
		session=r[2]
		i = day
		j = session+1
		while i<=5:
			if i!=day:
				j=2
			while j<=4:
				query2 = "insert into pitch_new (testid,day,session,spin) values("+str(testid)+","+str(i)+","+str(j)+","+str(1)+") on duplicate key update "
  				query2 += "spin = 1"
  				try:
  					#print query2
  					cursor.execute(query2)
  					db.commit()
  				except:
  					print 'failed update query',query2
  				j+=1
  			i+=1

def extractFeatures(results):
	counttoprint = 0
	for row in results:
		#print row

		#if not counttoprint%1000:
		#	print counttoprint
		text = row[3].lower()
		initddict()

		if not text[0:2]=='0.1':
			lines = text.split('.')
			for line in lines:
				# print 'line: ',line
				line.strip('\n')
				#line = line.replace(',',' ')
				#tokensl = line.split(' ')
				tokensl = tokenizer.tokenize(line)
				# print tokensl
				# print 'green' in stopwords
				tokens = (Set(tokensl) - stopwords)
				# print tokens
				tokens = [stemmer.stem(t) for t in tokens]
				tokensl = [stemmer.stem(t) for t in tokensl]
				tokens = Set(tokens)
				# print tokens
				# print tokensl
				# print tokens & weather
				if tokens & weather:
					negation = False
					count = 0
					# print 'match'
					for word in tokensl:
						if word in negationList:
							negation = True
							count = 0
							continue
						elif count>3:
							negation = False
						elif negation:
							count+=1
										
						if word in weather:
							# print word,":", line, negation
							clas = reversecollection[word]
							if negation:
								#clas = getOpp(clas)#addtooppclass
								#print 'negated',row[0],row[1],row[2],tokensl,line
							 	negation = False
							 	continue
							try:
								weatherwords[clas][clas]+=1
							except:
								print 'weather:',clas, word, row[0],row[1],row[2]
				#if str(row[0])=='1806':
				# print tokens
				if tokens & pitch:
					# print 'matched', tokensl
					negation = False
					count = 0
					#print tokensl
					for word in tokensl:
						# print word
						#print word,word in negationList,count, negation
						if word in negationList:
							negation = True
							#print word, tokens
							count = 0
							continue
						elif count>3:
							negation = False
						elif negation:
							count+=1
						if word in pitch:
							#print word, line
							# print word,":", line, negation
							clas = reversecollection[word]
							if negation:
								#print 'negated', row[0],row[1],row[2], line, word
								clas = getOpp(clas)#addtooppclass
								if clas == None:
									continue
								negation = False
							# if clas =='dri':
							# 	day = int(float(row[1]))
							# 	if day==1 or day==2:
							# 		pitchwords['flat']['flat']+=1
							# 	else:
							# 		pitchwords['spin']['spin']+=1
							# if clas == 'green':
							# 	pitchwords['bounc']['bounc']+=1
							# 	pitchwords['pace']['pace']+=1	
							# 	pitchwords['swing']['swing']+=1	
							# if clas == 'grass':
							# 	pitchwords['bounc']['bounc']+=1

							# 	pitchwords['pace']['pace']+=1	
							#print clas, word, pitchwords
							try:
								#print clas, word, line#, tokensl
								pitchwords[clas][clas]+=1
							except:
								print 'pitch:',clas, word, reversecollection[word],row[0],row[1],row[2]
			if not isEmpty(weatherwords):
				s=0
				t=0
				query = "insert into weather_new(testid,day,session"
				for collection in weatherwords:
					query+=","
					query += str(collection)
				query+=") values("+str(row[0])+","+str(row[1])+","+str(row[2])
				for collection in weatherwords:
					count = 0
					for word in weatherwords[collection]:
						count+=weatherwords[collection][word] 
					query+=","+str(count)
				query+=")"
				#print query
				try:
					pass
					# cursor.execute(query)
					# db.commit()
				except mdb.IntegrityError:
					pass
					#print "failed to insert data"
					#print query         
			else:
				pass
				#print 'empty'


			if not isEmpty(pitchwords):
				#weatherwords['green']['green']+=(weatherwords['bounce'])
				query = "insert into pitch_new(testid,day,session"
				for collection in pitchwords:
					query+=","
					query += str(collection)
				query+=") values("+str(row[0])+","+str(row[1])+","+str(row[2])
				for collection in pitchwords:
					count = 0
					for word in pitchwords[collection]:
						count+=pitchwords[collection][word] 
					query+=","+str(count)
				query+=")"
				#print query
				try:
					#pass
					# cursor.execute(query)
					# db.commit()
					counttoprint+=1
				except mdb.IntegrityError:
					pass
					# print "failed to insert data"
					# print query         
			else:
				pass
				#print 'empty'

def fixBowlFeatures(column):
	query = "select * from pitch_new where "+str(column)+">0"
	cursor.execute(query)
	results=cursor.fetchall()
	for r in results:
		testid=r[0]
		day = r[1]
		session=r[2]
		i = day
		j = session+1
		count = 0
		if i==1:
			end=3
			if column =='swing':
				end=2
			for i in range(1,end):
				j=1
				while j<=4:
					if j==1 and i!=1:
						j+=1
					query2 = "insert into pitch_new (testid,day,session,"+str(column)+") values("+str(testid)+","+str(i)+","+str(j)+","+str(1)+") on duplicate key update "
	  				query2 += str(column)+"= 1"
	  				#print query2
	  				try:
	  					# pass
  						cursor.execute(query2)
	  					db.commit()
	  				except:
	  					print 'failed update query',query2
	  				j+=1	

	  	elif i==2 and column!='swing':
	  		j=2
	  		while j<=4:
				query2 = "insert into pitch_new (testid,day,session,"+str(column)+") values("+str(testid)+","+str(i)+","+str(j)+","+str(1)+") on duplicate key update "
	  			query2 += str(column)+"= 1"
	  			try:
	  				# print query2
	  				cursor.execute(query2)
	  				db.commit()
	  			except:
	  				print 'failed update query',query2
	  			j+=1	  			
	  		

	  			#instemaybead of 2,1 doing 1,4
	  		query2 = "insert into pitch_new (testid,day,session,"+str(column)+") values("+str(testid)+",1,4,1) on duplicate key update "
	  		query2 += str(column)+"= 1"
	  		try:
	  				# print query2
				cursor.execute(query2)
				db.commit()
			except:
				print 'failed update 1,4 query',query2
	  	# elif i==3 and column!='swing':
	  	# 	while j>1:
				# query2 = "insert into pitch_new (testid,day,session,"+str(column)+") values("+str(testid)+","+str(i)+","+str(j)+","+str(1)+") on duplicate key update "
	  	# 		query2 += str(column)+"= 1"
	  	# 		try:
	  	# 			print query2
	  	# 			cursor.execute(query2)
	  	# 			db.commit()
	  	# 		except:
	  	# 			print 'failed update query',query2
	  	# 		j-=1
	  		
	  	# 	query2 = "insert into pitch_grass_updt (testid,day,session,"+str(column)+") values("+str(testid)+","+str(i-1)+",4,"+str(1)+") on duplicate key update "
	  	# 	query2 += str(column)+"= 1"
	  	# 	try:
	  	# 		print query2
	  	# 		cursor.execute(query2)
	  	# 		db.commit()
	  	# 	except:
	  	# 		print 'failed update query',query2

def addPaceBounce():
	query = "update pitch_new set bounc=1, pace=1 where grass>0"
	try:
		cursor.execute(query)
		db.commit()
	except:
		print 'failed update query',query  				

def updategreen(results):
	counttoprint = 0
	for row in results:
		text = row[3].lower()
		initddict()
		if not text[0:2]=='0.1':
			lines = text.split('.')
			for line in lines:
				line.strip('\n')
				line = line.replace(',',' ')
				#tokensl = line.split(' ')
				tokensl = tokenizer.tokenize(line)
				tokens = (Set(tokensl) - stopwords)
				tokens = [stemmer.stem(t) for t in tokens]
				tokensl = [stemmer.stem(t) for t in tokensl]
				tokens = Set(tokens)
				if tokens & pitch:
					negation = False
					count = 0
					for word in tokensl:
						if word in negationList:
							negation = True
							count = 0
							continue
						elif count>3:
							negation = False
						elif negation:
							count+=1
						if word in pitch:
							clas = reversecollection[word]
							if negation:
								clas = getOpp(clas)#addtooppclass
								if clas == None:
									continue
								negation = False
							try:
								pitchwords[clas][clas]+=1
							except:
								print 'pitch:',clas, word, reversecollection[word],row[0],row[1],row[2]
			#print pitchwords['green']
			if pitchwords['green']['green']:
				query = "update pitch_new set green="
				query += str(pitchwords['green']['green'])
				query+=" where testid="+str(row[0])+" and day="+str(row[1])+" and session="+str(row[2])
				#print query
				try:
#					pass
					cursor.execute(query)
					db.commit()
					counttoprint+=1
				except mdb.IntegrityError:
					pass
			else:
				pass

#db = mdb.connect("192.168.201.1","rahul","rahul123","cridatics",use_unicode = True, charset = "utf8")
db = mdb.connect("172.16.27.19","rahul","rahul123","cridatics",use_unicode = True, charset = "utf8")
cursor = db.cursor()
query = "select testid,day,session,text from envtextnew"# where testid=1884"# where testid in (select distinct testid from commentary where bat='293')"

cursor.execute(query)
results=cursor.fetchall()
vocab = {}
loadStopwords()
loadwords()
#print stopwords
tokenizer = RegexpTokenizer(r'\w+')

#print tokenizer.tokenize("what's up bitches, you faggots?")
#print results
#extractFeatures(results)
updategreen(results)
#addPaceBounce()
#fixSpin()
# fixBowlFeatures('grass')
# fixBowlFeatures('swing')
