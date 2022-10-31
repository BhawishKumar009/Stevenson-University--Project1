# IMPORTS
import urllib.request, urllib.parse, urllib.error 
import http
import sqlite3 
import json 
import time 
import ssl 
import sys
import codecs

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE



#API 
serviceurl = "https://maps.googleapis.com/maps/api/geocode/json?"
api_key="AIzaSyBNhCAFlfUSIhXCCuihcm6f6J2N7iHgySM"
#VAR
x=0
#ARRARYS
arr=list()
storeuni=list()
#CONNECTION TO DATABASE
conn = sqlite3.connect('unis.sqlite')
cur = conn.cursor()
#Creating Table
cur.execute('''
CREATE TABLE IF NOT EXISTS Locations (name TEXT, address TEXT)''')


#SEARCHING MECHANISM

user_inp=input("WHICH COUNTRY'S UNIVERSITY DO YOU WANT TO SEE?")
fhand=open('unis.txt','r',encoding='utf-8')
for line in fhand:
    if user_inp==str(line).split(',')[0]:
        storeuni.append(str(line).split(',')[1])
        x+=1
        print("WORKS")
        if x >5 :
            break
#6 UNIS STORED            
print(storeuni)
#FINDING THE GEO-Co-Ordinates and STORING IN DATABASE
for i in range(4):
    parms=dict()
    parms["address"]=storeuni[i]
    parms["key"]=api_key
    url = serviceurl + urllib.parse.urlencode(parms)
    print('Retrieving', url)
    uh = urllib.request.urlopen(url, context=ctx)
    data = uh.read().decode()
    print('Retrieved', len(data), 'characters', data[:20].replace('\n', ' '))
    try:
        js = json.loads(data)
    except:
        print(data)  # We print in case unicode causes an error
        continue
    if 'status' not in js or (js['status'] != 'OK' and js['status'] != 'ZERO_RESULTS') :
        print('==== Failure To Retrieve ====')
        print(data)
        break
    
    cur.execute('''INSERT INTO Locations (name, address)
            VALUES ( ?, ? )''', (memoryview(storeuni[i].encode()), memoryview(data.encode()) ) )
    conn.commit()  

cur.execute('SELECT * FROM Locations')
fhand = codecs.open('where.js', 'w', "utf-8")
fhand.write("myData = [\n")
count = 0
for row in cur :
    data = str(row[1].decode())
    print("for loop works")
    try: js = json.loads(str(data))
    except: continue

    if not('status' in js and js['status'] == 'OK') : continue

    lat = js["results"][0]["geometry"]["location"]["lat"]
    lng = js["results"][0]["geometry"]["location"]["lng"]
    if lat == 0 or lng == 0 : continue
    where = js['results'][0]['formatted_address']
    where = where.replace("'", "")
    try :
        print(where, lat, lng)

        count = count + 1
        if count > 1 : fhand.write(",\n")
        output = "["+str(lat)+","+str(lng)+", '"+where+"']"
        fhand.write(output)
    except:
        continue

fhand.write("\n];\n")
cur.close()
fhand.close()
print(count, "records written to where.js")
print("Open where.html to view the data in a browser")
