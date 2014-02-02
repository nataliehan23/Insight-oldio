#!/usr/bin/python
# Natalie's frontend control
import flask
from flask import Flask, render_template, request
app = Flask(__name__)
import MySQLdb
from backend import *
import json

app = Flask(__name__)
db = MySQLdb.connect(user="root", host="localhost", port=3306, db="reviews")


@app.route('/')
@app.route('/index')
def index():
    return flask.render_template('index.html')

@app.route('/search')
def search():
    keyword = request.args.get('musictitle')
    # keyword  = " " + keyword
    # json_data=open('/Users/natalie/Insight/myapp/djcloud/static/musiclist.json')
    # data = json.load(json_data)
    musics = recommender(keyword)
    modelids = ['modelid1', 'modelid2', 'modelid3','modelid4', 'modelid5']
    print "returning:...", len(musics)
    # json_data.close()
    # recmusic = data[:9]
    # titles,urls = [],[]
    # for m in recmusic:
    # 	titles.append(m[0])
    # 	urls.append(m[1])
    # print titles,urls
    return render_template('search.html', musics=musics, modelids = modelids)


@app.route('/slides.html')
def slides():
    return render_template('slides.html')

# @app.route("/db")
# def cities_page():
#     db.query("SELECT Name FROM city;")

#     query_results = db.store_result().fetch_row( maxrows=0 )
#     cities = ""
#     for result in query_results:
#         print result
#         # cities = cities + result[0]
#         cities += unicode( result[0], 'ISO-8859-1')
#         cities += "<br>"
#         #print result

#     return cities


@app.route('/<pagename>')
def regularpage(pagename=None):
	"""
	Route not found
	"""
	return "you've arriave at " + pagename

if __name__ == "__main__":
	app.debug=True
	app.run()
	# 
	# app.run(port=5001)