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

if __name__ == "__main__":
    app.run(debug=True, port=8000)