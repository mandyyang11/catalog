from flask import (Flask, render_template,
                   request, redirect, jsonify, url_for, flash)
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///CategoryItem.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# displays all categories along with the latest items
# number of latest items is bounded by the number of categories
@app.route('/')
def homepage():
    categories = session.query(Category)
    latest_items = (
        session.query(Item)
        .order_by(desc(Item.id))
        .limit(categories.count())
        )

    # check if the user is logged in and display the page accordingly
    if 'username' not in login_session:
        return render_template('homepage_public.html',
                               categories=categories,
                               latest_items=latest_items)
    else:
        return render_template('homepage_private.html',
                               categories=categories,
                               latest_items=latest_items,
                               user=login_session['username'])


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
