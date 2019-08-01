# A very simple Flask Hello World app for you to get started with...

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session.__init__ import Session
from tempfile import mkdtemp
# from mysite import db
import mysql.connector
from functools import wraps
# from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import pickle
import os.path
import oauth2client
from urllib import parse
import argparse
import sys
from oauth2client.file import Storage
from oauth2client.tools import run_flow

# import google.oauth2.credentials
import google_auth_oauthlib.flow
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import OAuth2WebServerFlow
# from __future__ import print_function
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
from oauth2client import file
# from oauth2client.contrib.keyring_storage import Storage

from oauth2client import client, tools, file
import httplib2
import json
import os

# from oauth2client import client
from googleapiclient import sample_tools
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from .ParsSZ import poshuk




app = Flask(__name__)
# app.config.from_object('app_config')
app.config["TEMPLATES_AUTO_RELOAD"] = True
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
SCOPES = ['https://www.googleapis.com/auth/calendar']
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'
CLIENT_SECRET_FILE = "/home/mprojekt/mysite/client_secret.json"
API_KEY_FILE_NAME = 'credentials.json'   # Name of json file you downloaded earlier
CALENDAR_ID = 'primary'
CREDS_FILENAME = 'credentials.json'

def database():
    mydb = mysql.connector.connect(
      host="mprojekt.mysql.pythonanywhere-services.com",
      user="mprojekt",
      passwd="19072019a",
      database="mprojekt$mpr"
    )
    return mydb
# cursor = mydb.cursor()
# sshtunnel.SSH_TIMEOUT = 5.0
# sshtunnel.TUNNEL_TIMEOUT = 5.0

# with sshtunnel.SSHTunnelForwarder(
#     ('ssh.pythonanywhere.com'),
#     ssh_username='mprojekt', ssh_password='19072019a',
#     remote_bind_address=('mprojekt.mysql.pythonanywhere-services.com', 3306)
# ) as tunnel:
#     mydb = mysql.connector.connect(
#         user='mprojekt', password='19072019a',
#         host='127.0.0.1', port=tunnel.local_bind_port,
#         database='mprojekt$mpr',
#     )
#     # Do stuff
#     cursor = mydb.cursor()
    # connection.close()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash("Спочатку зареєструйтесь")
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    db = database()
    cursor = db.cursor()
    if request.method == "POST":
        if not request.form.get("username"):
            flash("Введіть ім'я користувача")
            return redirect("/register")
        elif not request.form.get("password"):
            flash('Введіть пароль')
            return redirect("/register")

        elif not request.form.get("confirm"):
            flash('Введіть підтвердження пароля')
            return redirect("/register")

        elif request.form.get("password") != request.form.get("confirm"):
            flash('Пароль та підтвердження пароля повинні бути однакові')
            return redirect("/register")
        cursor.execute("SELECT id FROM users WHERE username = '%s'"
                       %request.form.get("username"))
        check = cursor.fetchall()
        if len(check)!=0:
            flash(f"Ім'я {request.form.get('username')} зайнято, виберіть інше ім'я користувача")
            return redirect("/register")

        password_hash = generate_password_hash(request.form.get("password"))
        cp = "INSERT INTO users(username, password) VALUES(%s,%s)"
        val = (request.form.get('username'), password_hash)
        cursor.execute(cp,val)
        db.commit()
        cursor.execute("SELECT * FROM users WHERE username = '%s'"
                              % request.form.get("username"))
        rows = cursor.fetchall()
        session["user_id"] = rows[0][0]
        session['username']=rows[0][1]
        flash(f"{request.form.get('username')} Ви успішно зареєструвались")
        db.close()
        return redirect("/")
    return render_template("signin.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    # if session:
    #     flash("Ви вже ввійшли")
    #     return redirect("/")
    db = database()
    cursor = db.cursor()
    if request.method == "POST":
        if not request.form.get("username"):
            flash("Введіть ім'я користувача")
            return redirect("/login")
        elif not request.form.get("password"):
            flash("Введіть пароль")
            return redirect("/login")
        cursor.execute("SELECT * FROM users WHERE username = '%s'"
                                % request.form.get("username"))
        rows = cursor.fetchall()
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            flash("Невірне ім'я користувача або пароль")
            return redirect("/login")

        session["user_id"] = rows[0][0]
        session['username'] = rows[0][1]
        global user
        user = rows[0][1]
        db.close()
        return redirect("/")


    return render_template("login.html")

@app.route("/logout")
def logout():
    """Вихід"""
    session.clear()
    return redirect("/")


@app.route("/google_auth")
@login_required
def auth():
    google_calendar()

    return redirect("/my_court")


@app.route("/my_court")
@login_required
def my_court():

    if session.get('calendar'):
        content = []
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        # return service
        events_result = google_calendar().events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        print(events)
        if not events:
            print('No upcoming events found.')
        for event in events:
            check = True
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'], event['description'])
            content.append(list((start, event['summary'], event['description'])))
        return render_template("court.html", content=content)
    return render_template("court.html")


@app.route("/about", methods=["GET", "POST"])
@login_required
def about():
    if request.method == "GET":
        return render_template("about.html")
    elif request.method=='POST':
        #list_data = []
        #list_data.clear()
        sud1 = request.form['sud']
        number1 = request.form['nomber']
        #list_data = [sud1, number1]
        sud2 = poshuk({'sud': sud1, 'number': number1})
        return render_template("about.html", nom=sud2)
    else:
        return("ok")


@app.route("/admin_db", methods=["GET", "POST"])
@login_required
def admin_bd():
    return render_template("admin_db.html")


if __name__ == '__main__':
    app.run()

