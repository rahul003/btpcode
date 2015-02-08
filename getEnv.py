import urllib2
from bs4 import BeautifulSoup
import MySQLdb as mdb
import re
import logging
import datetime
import time
import sys, os
from time import strptime

chars = ['"']
chars2= ["'"]
teamId= {}
teamId['x']=0
teamId['india']=1
teamId['australia']=2
teamId['england']=3
teamId['west indies']=4
teamId['south africa']=5
teamId['pakistan']=6
teamId['bangladesh']=7
teamId['srilanka']=8
teamId['zimbabwe']=9
teamId['new zealand']=10
teamId['sri lanka']=8

_digits = re.compile('\d')
proxy = urllib2.ProxyHandler({'http': 'http://h.rahul:AAVCcbqX4@202.141.80.19:3128'})
auth = urllib2.HTTPBasicAuthHandler()
opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
urllib2.install_opener(opener)
month = {'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,'july':7,'august':8,'september':9,'october':10,'november':11,'december':12}
Freq = 2500 # Set Frequency To 2500 Hertz
Dur = 1000 # Set Duration To 1000 ms == 1 second

def gettestid(soup):
    try:
        match_info = soup.findAll('a','headLink')#soup(attrs={'a': 'headLink'})
        testd = match_info[1].get_text().split()[2]
        testid=int(testd)
        #print(testid)
        return testid
    except Exception, e:
        print repr(e)
    return

def getPlayerId(name,team):
    newname= name.replace("'", "")
    query= 'SELECT playerid FROM `player` WHERE name LIKE "%'+newname+'%" and team="'+str(team)+'"'
    try:
        flag=0
        cursor.execute(query)
        db.commit()
        x= cursor.fetchone()
        if(x):
            return x[0]
        else:
            print query
            return 0
    except mdb.IntegrityError:
        print "failed to extract player id"
        return 0

def addMatchOrder(testid, matchorder):
    print "matchorder"
    batting_order= matchorder["batting"]
    # bowling_order= matchorder["bowling"]
    # print batting_order
    # print matchorder['innings']
    for innings in range(0, int(matchorder['innings'])):
        x = str(innings+1)+"team"
        position=1
        cur= innings+1
        for batsman in batting_order[innings]:
            print batsman
            lowern= batting_order[x].strip().lower()
            team= teamId[lowern]
            print team
            y= getPlayerId(batsman,team) 
            print y  
            if(y==0):
                print "batsman not found"
            print "inserting"
            try:
                query= 'insert into `battingorder` (`testid`,`innings`,`country`,`position`,`playerid`) values ('+str(testid)+','+str(cur)+','+str(team)+', '+str(position)+', '+str(y)+')'
                try:
                    cursor.execute(query)
                    db.commit()
                except mdb.IntegrityError:
                    print query
                    print "failed to insert data"
            except KeyError:
                print "errooooooooooooooo "+batting_order[x].strip().lower()
            position+=1
        position=1
        # for bowler in bowling_order[x]:
        #     y= getPlayerId(bowler)   
        #     try:
        #         lowern= bowling_order[x].strip().lower()
        #         team= teamId[lowern]   
        #         query= 'insert into `bowlingorder` (`testid`,`innings`,`country`,`position`,`playerid`) values ('+str(testid)+','+str(cur)+','+str(team)+', '+str(position)+', '+str(y)+')'
        #         try:
        #             print query
        #             cursor.execute(query)
        #             db.commit()
        #         except mdb.IntegrityError:
        #             print "failed to insert bowling data"
        #     except KeyError:
        #         print "errooooooooooooooo "+bowling_order[x].strip().lower()
        #     position+=1     
    
    # query= 'update `match` set toss="'+matchorder["toss"]+'" where testid="'+testid+'"'
    # print query
    # try:
    #     cursor.execute(query)
    #     db.commit()
    # except mdb.IntegrityError:
    #     print query
    #     print "failed to insert toss"

def getBattingOrder(link):
    try:
        data= urllib2.urlopen(link).read()
    except:
        print "Error in opening the scorecard url:"
        return
    print link
    print "getting batting_order"
    soup = BeautifulSoup(data,'html.parser')
    matchorder= {}
    batting_order = {}
    bowling_order= {}
    toss=""
    try:
        print "in loop"
        # y= soup.findAll('table',{'class' : 'bowling-table'})
        x=soup.find_all('table','batting-table')
        num=0
        # print x
        for innings in x:
            count=0
            tempstr= str(num+1)+"team"
            teaminning= innings.find('tr','tr-heading').find('th',{"colspan":"2"}).get_text().strip().split()
            if(teaminning[1].find('1st')>=0 or teaminning[1].find('2nd')>=0):
                batting_order[tempstr]= teaminning[0]
            else:
                batting_order[tempstr]= teaminning[0]+" "+teaminning[1]                
            playerList= []
            for player in innings.find_all('tr'):
                if(player.has_attr('class')):
                    continue;
                title= player.find('td','batsman-name').find('a')['title']
                name=title.split()[5]
                if(len(title.split())==7):
                    name+=" "+title.split()[6]
                playerList.append(name.lower())
                count+=1
            batting_order[num]= playerList
            num+=1
        print "cccc "+str(num)
        # num=0
        # for innings in y:
        #     count=0
        #     tempstr= str(num+1)+"team"
        #     bowlerList= []
        #     for player in innings.find_all('tr'):
        #         if(player.has_attr('class')):
        #             continue;
        #         title= player.find('td','bowler-name').find('a')['title']
        #         name=title.split()[5]
        #         if(len(title.split())==7):
        #             name+=" "+title.split()[6]
        #         bowlerList.append(name.lower())
        #         bowling_order[num]= bowlerList
        #         num+=1
        # print "nnnnnnn "+str(num)
        # bowling_order["1team"]= batting_order["2team"]
        # bowling_order["2team"]= batting_order["1team"]
        # if(num>=3):
        #     if(batting_order["3team"]==batting_order["1team"]):
        #         bowling_order["3team"]= bowling_order["1team"]
        #     else:
        #         bowling_order["3team"]= bowling_order["2team"]
        # if(num==4):
        #     bowling_order["4team"]= bowling_order["2team"]            
        # try:
        #     toss=soup.find('table','notesTable').find('tr','notesRow').find('td').get_text()
        #     toss= toss.split("\n")[1]
        # except:
        #     print "couldn't find toss"
        print "num "+str(num)
        matchorder['batting']= batting_order
        # matchorder['bowling']= bowling_order
        matchorder['innings']= num
        # matchorder['toss']= toss
        return matchorder
    except:
        print "error getting batting order"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return -1

def getOverList(link, testid):
    try:
        data= urllib2.urlopen(link).read()
    except:
        print(testid)
        print "Error in opening the scorecard url:"
        return
    print "getting matchnotes"
    soup = BeautifulSoup(data,'html.parser')
    try:
        notesList= soup.find('div', 'match-notes-block').find('ul','tabs-content').find_all('li', recursive=False);
        day=0
        innings=0
        for dayNotes in notesList:
            print dayNotes['id']
            if dayNotes['id']=="day0Tab":
                continue
            day+=1  
            notes= dayNotes.find('ul','notes').find_all('li')
            prevTeam=""  
            prevInnings= 1      
            for note in notes:
                session=0
                # print note
                notestr= note.string
                if(notestr.find('Lunch:')>=0):
                   team= notestr.split(':')[1].split('-')[0].strip().lower()
                   overs= re.findall('\w+.\w+ overs',notestr)
                   if not overs:
                    # print "hhhhhhhj"
                    overs='0.0 overs'
                   session=1
                   # print overs
                   # print "done"
                elif(notestr.find('Tea:')>=0):
                    team= notestr.split(':')[1].split('-')[0].strip().lower()
                    overs= re.findall('\w+.\w+ overs',notestr)
                    if not overs:
                        overs='0.0 overs'
                    session=2
                elif(notestr.find('New Ball Taken:')>=0):
                    n= notestr.split(':')[1].split()
                    team= n[0]
                    if( not bool(_digits.search(n[1]))):
                        team+=" "+n[1]
                    team= team.strip().lower()
                    overs= re.findall('\w+.\w+ overs',notestr)
                    if not overs:
                        overs='0.0 overs'
                    session=4
                elif(notestr.find('End Of Day:')>=0):
                    team= notestr.split(':')[1].split('-')[0].strip().lower()
                    overs= re.findall('\w+.\w+ overs',notestr)
                    if not overs:
                        overs='0.0 overs'
                    session=3
                elif(len(notestr.split(':'))==1):
                    if(len(notestr.split())==3 and notestr.split()[2].strip()=="innings"):
                        if(notestr.split()[1].strip()=='1st' and innings>=2):
                            x=1
                        elif(notestr.split()[1].strip()=='2nd' and innings>=4):
                            x=1
                        else:
                            innings+=1
                    elif(len(notestr.split())==4 and notestr.split()[3].strip()=="innings"):
                        if(notestr.split()[2].strip()=='1st' and innings>=2):
                            x=1
                        elif(notestr.split()[2].strip()=='2nd' and innings>=4):
                            x=1
                        else:
                            innings+=1
                if(session>0):
                    if prevTeam and team==prevTeam and innings==(prevInnings+2):
                        innings=prevInnings
                    # print team
                    query= 'insert into `overslist_new` (`testid`,`day`,`session`,`innings`,`team`,`over`) values('+str(testid)+','+str(day)+','+str(session)+', '+str(innings)+','+str(teamId[team])+', "'+str(overs[0].split()[0])+'")'
                    try:
                        print query
                        cursor.execute(query)
                        db.commit()
                        prevInnings= innings
                        prevTeam= team
                    except mdb.IntegrityError:
                        print "failed to insert data"
                        print query  
                if session==3:
                    break             
    except:
        print "hiii"
        print note
        print sys.exc_traceback.tb_lineno 
        print "failed to connect"
   
def getEnvText(soup,testid):
    tabs= soup.find("ul", {"id": "commentary-tabs"})
    innings= tabs.find_all('a')
    count=0
    
    for inning in innings:
        count+=1
        link= inning['href']
        url= 'http://www.espncricinfo.com'
        url= url+link
        
        if count==1:
            doCase1(url,1,1,testid,first=True)

        innData = getInningsData(testid,count)
        #print testid,count,innData

        for entry in innData:
            #print entry
            session = entry[1]
            if session not in [1,2,3]:
                continue


            over = entry[0]
            day = entry[2]
            #print entry
            #print day
            if str(entry[0])=='0':
                doCase1(url,entry[2],entry[1],testid, first=False)
                continue

            if str(entry[0][-2:]) == '.0':
                endover = str(int(entry[0][:-2])-1)+'.6'
            else:
                endover = entry[0]

            pagenum = (int(float(endover))/50)+1
            url1 = url.replace("page=1","page="+str(pagenum))
            
            try:
                data= urllib2.urlopen(url1).read()
            except:
                print "Error in opening the innings url: ",url1 
                break
            
            try:
                soup = BeautifulSoup(data,'html.parser')
                commentryText=soup.find('div','commentary-section')#.find_all('p',recursive=False)
                found = commentryText.find(text=str(endover))
            except:
                print 'didnt find:',endover, ' in url:',url1
            
            try:
                founddiv = found.parent.parent
                data = ""
                immed = 1
                for sibling in founddiv.findNextSiblings():
                    flag = 0
                    if immed ==1:
                        immed=0
                        if sibling.name=='div':
                            continue
                    if sibling.name=='p':
                        t = sibling.get_text().strip()
                        t=strip_non_ascii(t)#t=filter(lambda x: x in string.printable, t)
                        
                        t = t.replace("'","")
                        t = t.replace('"','')
                        t = t.replace('-','')
                        t = t.rstrip("\n")
                        data = data + ' '+ str(t)
                    else:
                        break
                query= 'insert into `envtextnew` (`testid`,`day`,`session`,`text`) values('+str(testid)+','+str(day)+','+str(session+1)+',"'+data+'")'
                #print query
                try:
                    #print query
                    #print
                    if data!='':
                        cursor.execute(query)
                        db.commit()
                except mdb.IntegrityError:
                    pass 
                    #print "failed to insert data below", testid, day, session+1                   
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print 'endover', endover,' ', url1, testid, found, pagenum
                continue

def doCase1(url,day,session,testid, first):
    try:
        data= urllib2.urlopen(url).read()
        soup = BeautifulSoup(data,'html.parser')
        commentryText=soup.find('div','commentary-section').find(text=str('0.1')).findAllPrevious('p')
    except:
        print "Error in opening url:" ,url
    try:
        data = ""
        for t in commentryText:
            t = t.get_text().strip()
            t=strip_non_ascii(t)
            t = t.replace("'","")
            t = t.replace('"','')
            t = t.replace('-','')
            if t[-9:-6]=='SR:':
                continue
            t = t.rstrip("\n")
            if t !='' and t!='\n':
                data = data + str(t)
        #print data
        #print 'inserting to',testid,day,session
        if not first:
            session+=1
        query= 'insert into `envtextnew` (`testid`,`day`,`session`,`text`) values('+str(testid)+','+str(day)+','+str(session)+',"'+data+'")'
        #print query
        try:
            #print query
            if data!="":
                cursor.execute(query)
                db.commit()
        except mdb.IntegrityError:
            pass
            #print "failed to insert data above", testid, day, session+1
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print 'endover', endover,' ', url, testid, pagenum


def getInningsData(testid,innings):
    query="select over, session, day, team from overslist_new where testid='"+str(testid)+"' and innings='"+str(innings)+"'"
    try:
        cursor.execute(query)
        db.commit()
        session_data= cursor.fetchall()
        #print session_data # data array
        return session_data
    except mdb.IntegrityError:
        print query
        print "failed to get data"

def getfirstSession(testid,count):
    #print 'call'
    query = "select session from overslist_new where testid='"+str(testid)+"' and innings='"+str(count)+"' and over='0'"
    #pint 'adad'
    #print query
    #print 'ad'
    try:
        print query
        cursor.execute(query)
        #print query
        db.commit()
        session_data= cursor.fetchall()
        print session_data
        return session_data
    except mdb.IntegrityError:
        print query
        print "failed to get data"
    return 

def nextover(endover):
    if endover[-2:]=='.6':
        newover = str(int(float(endover[:-2]))+1)
        newover = newover+'.1'
    else:
        newover = endover[:-1]+str(int(float(endover[-1:]))+1)
    return newover

def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

def getMatchDayData(link, scorecard_url):
    #print 'in getMatchDayData, this is match link',link
    try:
        data= urllib2.urlopen(link).read()
    except:
        print "Error in opening the commentary url:"        
        return
    soup = BeautifulSoup(data, 'html.parser')
    testid=gettestid(soup)
    print 'testid of match:',testid
    # try:
    #     query="insert into `matchlinks`(`testid`, `scorecard`)  values ('"+str(testid)+"', '"+str(scorecard_url)+"')"
    #     cursor.execute(query)
    #     db.commit()
    # except mdb.IntegrityError:
    #     print query
    #     print "failed to insert data"        
    # matchorder= getBattingOrder(scorecard_url)
    # addMatchOrder(testid, matchorder)
    getEnvText(soup, testid)
    # getOverList(scorecard_url, testid)
    
def commentary(link):
    #print 'in commentary fn:',link
    try:
        data= urllib2.urlopen(link).read()
    except:
        print "Error in opening the main url:"
        return

    soup = BeautifulSoup(data,'html.parser')
    #print soup
    try:        
        for test in soup.find_all('p','potMatchMenuText mat_links'):
            # print test
            x=test.find_all('span','cardMenu')
            scorecard_url= 'http://www.espncricinfo.com'+x[0].find('a')['href']
            getMatchDayData('http://www.espncricinfo.com'+x[1].find('a')['href'], scorecard_url)
    except:
        print "couldn't retrieve match url"
        return 0

def parser(url):
    #getPlayers()
    #print '\n\nserieslink:',url
    try:
        data= urllib2.urlopen(url).read()
    except:
        print "Error in opening the url"
        return

    soup = BeautifulSoup(data,'html.parser')
    try:
        series=soup.find('section','series-summary-wrap').findAll('section','series-summary-block')
        #print 'numseries:',len(series)
        flag = False
        for test in series:
            url=test.find('section','brief-summary').find('div','series-info').find('div','teams').find('a')
            link='http://www.espncricinfo.com'+url['href'] 
            # text=x.get_text()
            # print "commentary"
            # if(text.find('Test')!=-1 or text.find('Trans-Tasman')!=-1 or text.find('Ashes')!=-1 or text.find('Warne-Muralitharan')!=-1 or text.find('Border-Gavaskar')!=-1 or text.find('Clive')!=-1 or text.find('Basil')!=-1 or text.find('Wisden')!=-1 or text.find('Frank')!=-1 or text.find('Pataudi')!=-1 or text.find('MCC Spirit')!=-1):
            #print link
            commentary(link)

    except:
        print "Error in parsing data"
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return -1
    #print "No Error for a season"
    return

# Open database connection
db = mdb.connect("172.16.27.19","rahul","rahul123","cridatics", use_unicode = True, charset = "utf8")

# # prepare a cursor object using cursor() method
cursor = db.cursor()
urlbase="http://www.espncricinfo.com/ci/engine/series/index.html?season="
suffix=['2011','2011%2F12','2012','2012%2F13','2013%2F14']
#'2013','2006','2006%2F07','2007','2007%2F08','2008','2008%2F09','2009','2009%2F10','2010','2010%2F11',
for suf in suffix:
   parser(urlbase+suf+';view=season')
   print 'done ',suf