#!/usr/bin/env python

import os

from flask import Flask
from flask import url_for
from flask import render_template
from flask import jsonify
from flask import request
from FlavaAppBack import *

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html', title="MyTitle")

@app.route('/about')
def about():
    return render_template('about.html')
        
@app.route('/contact')
def contact():
    return render_template('contact.html')
    
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
    recsList=getRecs(flav)
    recs,recsList,imgs=getRecsInfo(recsList)
    global rec0
    global rec1
    global rec2
    global rec3
    rec0=recsList[0]
    rec1=recsList[1]
    rec2=recsList[2]
    rec3=recsList[3]
    return render_template('output.html',flavor=flavor,recs=recs,recsList=recsList,imgs=imgs)


@app.route('/more',methods=['GET','POST'])
def more():
    flav=flavor.lower()
    recsList=getRecs(flav)
    recs,recsList,imgs=getRecsInfo(recsList)
    global rec0
    global rec1
    global rec2
    global rec3
    rec0=recsList[0]
    rec1=recsList[1]
    rec2=recsList[2]
    rec3=recsList[3]    
    return render_template('output.html',flavor=flavor,recs=recs,recsList=recsList,imgs=imgs)

@app.route('/more0',methods=['GET','POST'])
def more0():
    '''
    finds neighbors of rec0
    '''
    flav=flavor.lower()
    recsList=getNeighbors(rec0)
    recs,yums,imgs=getNeighborsInfo(recsList)
    return render_template('output2.html',flavor=flavor,recs=recs,yums=yums,imgs=imgs)


#similarly for more1,more2,more3
@app.route('/more1',methods=['GET','POST'])
def more1():
    flav=flavor.lower()
    recsList=getNeighbors(rec1)
    recs,yums,imgs=getNeighborsInfo(recsList)
    return render_template('output2.html',flavor=flavor,recs=recs,yums=yums,imgs=imgs)

@app.route('/more2',methods=['GET','POST'])
def more2():
    flav=flavor.lower()
    recsList=getNeighbors(rec2)
    recs,yums,imgs=getNeighborsInfo(recsList)
    return render_template('output2.html',flavor=flavor,recs=recs,yums=yums,imgs=imgs)

@app.route('/more3',methods=['GET','POST'])
def more3():
    flav=flavor.lower()
    recsList=getNeighbors(rec3)
    recs,yums,imgs=getNeighborsInfo(recsList)
    return render_template('output2.html',flavor=flavor,recs=recs,yums=yums,imgs=imgs)

if __name__ == '__main__':
    app.debug=True
    app.run()
    
