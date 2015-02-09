import urllib2
from bs4 import BeautifulSoup
import MySQLdb as mdb
import re
import logging
import datetime
import time
import sys, os
from time import strptime
db = mdb.connect("127.0.0.1","root","","cridatics", use_unicode = False, charset = "utf8")
cursor = db.cursor()

def commonGetFeatures(which,testid, day, session):
	query="select * from "+ str(which)+" where testid='"+str(testid)+"' and day='"+str(day)+"' and session='"+str(session)+"'"
	try:
		cursor.execute(query)
		db.commit()
		session_data= cursor.fetchall()
		if not session_data:
			query="select * from "+str(which)+" where testid='"+str(testid)+"'"
			try:
				cursor.execute(query)
				db.commit()
				session_data = cursor.fetchall()
				#print 'all:',which, session_data
			except:
				print 'couldnt fetch all of test'

			i = day
			j = session - 1
			found = False
			while i>0:
				while j>0:
					#print i,j
					rv = getEntry(session_data,i,j)

					#print rv
					if rv:
						found = True
						rv = list(rv)
						break
					j-=1
				if found:
					break
				i-=1
				j=4
			
		
			if not found:
				if which == 'weather':
					rv = [0,0,0,0,0,0,0]
				elif which == 'pitch_new':
					rv = [0,0,0,0,0,0,0,0,0,0,0,0]
		
		else:
			print which, session_data
			rv =  list(session_data[0])

		if which=='pitch_new':
			rv = checkPrevSpin(rv,which,cursor)
			rv = fixDry(rv)
			rv = paceandbounce(rv)
			rv = sumupgrass(rv)
		
		return rv[3:]
	except mdb.IntegrityError:
		print "failed to get data", query

def getFeatures(testid, day, session):
	if session ==1 and day!=1:
		day -=1
		session = 4
		
	rval  = dict()
	rval['weather'] = commonGetFeatures('weather',testid,day,session)
	rval['pitch'] = commonGetFeatures('pitch_new',testid,day,session)
	print rval
	return rval

def getEntry(data, day, session):
	for item in data:
		if item[1]==day and item[2]==session:
			return item
	return None


def checkPrevSpin(rv,which):
	print rv
	query="select day,session,spin from "+ str(which)+" where testid='"+str(rv[0])+"'"#" and day='"+str(rv[1])+"' and session='"+str(rv[2])+"'"
	cursor.execute(query)
	db.commit()
	session_data= cursor.fetchall()
	#print session_data
	for item in session_data:
		print item
		if (item[0],item[1]) < (rv[1],rv[2]):
			if item[2]>0:
				rv[7]=item[2]
				break
	#print rv
	return rv

#return grass+green adn swing+green
def fixDry(rv):
	#if first or secodn day, flat. else spin
	#if dry and swing: then remove flat for first days
	#9 is swing
	# 11 is dry
	# 10 is flat
	print rv
	if rv[11]>0 and rv[1]<=2 and not rv[9]:
		rv[10] = rv[11]
	elif rv[11]>0 and rv[1]>2:
		rv[7] = rv[11]
	print rv
	return rv

def paceandbounce(rv):
	if rv[5] and rv[6]:
		rv[4] = rv[5]+rv[6]
	return rv

def sumupgrass(rv):
	rv[4] +=rv[3]
	rv[9]+=rv[3]
	return rv
# Open database connection

# db = mdb.connect("10.11.12.14","rahul","rahul123","cridatics", use_unicode = True, charset = "utf8")

# # # prepare a cursor object using cursor() method
# cursor = db.cursor()
     
# r = getFeatures(2085,2,3)
# print r
# print r['weather']
# print r['weather'][4]