"""
Routes and views for the flask application.
"""
from __future__ import print_function
import tweepy
import json
from datetime import datetime
from flask import render_template, render_template, Response, request, redirect, url_for, session, Markup
from TwitterApiWebProject import app
import pymysql
import pymongo
import dns
from dateutil import parser
import json
from json2html import *
import pandas as pd
import time
import xlsxwriter
import xlrd
import unidecode
from plotly.offline import plot
from plotly.graph_objs import *

#WORDS = ['#bigdata', '#AI', '#datascience', '#machinelearning', '#ml', '#iot']
keyword = '' 
CONSUMER_KEY = "co3L9cuHZecZosLFpoYDIKKRg"
CONSUMER_SECRET = "4U3ZVNgVywsBqUqW1iRsOa9yc9duPN9Z3IDn7H6cfkntGGM2C3"
ACCESS_TOKEN = "1042846189459255296-sC6ReCF80DGqRVknmXOMc3CZAvCsIM"
ACCESS_TOKEN_SECRET = "8Uq0IJHBeum39IlrA753cCwOGDyb7QURfCvDg1bcxfi0x"
count = 0
insert_query_Twitter = "INSERT INTO TWITTER (tweet_id, screen_name, created_at, text, SEARCHKEYWORD_ID) VALUES "
keywordid = 0
json_data = []
row=0
col=0
count=0
login = {}
workbook = xlsxwriter.Workbook('tweet.csv')
worksheet = workbook.add_worksheet()
timeToSearch = 0.0
mongoStartTime = 0.0
mongoEndTime = 0.0
mysqlStartTime = 0.0
mySqlEndTime = 0.0
numberOfRecords = 0
searchkeywordid = 0

#specify your database server credentials#
login['host'] = 'localhost'
login['username'] = 'Lokesh'
login['password'] = '12345'
login['database'] = 'twitterdatabase'
#excel sheet file path#########################
excel_file_path  = 'tweet.csv'


def get_cursor():
    
    try:
        conn = pymysql.connect(host="localhost", user="Lokesh", passwd="12345", db="twitterdatabase", charset="utf8")
        return conn,conn.cursor()
    except:
        print ('Database connection failed!')
        return None

def store_timeresults(timeMongo, timeSql, keywordid, numberofrecords):
    try:
        db=pymysql.connect(host="localhost", user="Lokesh", passwd="12345", db="twitterdatabase", charset="utf8")
        cursor = db.cursor()
        insert_query = "INSERT INTO RESULTS (SEARCHKEYWORDID, MONGO_TIME,MYSQL_TIME,NUMBEROFRECORDS) VALUES (%s,%s,%s,%s)"
        cursor.execute(insert_query,(keywordid,timeMongo,timeSql,numberofrecords))
        db.commit()
        cursor.close()
        db.close()
        return True
    except:
        print ('Database connection failed!')
        return False


def store_data_mysql():

    conn,cursor = get_cursor()
    #conn.set_character_set('utf8')
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')

    workbook = xlrd.open_workbook(excel_file_path)
    worksheet = workbook.sheet_by_name('Sheet1')

    nrows = worksheet.nrows


    print (nrows)
    for each in range(0,nrows):
        print ('###############')
        print ('row '+ repr(each) + ' inserted')
        print ('###############')
        screen_name = worksheet.row(each)[0].value#Screen name
        #company_type = "consulate" #fixed string
        text = unidecode.unidecode(worksheet.row(each)[1].value)# Text
        text = mdb.escape_string(text)
        created_at = datetime.datetime.now()# Created at
        tweet_id = worksheet.row(each)[3].value #Tweet Id

        query = """insert into TWITTER (SCREEN_NAME,TEXT,CREATED_AT,TWEET_ID) values ("%s","%s","%s","%s")"""%(screen_name, text, created_at, tweet_id)

        cursor.execute(query)
        conn.commit()
    return

def store_data_mongo(data):
    client = pymongo.MongoClient("mongodb+srv://Lokesh_Gupta:Lokesh123@cluster0-hyzek.mongodb.net/test?retryWrites=true")
    db = client['TwitterDatabase']
    db.Tweets.insert(json_data)


class StreamListener(tweepy.StreamListener):    
    #This is a class provided by tweepy to access the Twitter Streaming API. 
    def __init__(self, time_limit=timeToSearch):
        self.start_time = time.time()
        time_limit = timeToSearch
        self.limit = time_limit
        #self.saveFile = open('abcd.json', 'a')
        super(StreamListener, self).__init__()

    def on_connect(self):
        # Called initially to connect to the Streaming API
        print("You are now connected to the streaming API.")
 
    def on_error(self, status_code):
        # On error - if an error occurs, display the error / status code
        print('An Error has occured: ' + repr(status_code))
        return False
 
    def on_data(self, data):
        #This is the meat of the script...it connects to your mongoDB and stores the tweet
        try:
            if (time.time() - self.start_time) < self.limit:
                global row
                #client = MongoClient(MONGO_HOST)
                
            # Decode the JSON from Twitter
                datajson = json.loads(data)
                text = datajson['text']
                " ".join(text.split())
                screen_name = datajson['user']['screen_name']
                tweet_id = datajson['id']
                created_at = datajson['created_at']
                created_at = parser.parse(datajson['created_at'])
                created_at_new=created_at.replace(tzinfo=None)
                worksheet.write(row, col, screen_name)
                worksheet.write(row, col + 1, text)
            #format2 = workbook.add_format({'num_format': 'dd:mm:yy'})
                worksheet.write(row, col + 2, created_at_new)
                worksheet.write(row, col + 3, tweet_id)
                row += 1
            #print out a message to the screen that we have collected a tweet
                print("Tweet collected at " + str(created_at))

                global json_data
                data = {}
                data['text'] = text
                data['screen_name'] = screen_name
                data['id'] = tweet_id
                data['created_at'] = str(created_at)
                json_data.append(data)
            else:
                global mongoEndTime
                global mongoStartTime
                global mySqlEndTime
                global mysqlStartTime
                global numberOfRecords
                mongoStartTime = time.time()
                store_data_mongo(json_data)
                mongoEndTime = time.time()
                print("Mongo DB took " + str((mongoEndTime - mongoStartTime)) + "seconds to store " + str((len(json_data))))
                numberOfRecords = len(json_data)
                #Call store mysql function
                mysqlStartTime = time.time()
                #store_data_mysql()
                mySqlEndTime = time.time()
                timeMongo = mongoEndTime - mongoStartTime
                timemysql = 30.0 # replace the code gere for calling mysql code
                store_timeresults(timeMongo,timemysql,searchkeywordid,numberOfRecords)
                #store_data_mysql()
                #workbook.close()
                return False
        except Exception as e:
           print(e)

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Please Login',
        message = 'Enter you credentials',
        year=datetime.now().year,
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/RunApi')
def RunApi():
    """Renders the about page."""
    db=pymysql.connect(host="localhost", user="Lokesh", passwd="12345", db="twitterdatabase", charset="utf8")
    cursor = db.cursor()
    if str(session["userrole"]) == "Admin":
        select_query = "SELECT SEARCHKEYWORD_ID AS 'SEARCH KEYWORD ID', SEARCH_TEXT AS 'SEARCH TEXT', SEARCH_AT AS 'SEARCHED AT',USER_ID AS 'USER ID' FROM SEARCHKEYWORD ORDER BY SEARCH_AT DESC"
        cursor.execute(select_query)
    else:
        select_query = "SELECT SEARCHKEYWORD_ID AS 'SEARCH KEYWORD ID', SEARCH_TEXT AS 'SEARCH TEXT', SEARCH_AT AS 'SEARCHED AT',USER_ID AS 'USER ID' FROM SEARCHKEYWORD WHERE USER_ID = %s ORDER BY SEARCH_AT DESC"
        cursor.execute(select_query,(str(session["userid"])))
    
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    rv = cursor.fetchall()
    json_data=[]
    for result in rv:
        json_data.append(dict(zip(row_headers,result)))
    #display = json2html.convert(json = json_data)
    return render_template(
        'ReadTweets.html',
        title='Read Tweets',
        year=datetime.now().year,
        username=session["username"],
        data = json2html.convert(json = json_data, table_attributes="id=\"searchTable\" border=\1\"")
    )

@app.route('/RunTwitterApi', methods=['GET', 'POST'])
def RunTwitterApi():
    global keyword
    global timeToSearch
    global searchkeywordid
    keyword = request.form["keyword"]
    timeToSearch = float(request.form["time"])
    timeToSearch = timeToSearch * 60
    db=pymysql.connect(host="localhost", user="Lokesh", passwd="12345", db="twitterdatabase", charset="utf8")
    cursor = db.cursor()
    insert_query = "INSERT INTO SEARCHKEYWORD (SEARCH_TEXT, SEARCH_AT,USER_ID) VALUES (%s, CURRENT_TIMESTAMP,%s)"
    cursor.execute(insert_query,(keyword,str(session["userid"])))
    db.commit()
    select_query = "SELECT SEARCHKEYWORD_ID FROM SEARCHKEYWORD WHERE USER_ID = %s and SEARCH_TEXT = %s ORDER BY SEARCH_AT DESC"
    cursor.execute(select_query,(str(session["userid"]),keyword))
    result = cursor.fetchone()
    searchkeywordid = int(result[0])
    insert_query = "INSERT INTO SEARCHHISTORY (USER_ID,SEARCHKEYWORD_ID,CREATED_AT) VALUES(%s,%s,CURRENT_TIMESTAMP)"
    cursor.execute(insert_query,(str(session["userid"]),str(searchkeywordid)))
    db.commit()
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    #workbook = xlsxwriter.Workbook('tweet.csv')
    #worksheet = workbook.add_worksheet()
    #Set up the listener. The 'wait_on_rate_limit=True' is needed to help with Twitter API rate limiting.
    #listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True)) 
    listener = StreamListener()
    streamer = tweepy.Stream(auth=auth, listener=listener)
    #print("Tracking: " + str(WORDS))
    #keyword = request.form["keyword"]
    streamer.filter(track= keyword)
    return redirect(url_for('DisplayResults'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        db=pymysql.connect(host="localhost", user="Lokesh", passwd="12345", db="login", charset="utf8")
        username = request.form["username"]
        password = request.form["password"]
        cursor = db.cursor()
        select_query = "select * from user where USER_NAME = %s and PASSWORD = %s"
        cursor.execute(select_query, (username,password))
        row = cursor.fetchall()
        if cursor.rowcount != 0:
            #print("User Valid")
            #do routing to landing page
            flag = True
            roleid = row[0][3]
            role_query = "select ROLE_NAME from role where Role_id = %s"
            cursor.execute(role_query, (roleid))
            message = "User Authenticated"
            session["userid"] = row[0][0]
            session["username"] = row[0][1]
            session["userrole"] = cursor.fetchall()[0][0]
            cursor.close()
            db.close()
            return redirect(url_for('RunApi'))
        else:
            flag = False
            message1 = "Username or Password invalid. Please try again."
            cursor.close()
            db.close()
            return render_template('index.html',
                 title='Please Login',
                 message = 'Enter you credentials',
                 loginmessage = message1,
                 year=datetime.now().year,)
        
    except Exception as e:
        print(e)
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # remove the username from the session if it is there
    session.pop('userid', None)
    session.pop('username', None)
    session.pop('userrole', None)
    return redirect(url_for('home'))

@app.route('/getTweets',methods=['GET','POST'])
def getTweets():
    data = request.form['keyword']
    db=pymysql.connect(host="localhost", user="Lokesh", passwd="12345", db="twitterdatabase", charset="utf8")
    cursor = db.cursor()
    select_query = "SELECT TWEET_ID AS 'TWEET ID', SCREEN_NAME AS 'SCREEN NAME', CREATED_AT AS 'TWEET CREATED AT', TEXT, SEARCHKEYWORD_ID AS 'SEARCHKEYWORDID' FROM TWITTER WHERE SEARCHKEYWORD_ID = %s"
    cursor.execute(select_query,(data))
    row_headers=[x[0] for x in cursor.description] #this will extract row headers
    rv = cursor.fetchall()
    cursor.close()
    db.close()
    json_data=[]
    for result in rv:
        json_data.append(dict(zip(row_headers,result)))

    return json2html.convert(json = json_data, table_attributes="id=\"twitterResult\" border=\1\"")

@app.route('/DisplayResults')
def DisplayResults():
    db=pymysql.connect(host="localhost", user="Lokesh", passwd="12345", db="twitterdatabase", charset="utf8")
    cursor = db.cursor()
    select_query = "SELECT SEARCHKEYWORD_ID,SEARCH_TEXT FROM SEARCHKEYWORD WHERE USER_ID = %s ORDER BY SEARCHKEYWORD_ID DESC"
    cursor.execute(select_query,(str(session["userid"])))
    rv = cursor.fetchall()
    keywordiddata=[]
    keyword=[]

    for result in rv:
        keywordiddata.append(str(result[0]))
    

    format_strings = ','.join(['%s'] * len(keywordiddata))
    cursor.execute("SELECT SEARCHKEYWORDID, MONGO_TIME, MYSQL_TIME, NUMBEROFRECORDS FROM RESULTS WHERE SEARCHKEYWORDID IN (%s) ORDER BY RESULTID DESC LIMIT 4" % format_strings,tuple(keywordiddata))
    rv = cursor.fetchall()
    numberofrecords=[]
    mongotimes=[]
    mysqltimes=[]
    for result in rv:
        numberofrecords.append(int(result[3]))
    for result in rv:
        mongotimes.append(float(result[1]))
    for result in rv:
        mysqltimes.append(float(result[2]))
    for result in rv:
        keywordiddata.append(str(result[0]))
    format_strings = ','.join(['%s'] * len(keywordiddata))
    cursor.execute("SELECT SEARCH_TEXT FROM SEARCHKEYWORD WHERE SEARCHKEYWORD_ID IN (%s) ORDER BY SEARCHKEYWORD_ID DESC LIMIT 4" % format_strings,tuple(keywordiddata))
    rv = cursor.fetchall()
    for result in rv:
        keyword.append(str(result[0]))
    trace1 = Scatter(
        x=numberofrecords,
        y=mongotimes,
        name='Mongo DB',
        connectgaps=True
        )
    trace2 = Scatter(
        x=numberofrecords,
        y=mysqltimes,
        name='MySQL DB',
        connectgaps=True
        )
    #trace1 = Bar(
    #x=numberofrecords,
    #y=mongotimes,
    #name='Mongo DB',
    #width = [1.5, 1.5, 1.5, 1.5],
    #marker=dict(
    #    color='rgb(49,130,189)'
    #)
    #)
    #trace2 = Bar(
    #x=numberofrecords,
    #y=mysqltimes,
    #name='MySQL DB',
    #width = [1.5, 1.5, 1.5, 1.5],
    #text = keyword,
    #marker=dict(
    #    color='rgb(204,204,204)'
    #)
    #)

    data = [trace1, trace2]
    layout = Layout(
    title='Comparision between Times',
    xaxis=dict(
        title='Number of Records(in thousands)',
    ),
    yaxis=dict(
        title='Time(in Seconds)',
    ),
    barmode='group'
    )

    fig = Figure(data=data, layout=layout)
    #my_plot_div = plot([Bar(x=numberofrecords, y=mongotimes,name="Mongo DB")], output_type='div')
    my_plot_div = plot(fig, output_type='div')
    return render_template('results.html',
                               div_placeholder=Markup(my_plot_div)
                              )