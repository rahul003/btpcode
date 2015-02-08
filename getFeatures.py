import urllib2
from bs4 import BeautifulSoup
import MySQLdb as mdb
import re
import logging
import datetime
import time
import sys, os
from time import strptime

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
				print 'all:',which, session_data
			except:
				print 'couldnt fetch all of test'

			i = day
			j = session - 1
			found = False
			while i>0:
				while j>0:
					print i,j
					rv = getEntry(session_data,i,j)
					#print rv
					if rv:
						found = True
						break
					j-=1
				if found:
					break
				i-=1
				j=4
			if not found:
				if which == 'weather':
					rv = (0,0,0,0,0,0,0)
				elif which == 'pitch':
					rv = (0,0,0,0,0,0,0,0,0,0,0,0)
			return list(rv)
		else:
			print which, session_data
			return list(session_data[0])
	except mdb.IntegrityError:
		print "failed to get data", query

def getFeatures(testid, day, session):
	if session ==1 and day!=1:
		day -=1
		session = 4
		
	rval  = dict()
	rval['weather'] = commonGetFeatures('weather',testid,day,session)
	rval['pitch'] = commonGetFeatures('pitch',testid,day,session)
	print rval
	return rval

def getEntry(data, day, session):
	for item in data:
		if item[1]==day and item[2]==session:
			return item

	return None



# Open database connection
db = mdb.connect("172.16.27.19","rahul","rahul123","cridatics", use_unicode = True, charset = "utf8")

# # prepare a cursor object using cursor() method
cursor = db.cursor()
     
r = getFeatures(2085,2,3)
print r['weather']
print r['weather'][4]