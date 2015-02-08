import MySQLdb as mdb
import re
import numpy as np
from bs4 import BeautifulSoup
import operator
import string

# Open database connection
db = mdb.connect("127.0.0.1","root","","cridatics",use_unicode = False, charset = "utf8")

# prepare a cursor object using cursor() method
cursor = db.cursor()

query = "select name from player"
cursor.execute(query)
x=cursor.fetchall()
f = open('stop/playernames.txt', 'w')
for r in x:
	name = r[0].lower()
	for w in name.split():
		f.write(w)
		f.write('\n')
f.close()

query = "select name,location,end1,end2 from venue where name <>'anyground'"
cursor.execute(query)
x=cursor.fetchall()
f= open('stop/venue.txt','w')
for r in x:
	#print r
	for i in range(0,4):
		#print i
		name = r[i].lower()
		name = name.translate(None, string.punctuation)
		for w in name.split():
			f.write(w)
			f.write('\n')
f.close()