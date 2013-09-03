import requests
import json
import MySQLdb

headers = {'X-Yummly-App-ID':'c1589366','X-Yummly-App-Key': '111df0b296542d260b860f6058c46de7'}

###Flavor is SAVORY/MEATY!!###

def simpleGetPut(food,sweet,sour,salty,piquant,bitter):
    '''
    food - string
    sweet, etc. - integers between 1 and 2
    number - int
    returns number many recipes from yummly containing the given food with the specified flavor profile,
    puts them into the yum database
    '''
    flavor='savory'
    sweetMin=float(sweet-1)/2
    sweetMax=float(sweet)/2
    sourMin=float(sour-1)/2
    sourMax=float(sour)/2
    saltyMin=float(salty-1)/2
    saltyMax=float(salty)/2
    piquantMin=float(piquant-1)/2
    piquantMax=float(piquant)/2
    bitterMin=float(bitter-1)/2
    bitterMax=float(bitter)/2
    #meatyMin=float(meaty-1)/2
    #meatyMax=float(meaty)/2
    url="http://api.yummly.com/v1/api/recipes?q=%s\
    &flavor.sweet.min=%f\
    &flavor.sweet.max=%f\
    &flavor.sour.min=%f\
    &flavor.sour.max=%f\
    &flavor.salty.min=%f\
    &flavor.salty.max=%f\
    &flavor.piquant.min=%f\
    &flavor.piquant.max=%f\
    &flavor.bitter.min=%f\
    &flavor.bitter.max=%f\
    &flavor.meaty.min=0.8\
    &flavor.meaty.max=1.0\
    &maxResult=200\
    &requirePictures=True\
    " %(food,sweetMin,sweetMax,sourMin,sourMax,saltyMin,saltyMax,piquantMin,piquantMax,bitterMin,bitterMax)
    r=requests.get(url,headers=headers)
    print r
    try:
        data=json.loads(r.text)
        recs=data['matches']
        connection=MySQLdb.connect(host='127.0.0.1',user='root',passwd='',db='flava_db')
        cursor=connection.cursor()
        yum_id=''
        rec_name=''
        rec_rating=0
        for i in range(len(recs)):
            yum_id=recs[i]['id'].encode('ascii','ignore')
            yum_id=yum_id.replace('/','AAA').replace('"','BBB')
            rec_name=recs[i]['recipeName'].encode('ascii','ignore')
            rec_name=rec_name.replace('/','AAA').replace('"','BBB')
            if recs[i]['rating']!=None:
                rec_rating=recs[i]['rating']
            cursor.execute('INSERT INTO info(rec_id,yum_id,rec_name,rec_flavor,rec_food,rec_rating) VALUES(NULL,"%s","%s","%s","%s","%d")'\
            %(yum_id,rec_name,flavor,food,rec_rating))
            cursor.execute("""select rec_id from flava_db.info order by rec_id desc limit 1""")
            index=cursor.fetchall()
            index=int(index[0][0])
            for j in range(len(recs[i]['ingredients'])):
                cursor.execute('INSERT INTO ingredients(row_id,rec_id,ingredient) VALUES(NULL,"%d","%s")'%(index,recs[i]['ingredients'][j].encode('ascii','ignore')))
            for k in range(len(recs[i]['smallImageUrls'])):
                cursor.execute('INSERT INTO images(row_id,rec_id,url) VALUES(NULL,"%d","%s")' %(index,recs[i]['smallImageUrls'][k].encode('ascii','ignore')))
    except:
        print 'skipped this one'
    return
    
def simpleGather(food):
    '''
    food - a string
    number - an int
    '''
    for a in range(1,3):
        for b in range(1,3):
            for c in range(1,3):
                for d in range(1,3):
                    for e in range(1,3):
                        for f in range(1,3):
                            simpleGetPut(food,a,b,c,d,e)
    return





