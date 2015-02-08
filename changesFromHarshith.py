import sys, os

def getEnvText(soup,testid):
    tabs= soup.find("ul", {"id": "commentary-tabs"})
    innings= tabs.find_all('a')
    count=0
    
    for inning in innings:
            count+=1
            link= inning['href']
            url= 'http://www.espncricinfo.com'
            url= url+link
            
            innData = getInningsData(testid,count)
            
            #if count ==1:
            try:
                minsession = getFirstSession(testid,count)

                #day = 
                #session = 

                #print 'for first innings url:',url
                data= urllib2.urlopen(url).read()
                soup = BeautifulSoup(data,'html.parser')
                commentryText=soup.find('div','commentary-section').find(text=str('0.1')).findAllPrevious('p')
                #print commentryText

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
                        #print t
                        #print
                        data = data + str(t)
                #print data

                query= 'insert into `envtext` (`testid`,`day`,`session`,`text`) values('+str(testid)+','+str(day)+','+str(session)+',"'+data+'")'
                print query
                # try:
                #     #print query
                #     if data!="":
                #         cursor.execute(query)
                #         db.commit()
                # except mdb.IntegrityError:
                #     #print query
                #     print "failed to insert data above"
            except:
                print "\nError in opening the innings url for first part of innings:" ,url
                continue

            
            for session in range(1,4):
                for entry in innData:
                    if session == entry[1]:

                        if str(entry[0][-2:]) == '.0':
                            endover = str(int(entry[0][:-2])-1)+'.6'
                            #print 'newover:',endover
                        else:
                            #print 'entry[0]:',entry[0]
                            endover = entry[0]

                        pagenum = (int(float(endover))/50)+1
                        #print url
                        #print entry[0], endover, pagenum
                        
                        url1 = url.replace("page=1","page="+str(pagenum))
                        #print url1
                        try:
                            data= urllib2.urlopen(url1).read()
                        except:
                            print "Error in opening the innings url" 
                            break
                        soup = BeautifulSoup(data,'html.parser')
                        commentryText=soup.find('div','commentary-section')#.find_all('p',recursive=False)
                        

                        # if endover == 49.6:
                        #     endover = 50.0
                        # elif endover == 99.6:
                        #     endover = 100.0
                        # elif endover == 149.6:
                        #     endover = 150.0

                        found = commentryText.find(text=str(endover))
                        
                        #print 'in second part'
                        try:
                            founddiv = found.parent.parent
                            #print founddiv
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
                            #print data
                            query= 'insert into `envtext` (`testid`,`day`,`session`,`text`) values('+str(testid)+','+str(entry[2])+','+str(entry[1]+1)+',"'+data+'")'
                            # nextSibling.findAllNext(True)#'p')[:3]
                            # print type(afterdata[1])
                            # print afterdata
                            # # print nextover(endover)
                            # print afterdata.find(text=str(nextover(endover)))#'div','commentary-event')
                            #for t in afterdata:
                                
                            
                            # try:
                            #     #print query
                            #     #print
                            #     if data!='':
                            #         cursor.execute(query)
                            #         db.commit()
                            # except mdb.IntegrityError:
                            #     #print query
                            #     print "failed to insert data below"                   
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            print(exc_type, fname, exc_tb.tb_lineno)
                            print 'endover value:', endover
                            print 'in url:',url1
                            print 'continuing\n'
                            break #remove
                            continue

def getInningsData(testid,innings):
    query="select over, session, day, team from overslist_new where testid='"+str(testid)+"' and innings='"+str(innings)+"'"
    try:
        #print query
        cursor.execute(query)
        db.commit()
        session_data= cursor.fetchall()
        #print session_data # data array
        return session_data
    except mdb.IntegrityError:
        print query
        print "failed to get data"

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

