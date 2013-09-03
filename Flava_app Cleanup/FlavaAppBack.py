import pandas as pd
from pandas import DataFrame,Series
from numpy.random import shuffle
import numpy as np
import MySQLdb
import pandas.io.sql as psql
import requests
import json


connection=MySQLdb.connect(host='127.0.0.1',user='root',passwd='',db='flava_db')
flavor=''

def getRecs(flav):
    '''
    flavor -  a string
    '''
    global flavor
    flavor=flav
    DF=psql.frame_query('SELECT distinct(flava_db.info.rec_id), flava_db.info.yum_id,flava_db.info.rec_name, \
    flava_db.info.rec_flavor,flava_db.info.rec_food,flava_db.info.rec_rating \
    FROM flava_db.info \
    INNER JOIN flava_db.%s \
    ON flava_db.info.rec_id = flava_db.%s.id_to;'%(flav,flav),connection)
    meatDF=DF[(DF['rec_food']=='chicken')|(DF['rec_food']=='pork')|(DF['rec_food']=='beef')|(DF['rec_food']=='steak')]
    fishDF=DF[(DF['rec_food']=='fish')|(DF['rec_food']=='tuna')|(DF['rec_food']=='salmon')]
    pastaDF=DF[(DF['rec_food']=='pasta')|(DF['rec_food']=='salad')]
    meatVect=np.array(meatDF['rec_id']).astype(int)
    fishVect=np.array(fishDF['rec_id']).astype(int)
    pastaVect=np.array(pastaDF['rec_id']).astype(int)
    shuffle(meatVect)
    shuffle(fishVect)
    shuffle(pastaVect)
    recsList=[meatVect[0],meatVect[1],fishVect[0],pastaVect[0]]
    return recsList
    
def getRecsInfo(recsList):
    '''
    recsListIn - list of recipe ids to look up
    '''
    recsDF=psql.frame_query('SELECT rec_id,rec_name,yum_id FROM flava_db.info WHERE (rec_id=%d)OR(rec_id=%d)OR(rec_id=%d)OR(rec_id=%d);'\
    %(recsList[0],recsList[1],recsList[2],recsList[3]),connection)
    recsList=list(recsDF['rec_id'])
    recs=recsDF['rec_name']
    yums=recsDF['yum_id']
    imgs=[]
    for i in range(4):
        search=recs[i].replace('AAA','/').replace('BBB','"').replace(' ','%20')+'%20yummly'
        url='https://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=%s'%search 
        recs[i]=recs[i].replace('AAA','/').replace('BBB','"')
        r=requests.get(url)
        try:
            data=json.loads(r.text)
            imgs.append(data['responseData']['results'][0]['url'].encode('ascii','ignore'))
        except:
            imgs.append('http://www.alohaorganicfruit.com/wp-content/uploads/2010/10/peaches-pile.jpg')
    return recs,recsList,imgs
    
def getNeighbors(rec_id):
    '''
    rec_id - an integer, the rec_id whose neighbors to retrieve
    '''
    DF=psql.frame_query('SELECT id_from FROM flava_db.%s WHERE id_to=%d ORDER BY dist ASC LIMIT 4;' \
    %(flavor,rec_id),connection)
    recsList=list(DF['id_from'])
    return recsList
    
def getNeighborsInfo(recsList):
    '''
    recsList - list of rec_ids consisting of selection and nearest neighbors
    '''
    recsDF=psql.frame_query('SELECT rec_id,rec_name,yum_id FROM flava_db.info WHERE (rec_id=%d)OR(rec_id=%d)OR(rec_id=%d)OR(rec_id=%d);'\
    %(recsList[0],recsList[1],recsList[2],recsList[3]),connection)
    ##NOTE: things come out of SQL not necessarily in the order in which it was queried! 
    #Have to put results back in original order!!
    id_list=list(recsDF['rec_id'])
    temp_names=recsDF['rec_name']
    temp_yums=recsDF['yum_id']
    recs=[]
    yums=[]
    for num in recsList:
        for shuf in id_list:
            if num==shuf:
                recs.append(temp_names[id_list.index(shuf)])
                yums.append(temp_yums[id_list.index(shuf)])
    imgs=[]
    for i in range(4):
        search=recs[i].replace('AAA','/').replace('BBB','"').replace(' ','%20')+'%20yummly'
        url='https://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=%s' %search 
        yums[i]='http://www.yummly.com/recipe/'+yums[i].replace('AAA','/').replace('BBB','"')
        recs[i]=recs[i].replace('AAA','/').replace('BBB','"')
        r=requests.get(url)
        try:
            data=json.loads(r.text)
            imgs.append(data['responseData']['results'][0]['url'].encode('ascii','ignore'))
        except:
            imgs.append('http://www.alohaorganicfruit.com/wp-content/uploads/2010/10/peaches-pile.jpg')
    return recs,yums,imgs

