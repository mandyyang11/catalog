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


# show category items
@app.route('/catalog/<catalog_name>/items')
def showCategory(catalog_name):
    categories = session.query(Category)

    # check whether catalog_name is in the database
    valid_name = categories.filter(Category.name == catalog_name).count()
    if valid_name == 1:
        items = (
            session.query(Item)
            .join(Category)
            .filter(Category.name == catalog_name)
            )

        # check if the user is logged in and display the page accordingly
        if 'username' not in login_session:
            return render_template('category_page_public.html',
                                   items=items,
                                   categories=categories,
                                   current_category=catalog_name)
        else:
            return render_template('category_page_private.html',
                                   items=items,
                                   categories=categories,
                                   current_category=catalog_name,
                                   user=login_session['username'])
    else:

        # if catalog name invalid, redirect back to
        # home and flash the error message
        flash("catalog name invalid, please check your url")
        return redirect(url_for('homepage'))


# show a specific item
@app.route('/catalog/<catalog_name>/<item_name>')
def showItem(catalog_name, item_name):

    # check whether catalog_name and item_name are in the database
    valid_item = (
        session.query(Item)
        .join(Category)
        .filter(Category.name == catalog_name)
        .filter(Item.name == item_name)
        )
    if valid_item.count() == 1:
        valid_item = valid_item.one()

        if 'username' in login_session:
            if valid_item.user.name == login_session['username']:
                # only show edit and delete option if the user
                # is both logged in and is the owner
                return render_template('item_page_private.html',
                                       item_description=valid_item.description,
                                       item_name=valid_item.name,
                                       category_name=valid_item.category.name,
                                       user=login_session['username'],
                                       owner_check=True)
            else:
                return render_template('item_page_private.html',
                                       item_description=valid_item.description,
                                       item_name=valid_item.name,
                                       category_name=valid_item.category.name,
                                       user=login_session['username'],
                                       owner_check=False)
        else:
            return render_template('item_page_public.html',
                                   item_description=valid_item.description,
                                   item_name=valid_item.name)
    else:

        # if either names invalid, redirect back to
        # home and flash the error message
        flash("catalog name and/or item_name invalid, please check your url")
        return redirect(url_for('homepage'))


# Create a new item
@app.route('/item/new/', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        current_user = (
            session.query(User)
            .filter(User.name == login_session['username'])
            .one()
            )
        current_category = (
            session.query(Category)
            .filter(Category.name == request.form['category'])
            .one()
            )

        # check if the item is not yet in the database
        valid_item = (
            session.query(Item)
            .join(Category)
            .filter(Category.name == request.form['category'])
            .filter(Item.name == request.form['title'])
            )
        if valid_item.count() == 0:
            new_item = Item(user=current_user,
                            name=request.form['title'],
                            description=request.form['description'],
                            category=current_category)
            session.add(new_item)
            session.commit()
            flash('New Item %s Successfully Created' % new_item.name)
            return redirect(url_for('homepage'))
        else:

            # in the case when its duplicated,
            # redirect to homepage and flash error message
            flash('New Item Fail to Create! %s is Duplicated'
                  % request.form['title'])
            return redirect(url_for('homepage'))
    else:
        categories = session.query(Category).all()
        return render_template('new_item.html',
                               categories=categories,
                               page_title='New',
                               user=login_session['username'])


# Edit an item
@app.route('/item/edit/<catalog_name>/<item_name>', methods=['GET', 'POST'])
def editItem(catalog_name, item_name):

    # check whether catalog_name and item_name are in the database
    current_valid_item = (
        session.query(Item)
        .join(Category)
        .filter(Category.name == catalog_name)
        .filter(Item.name == item_name)
        )
    if current_valid_item.count() == 1:
        editedItem = current_valid_item.one()
        if 'username' not in login_session:
            return redirect('/login')
        if editedItem.user.name != login_session['username']:

            # only the owner can edit the item
            flash('Only The Owner Can Edit The Item!')
            return redirect(url_for('homepage'))
        if request.method == 'POST':
            current_category = (
                session.query(Category)
                .filter(Category.name == request.form['category'])
                .one()
                )

            # check if the item is not yet in the database
            valid_item = (
                session.query(Item)
                .join(Category)
                .filter(Category.name == request.form['category'])
                .filter(Item.name == request.form['title'])
                )
            if valid_item.count() == 0:
                editedItem.name = request.form['title']
                editedItem.description = request.form['description']
                editedItem.category = current_category
                session.add(editedItem)
                session.commit()
                flash('Item Successfully Edited')
                return redirect(url_for('homepage'))
            else:

                # in the case when its duplicated,
                # redirect to homepage and flash error message
                flash('Item Fail to Edit! %s is Duplicated'
                      % request.form['title'])
                return redirect(url_for('homepage'))
        else:
            categories = session.query(Category).all()
            return render_template('new_item.html',
                                   categories=categories,
                                   page_title="Edit",
                                   user=login_session['username'])
    else:

        # if either names invalid, redirect back to
        # home and flash the error message
        flash("catalog name and/or item_name invalid, please check your url")
        return redirect(url_for('homepage'))


# Delete an item
@app.route('/item/delete/<catalog_name>/<item_name>', methods=['GET', 'POST'])
def deleteItem(catalog_name, item_name):

    # check whether catalog_name and item_name are in the database
    current_valid_item = (
        session.query(Item)
        .join(Category)
        .filter(Category.name == catalog_name)
        .filter(Item.name == item_name)
        )
    if current_valid_item.count() == 1:
        itemToDelete = current_valid_item.one()
        if 'username' not in login_session:
            return redirect('/login')
        if itemToDelete.user.name != login_session['username']:

            # only the owner can delete the item
            flash('Only The Owner Can Delete The Item!')
            return redirect(url_for('homepage'))
        if request.method == 'POST':
            deleted_name = itemToDelete.name
            session.delete(itemToDelete)
            session.commit()
            flash('%s Item Successfully Deleted' % deleted_name)
            return redirect(url_for('homepage'))
        else:
            categories = session.query(Category).all()
            return render_template('delete_item.html',
                                   user=login_session['username'])
    else:
        # if either names invalid, redirect back to
        # home and flash the error message
        flash("catalog name and/or item_name invalid, please check your url")
        return redirect(url_for('homepage'))


# Json api for all catalogy data
@app.route('/catalog.json')
def catalog_json():

    # constructing a output structure similar to the sample
    j = {"catalog": []}
    categories = session.query(Category).all()
    for i in xrange(len(categories)):
        j["catalog"].append({})
        j["catalog"][i]["id"] = categories[i].id
        j["catalog"][i]["name"] = categories[i].name

    items = session.query(Item).all()
    for i in xrange(len(items)):
        tmp = {"cat_id": items[i].category_id,
               "description": items[i].description,
               "id": items[i].id,
               "title": items[i].name}
        if "Item" in j["catalog"][items[i].category_id-1]:
            j["catalog"][items[i].category_id-1]["Item"].append(tmp)
        else:
            j["catalog"][items[i].category_id-1]["Item"] = [tmp]

    return jsonify(j)


# Json api for arbitrary item
@app.route('/api/<catalog_name>/<item_name>')
def item_json(catalog_name, item_name):

    # check whether catalog_name and item_name are in the database
    valid_item = (
        session.query(Item)
        .join(Category)
        .filter(Category.name == catalog_name)
        .filter(Item.name == item_name)
        )
    if valid_item.count() == 1:
        item = valid_item.one()
        j = {"item": {"id": item.id,
                      "name": item.name,
                      "description": item.description,
                      "user": {"user_id": item.user.id,
                               "user_name": item.user.name,
                               "user_email": item.user.email},
                      "category": {"cat_id": item.category.id,
                                   "cat_name": item.category.name}}}
        return jsonify(j)

    else:

        # if either names invalid, redirect back to
        # home and flash the error message
        flash("catalog name and/or item_name invalid, please check your url")
        return redirect(url_for('homepage'))


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(string.ascii_uppercase +
                      string.digits) for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code, now compatible with Python3
    request.get_data()
    code = request.data.decode('utf-8')

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps("""Current user
                                is already connected."""),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    flash("you are now logged in as %s" % login_session['username'])
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
