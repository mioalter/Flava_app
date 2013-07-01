#!/usr/bin/env python

import os

from flask import Flask
from flask import url_for
from flask import render_template
from flask import jsonify
from flask import request
import pandas as pd
from pandas import DataFrame,Series
from numpy.random import shuffle
import numpy as np
import MySQLdb
import pandas.io.sql as psql


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html', title="MyTitle")

flavor=''
rec0=0
rec1=0
rec2=0
rec3=0


@app.route('/drop',methods=['GET','POST'])
def drop():
    global flavor
    flavor=request.form['flavor']
    flav=flavor.lower()
    connection=MySQLdb.connect(host='127.0.0.1',user='root',passwd='',db='flava_db')
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
    recsDF=psql.frame_query('SELECT rec_id,rec_name,yum_id FROM flava_db.info WHERE (rec_id=%d)OR(rec_id=%d)OR(rec_id=%d)OR(rec_id=%d);'\
    %(recsList[0],recsList[1],recsList[2],recsList[3]),connection)
    recsList=list(recsDF['rec_id'])
    global rec0
    global rec1
    global rec2
    global rec3
    rec0=recsList[0]
    rec1=recsList[1]
    rec2=recsList[2]
    rec3=recsList[3]
    recs=recsDF['rec_name']
    yums=recsDF['yum_id']
    for i in range(4):
        yums[i]='http://www.yummly.com/recipe/'+yums[i].replace('AAA','/').replace('BBB','"')
        recs[i]=recs[i].replace('AAA','/').replace('BBB','"')
    return render_template('output.html',flavor=flavor,recs=recs,recsList=recsList)


@app.route('/more',methods=['GET','POST'])
def more():
    #flavor=request.form['flavor']
    flav=flavor.lower()
    connection=MySQLdb.connect(host='127.0.0.1',user='root',passwd='',db='flava_db')
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
    recsDF=psql.frame_query('SELECT rec_id,rec_name,yum_id FROM flava_db.info WHERE (rec_id=%d)OR(rec_id=%d)OR(rec_id=%d)OR(rec_id=%d);'\
    %(recsList[0],recsList[1],recsList[2],recsList[3]),connection)
    recsList=list(recsDF['rec_id'])
    global rec0
    global rec1
    global rec2
    global rec3
    rec0=recsList[0]
    rec1=recsList[1]
    rec2=recsList[2]
    rec3=recsList[3]
    recs=recsDF['rec_name']
    yums=recsDF['yum_id']
    for i in range(4):
        yums[i]='http://www.yummly.com/recipe/'+yums[i].replace('AAA','/').replace('BBB','"')
        recs[i]=recs[i].replace('AAA','/').replace('BBB','"')
    return render_template('output.html',flavor=flavor,recs=recs,recsList=recsList)


        
@app.route('/more0',methods=['GET','POST'])
def more0():
    flav=flavor.lower()
    #find neighbors of rec0
    connection=MySQLdb.connect(host='127.0.0.1',user='root',passwd='',db='flava_db')
    DF=psql.frame_query('SELECT id_from FROM flava_db.%s WHERE id_to=%d ORDER BY dist ASC LIMIT 4;' \
    %(flav,rec0),connection)
    recsList=list(DF['id_from'])
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
    for i in range(4):
        yums[i]='http://www.yummly.com/recipe/'+yums[i].replace('AAA','/').replace('BBB','"')
        recs[i]=recs[i].replace('AAA','/').replace('BBB','"')
    return render_template('output2.html',flavor=flavor,recs=recs,yums=yums)


#similarly for more1,more2,more3
@app.route('/more1',methods=['GET','POST'])
def more1():
    flav=flavor.lower()
    #find neighbors of rec0
    connection=MySQLdb.connect(host='127.0.0.1',user='root',passwd='',db='flava_db')
    DF=psql.frame_query('SELECT id_from FROM flava_db.%s WHERE id_to=%d ORDER BY dist ASC LIMIT 4;' \
    %(flav,rec1),connection)
    recsList=list(DF['id_from'])
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
    for i in range(4):
        yums[i]='http://www.yummly.com/recipe/'+yums[i].replace('AAA','/').replace('BBB','"')
        recs[i]=recs[i].replace('AAA','/').replace('BBB','"')
    return render_template('output2.html',flavor=flavor,recs=recs,yums=yums)

@app.route('/more2',methods=['GET','POST'])
def more2():
    flav=flavor.lower()
    #find neighbors of rec0
    connection=MySQLdb.connect(host='127.0.0.1',user='root',passwd='',db='flava_db')
    DF=psql.frame_query('SELECT id_from FROM flava_db.%s WHERE id_to=%d ORDER BY dist ASC LIMIT 4;' \
    %(flav,rec2),connection)
    recsList=list(DF['id_from'])
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
    for i in range(4):
        yums[i]='http://www.yummly.com/recipe/'+yums[i].replace('AAA','/').replace('BBB','"')
        recs[i]=recs[i].replace('AAA','/').replace('BBB','"')
    return render_template('output2.html',flavor=flavor,recs=recs,yums=yums)

@app.route('/more3',methods=['GET','POST'])
def more3():
    flav=flavor.lower()
    #find neighbors of rec0
    connection=MySQLdb.connect(host='127.0.0.1',user='root',passwd='',db='flava_db')
    DF=psql.frame_query('SELECT id_from FROM flava_db.%s WHERE id_to=%d ORDER BY dist ASC LIMIT 4;' \
    %(flav,rec3),connection)
    recsList=list(DF['id_from'])
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
    for i in range(4):
        yums[i]='http://www.yummly.com/recipe/'+yums[i].replace('AAA','/').replace('BBB','"')
        recs[i]=recs[i].replace('AAA','/').replace('BBB','"')
    return render_template('output2.html',flavor=flavor,recs=recs,yums=yums)

    
    

if __name__ == '__main__':
    app.debug=True
    app.run()
    
