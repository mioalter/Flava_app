###############IMPORTANT#######################
import nltk
from nltk import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
lmtzr = WordNetLemmatizer()
###Do this:   lmtzr.lemmatize('cars')
###############################################
import pandas.io.sql as psql
import MySQLdb
import numpy as np
import pandas as pd

####SET FLAVOR: PIQUANT, SWEET, MEATY#############

################################
##SETTING FLAVOR TO: SWEET######
################################

FLAVOR='piquant'

connection=MySQLdb.connect(host='127.0.0.1',user='xxx',passwd='xxx',db='flava_db')
DF=psql.frame_query('SELECT rec_id,yum_id,rec_name,rec_flavor,rec_food,rec_rating,count(rec_name) AS Count \
FROM flava_db.info \
WHERE ((rec_flavor="%s")AND(rec_rating>3)) \
GROUP BY rec_name \
ORDER BY count(rec_name) ASC;' %FLAVOR,connection)

#DataFrame of all ingredients
ingDF=psql.frame_query('SELECT * from flava_db.ingredients',connection)
#DataFrame of ingredients of the recipes in DF
flavorDF=pd.merge(DF,ingDF,how='inner',on='rec_id')                
#vector of rec_id's to iterate over
R=np.array(DF['rec_id']).astype(int)
#create dictionary {rec_id:rec_name}


####### use Lemmatizer in dataVacuum to make all plurals singular.

namesDict={}
for i in range(len(DF)):
    namesDict[R[i]]=DF.get_value(i,'rec_name')
#create a dictionary {rec_id:[ingredients]}
    
ingDict={}
for i in range(len(DF)):
    ingDict[R[i]]=list(flavorDF[flavorDF['rec_id']==R[i]]['ingredient']) 


cleanIngDict={}
for num in ingDict.keys():
    cleanIngDict[num]=ingDict[num]

###Make all plurals singular: lemmatize all words!####
for wuz in cleanIngDict.keys():
    for item in cleanIngDict[wuz]:
        newItem=''
        for word in item.split():
            newItem+='%s '%lmtzr.lemmatize(word)
        newItem=newItem.rstrip()
        cleanIngDict[wuz][cleanIngDict[wuz].index(item)]=newItem

#a list of one word ingredients: an ingredient containing one of these words can be replaced by the word##
monoFoods=['flour','egg',\
'orange','pear','banana','pineapple','lemon','lime','apricot','strawberry','rasberry','coconut','pumkin',\
'onion','tomato','celery','spinach','broccoli','zucchini','carrot','potato','asparagus','lettuce','pea',\
'garlic','cumin','coriander','tabasco','salt','basil','mint','thyme','rosemary','tarragon','cinnamon','mustard','raisin','dill',\
'curry','worcestershire','paprika','cayenne','balsamic','cilantro','ginger','parsley','chile','marjoram',\
'chicken','pork','beef','fish','tuna','salmon','sausage','steak','shrimp',\
'almond','pecan','walnut',\
'melon','grape','sugar',\
'yogurt','water','molasses','yeast','soba',\
'macaroni','cheddar','parmigiano','mozzarella','butter','gruyere','parmesan','penne','pasta',\
'olive oil','sour cream',\
'bourbon','vodka']

#apple vs. apple cider vinegar, EV olive oil/olive oil vs. varieties of olives, roquefort vs. blue cheese


####CLEAN UP STANDARDIZES INGREDIENTS               

def cleanUp(ingDict):
    '''
    ingDict- (rec_id,[ingredients]) dictionary
    '''
    for recipe in ingDict.keys():
        for item in ingDict[recipe]:
            if len(item.split())>2:
                token=word_tokenize(item)
                newItem=token[-2]+' '+token[-1]
                ingDict[recipe][ingDict[recipe].index(item)]=newItem
            if (('black pepper' in item) or ('ground pepper' in item)\
            or ('ground black pepper' in item) or ('fresh ground black pepper' in item)):
                try:
                    ingDict[recipe][ingDict[recipe].index(item)]='pepper'
                except:
                    print 'skipped'
            if ('green pepper' or 'red pepper' or 'bell pepper' or 'green bell pepper' or 'red bell pepper' or 'orange bell pepper') in item:
                try: 
                    ingDict[recipe][ingDict[recipe].index(item)]='bell pepper'
                except:
                    print 'skipped'
            for food in monoFoods:
                if food in item.split():
                    try:
                        ingDict[recipe][ingDict[recipe].index(item)]=food
                    except:
                        print 'skipped'
    return ingDict
     
##Cleaning Up the ingredients!##           
cleanIngDict=cleanUp(cleanIngDict)

                          
##Parameters for special cases!##
a=0.5
b=0.5
                        
def jaccard(A,B):
    '''
    A,B - lists of ingredients
    '''
    J=0.0
    if (set(A)<=(set(A)&set(B)))or(set(B)<=(set(A)&set(B))):
        J=a*(1.0-float(len(set(A)&set(B)))/len(set(A+B)))
    elif (len(set(A))<=5) or (len(set(B))<=5):
        J=1.0-(b*float(len(set(A)&set(B)))/len(set(A+B)))
    else:
        J=1.0-float(len(set(A)&set(B)))/len(set(A+B))
    return J
   
id_list=cleanIngDict.keys()

##Now choose a subList and subDict!##


##Distance matrix
def distances(id_list,ingDict):
    '''
    id_list - ordered list of keys of ingDict
    ingDict - (key,value)=(rec_id,list of ingredients)
    '''
    ingList=id_list
    n=len(ingList)
    D=np.zeros(n**2)
    D=D.reshape(n,n)
    for i in range(n):
        for j in range(i+1,n):
            D[i,j]=jaccard(ingDict[ingList[i]],ingDict[ingList[j]])
            D[j,i]=D[i,j]
            print i,j
    return D

##############################################################################
###Right here is where to change what table in the database to write into#####
##############################################################################
                                                                        
cursor=connection.cursor()
##Change db name to agree with parameters!##
FLAVOR='spicy_half_half_1000'
def writeDistances(id_list,D):
    '''
    id_list - list
    D - numpy array of distances
    '''
    for id_to in id_list:
        for id_from in id_list:
            distance=D[id_list.index(id_to),id_list.index(id_from)]
            cursor.execute('INSERT INTO flava_db.%s(row_id,id_to,id_from,dist) VALUES(NULL,%d,%d,%f)'%(FLAVOR,id_to,id_from,distance))
    return 'done'
    
    
