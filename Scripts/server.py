import os
import sys
from os.path import join, dirname, realpath

import flask
from flask import Flask, redirect, url_for, render_template, request, send_from_directory, flash, session
from werkzeug.utils import secure_filename
from flask_session import Session
import json
import pandas as pd
from extract_csv import extract_data
from Visualizations import *
import numpy as np
import asyncio
import time
import threading

upload_folder = join(dirname(realpath(__file__)), 'csv_files/')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = upload_folder
app.config['UPLOAD_EXTENSIONS'] = ['.csv']

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

uploadedFileName = []
csvFilesPos = []
csvFilesUserName = []

PEOPLE_FOLDER = os.path.join('static', 'people_photo')

#app = Flask(__name__)
#app.config['PHOTO_FOLDER'] = PEOPLE_FOLDER



@app.route('/set/')
def set():
    session['key'] = 'value'
    return 'ok'

@app.route('/get/')
def get():
    return session.get('key', 'not set')

@app.route("/")  # Here the main page is defined
def home():
    return render_template("Indexpage.html")

@app.route("/<name>")               # This allows the user to go to different pages instead of the homepage
def user(name):                     # essentially it takes .../x the x as input and loads file x (for example: 127.0.0.1:5000/Indexpage.html loads Indexpage.html)
    return render_template({name}, Arraynames = csvFilesUserName)

# @app.route("/admin")  # This can be used to redirect user (for example now it redirects url/admin to url.)
# def admin():          # not very relevant for us yet.
#     return redirect(url_for("home"))

@app.route("/Indexpage", methods=['GET', 'POST'])    # Check for current page if there are HTML forms with the methods Get and Post
def testbutton():                           #Function you want to define in the HTML form
    if request.method == "POST":            #Check if form method was post
        pong = "PONG"
        return render_template("Indexpage.html", testvariable = pong)              #Type pong on site
    else:
        return "Did not work"

@app.route('/Groupinfo.html')
def show_people():
    full_filename = os.path.join(app.config['PHOTO_FOLDER'], 'Naomi_Han.jpg')
    return render_template("Groupinfo.html", user_image=full_filename)

@app.route('/upload_file', methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        uploadname = request.form['fileName']
        uploaded_file = request.files['file']                   #Get the file from the request
        filename = secure_filename(uploaded_file.filename)      #Check if someone didnt do something weird with the file

        if filename != '':                                      #Check if filename is not empty
            file_ext = os.path.splitext(filename)[1]                #Split the extensions
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:     #Check if it is a valid extension
                flash("This extension is not supported")
                return render_template('Visualisation.html', Arraynames=csvFilesUserName)

            if filename in uploadedFileName:
                flash("This file is already uploaded")
                return render_template('Visualisation.html', Arraynames=csvFilesUserName)
            if uploadname in csvFilesUserName:
                flash("This name has already been used")
                return render_template('Visualisation.html', Arraynames=csvFilesUserName)
            csvFilesUserName.append(uploadname) #Add the upload name to the array
            csvFilesPos.append(os.path.join(app.config['UPLOAD_FOLDER'], filename)) #upload the path to the array
            uploadedFileName.append(filename) #upload the file to the uploaded files
            uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) #upload file to correct position
            return render_template('Visualisation.html', Arraynames = csvFilesUserName)

    return render_template('Visualisation.html', Arraynames = csvFilesUserName)

@app.route('/getData', methods=['GET','POST'])
def getData():

    if request.method == 'POST':
        fileSelect = request.form.get('File-Dropdown') #Get which files the person selected
        filePath = "" #create an empty path
        if fileSelect in csvFilesUserName: #Check if the selected file was uploaded
            # Get the index of the selected file and add the filepath to the variable
            index = csvFilesUserName.index(fileSelect)
            filePath = csvFilesPos[index]

        #Get the data from the csv file
        data = extract_data(filePath)

        #Process data asynchronous
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()

        # HERE YOU CAN RETRIEVE NEW DATA FROM THE SHEET
        # ADD THE VARIABLE IN THE LINES BELOW AND RETURN IT AS var1 = var1
        # THEN ON THE HTML FILES YOU CAN LOAD {{ var1 }} as value in graphs/plots
        barchart_data = 0  # loop.run_until_complete(makeGraphs(data)) not loaded because it makes the site too slow
        forcegraph_data = loop.run_until_complete(forceDirectedGraph(data))



        #print(makeMatrix(data),sys.stderr)
        #print(makeGraphs(data),sys.stderr)
    return render_template('Visualisation.html',Arraynames = csvFilesUserName, barchart_data = barchart_data,
                           forcegraph_data = forcegraph_data)


if __name__ == "__main__":
    app.run(debug=True)
