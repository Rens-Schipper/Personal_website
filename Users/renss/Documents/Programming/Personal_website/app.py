    # -*- coding: utf-8 -*-
"""
Created on Thu May 25 16:59:08 2023

@author: renss

.\Scripts\Activate.ps1
to exit type deactivate in terminal


set FLASK_APP=app.py
$env:FLASK_DEBUG = "1"
flask run

git add .
git commit -m master/other branch
git push -u origin master

pip freeze > requirements.txt

"""

from flask import Flask, render_template, url_for
import os
import pandas as pd
import ast

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title = "check")

@app.route("/test")
def test():
    return render_template("test.html", title = "test")

@app.route("/miranda")
def miranda():
    imgs = []
    for i in range(84):
        imgs.append(f"travel_map_{i}")

    
    df = pd.read_csv("./static/data/miranda_travels.csv", delimiter = "|")
    stories = df["description"].dropna().tolist()
    titles = df["title"].dropna().tolist()
    cities = df.dropna(subset = ["title"])["city"].tolist()
    dates = df.dropna(subset = ["title"])["date"].tolist()
    people_bools = df.dropna(subset = ["title"])["people"].notnull().tolist()
    people = df.dropna(subset = ["title"])["people"].apply(lambda x: ast.literal_eval(x)).tolist()

    wiki_df = pd.read_csv("./static/data/wiki.csv", delimiter = "|")
    wiki_df["wiki_link"] = wiki_df["wiki_link"].replace('"', '', regex=True).replace(' ', '', regex=True)
    return render_template("miranda.html", title = "The life of Fransisco de Miranda.", images = imgs, stories = stories, cities = cities, dates = dates, titles = titles, people = people, people_bools = people_bools, wiki_df = wiki_df)

import asyncio

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.embed import server_document
from bokeh.server.server import BaseServer
from bokeh.server.tornado import BokehTornado
from bokeh.server.util import bind_sockets
from when2leap import modify_doc
#from usa_demographic_clustering import modify_doc

# can't use shortcuts here, since we are passing to low level BokehTornado
bkapp = Application(FunctionHandler(modify_doc))

# This is so that if this app is run using something like "gunicorn -w 4" then
# each process will listen on its own port
sockets, port = bind_sockets("localhost", 5006)

@app.route('/election_analysis', methods=['GET'])
def bkapp_page():
    script = server_document('http://localhost:5006/bkapp')
    return render_template("election_analysis.html", script=script, template="Flask")
    #return render_template("usa_demo_clustering.html", script=script, template="Flask")

def bk_worker():
    asyncio.set_event_loop(asyncio.new_event_loop())

    bokeh_tornado = BokehTornado({'/bkapp': bkapp}, extra_websocket_origins=["localhost:5000","localhost:5006","localhost:8000"])
    bokeh_http = HTTPServer(bokeh_tornado)
    bokeh_http.add_sockets(sockets)

    server = BaseServer(IOLoop.current(), bokeh_tornado, bokeh_http)
    server.start()
    server.io_loop.start()

from threading import Thread
Thread(target=bk_worker).start()

if __name__ == "__main__":
    app.run(debug=True, port=8000)