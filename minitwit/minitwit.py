# -*- coding: utf-8 -*-
"""
    MiniTwit
    ~~~~~~~~
    A microblogging application written with Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import urllib2
import base64
from functools import wraps
import time
import sys
import os
from sqlite3 import dbapi2 as sqlite3
from flask_pymongo import PyMongo

from hashlib import md5
from datetime import datetime
from flask import Flask, json, jsonify, request, session, url_for, redirect, \
    render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash
from flask import Response, current_app, request
from flask.ext.api import status
from flask_sessionstore import Session
import hashlib
#from flask_sqlalchemy import SQLAlchemy
from flask_basicauth import BasicAuth
from flask_httpauth import HTTPBasicAuth
from pymongo import MongoClient
from bson.objectid import ObjectId

import cPickle
import pickle

import redis


# configuration
DATABASE = '/tmp/minitwit.db'
PER_PAGE = 30
DEBUG = False
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'

# create our little application :)
app = Flask('minitwit')
app.config.from_object(__name__)
client = MongoClient('localhost')
mongo = PyMongo(app)  # MONGO CODE
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY='development key'))
REDIS_URL = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/minitwit.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#app.config['SESSION_TYPE'] = 'sqlalchemy'
session_newvar = Session(app)
redis_obj = redis.from_url(REDIS_URL)

R_SERVER = redis.Redis("localhost")

# if app.config.get('SESSION_TYPE', None) == 'sqlalchemy':
#    session_newvar.app.session_interface.db.create_all()

#
# @app.route('/set', methods=['POST'])
# def set_val():
#   flask.session['value'] = flask.request.form['value']
#   return 'value set'
#
# @app.route('/get')
# def get():
#    return flask.session['value']
#
# @app.route('/delete', methods=['POST'])
# def delete():
#    del flask.session['value']
#    return 'value deleted'

# def get_db():
# #     """Opens a new database connection if there is none yet for the
# #     current application context.
# #     """
# #     # top = _app_ctx_stack.top
# #     # if not hasattr(top, 'sqlite_db'):
# #     #     top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
# #     #     top.sqlite_db.row_factory = sqlite3.Row
# #     # return top.sqlite_db
# #
# #     print "CLient", client
#       db = mongo.minitwit
# #     print "db",db
#       return db


@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    # top = _app_ctx_stack.top
    # if hasattr(top, 'sqlite_db'):
    #     top.sqlite_db.close()
    client.close()


# def init_db():
#     """Initializes the database."""
#     db = get_db()
#     with app.open_resource('schema.sql', mode='r') as f:
#         db.cursor().executescript(f.read())
#     db.commit()


def populate_db():
    """filling database"""
    # db = get_db()
   # print db
    # with app.open_resource('populatemongo.json', mode='r') as f:
    # db.cursor().executescript(f.read())
    # db.commit()
    #users= db.users
    os.system("sh populatedb.sh")


#
# @app.cli.command('initdb')
# def initdb_command():
#     """Creates the database tables."""
#     init_db()
#     print('Initialized the database.')

@app.cli.command('populatedb')
def populatedb_command():
    """insert values."""
    print('entered populate')
    populate_db()
    print('inserting values to db')


# def query_db(query, args=(), one=False):
#     """Queries the database and returns a list of dictionaries."""
    #db =client
    # cur = get_db().execute(query, args)
    # rv = cur.fetchall()
    # return (rv[0] if rv else None) if one else rv


def get_user_id(username):
    """Convenience method to look up the id for a username."""
    # rv = query_db('select user_id from user where username = ?',
    #               [username], one=True)
    # return rv[0] if rv else None
    # db = get_db()
    # print "LOOKHERE UID"
    rv = mongo.db.users.find_one({'username': username}, {'_id': []})
    print rv['_id']
    return rv['_id'] if rv else None


def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return 'https://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        # g.user = query_db('select * from user where user_id = ?',
        #[session['user_id']], one=True)
        # db = get_db()
        g.user = mongo.db.users.find_one({'_id': session['user_id']})


'''
/********************************/
        REFACTORING DB
/********************************/
'''


def query():
    # messages=query_db('''
    #    select message.*, user.* from message, user
    #    where message.author_id = user.user_id and (
    #        user.user_id = ? or
    #        user.user_id in (select whom_id from follower
    #                                where who_id = ?))
    #    order by message.pub_date desc limit ?''',
    #    [g.user, g.user, PER_PAGE])
    followed = mongo.db.users.find_one(
        {'_id': g.user['_id']}, {'follows': 1})
    if followed is None:
        followed = {'follows': []}
    messages = mongo.db.message.find(
        {'$or': [
            {'author_id': session['user_id']},
            {'author_id': {'$in': followed['follows']}}
        ]}).sort('pub_date', -1)

    return list(messages)


def public_timeline_query():
    # messages = query_db('''
    #     select message.*, user.* from message, user
    #     where message.author_id = user.user_id
    #     order by message.pub_date desc limit ?''', [PER_PAGE])
    # db = get_db()
    messages = mongo.db.message.find().sort('pub_date', -1)
    #messages = json.loads(messages)

    return list(messages)


def user_query(profile_user):
    # messages=query_db('''
    #         select message.*, user.* from message, user where
    #         user.user_id = message.author_id and user.user_id = ?
    #         order by message.pub_date desc limit ?''',
    #         [profile_user['user_id'], PER_PAGE])

    messages = mongo.db.message.find(
        {'author_id': profile_user['_id']}).sort('pub_date', -1)
    return list(messages)


def follow_query(whom_id):
    # db = get_db()
    # db.execute('insert into follower (who_id, whom_id) values (?, ?)',[g.user[0], whom_id])
    # db.commit()
    mongo.db.users.update({'_id': g.user[0]}, {'$push': {'follows': whom_id}})


def unfollow_query(whom_id):
    # db = get_db()
    # db.execute('delete from follower where who_id=? and whom_id=?',
    #           [g.user[0], whom_id])
    # db.commit()
    mongo.db.users.update({'_id': g.user[0]}, {'$pull': {'follows': whom_id}})


def userdetails_API_query(username):
    # user = query_db('''select * from user where
    #             username = ?''', [username], one=True)

    user = mongo.db.users.find_one({'username': username})
    return user


def add_message_query():
    # db = get_db()
    # db.execute('''insert into message (author_id, text, pub_date)
    #       values (?, ?, ?)''', (g.user[0], request.form['text'],
    #                             int(time.time())))
    # db.commit()

    user = mongo.db.users.find_one(
        {'_id': g.user['_id']}, {'email': [], 'username': []})
    print "add message", user
    mongo.db.message.insert(
        {'author_id': session['user_id'],
         'email': user['email'],
         'username': user['username'],
         'text': request.form['text'],
         'pub_date': int(time.time())})


def userdetails_query():
    # user = query_db('''select * from user where
    #            username = ?''', [request.form['username']], one=True)
    # db=get_db()
    user = mongo.db.users.find_one({'username': request.form['username']})
    return user


'''
/********************************/
    REFACTORING DB ENDS HERE
/********************************/
'''


'''
/*********************************/
    HTTP BASIC AUTH CODE
/*********************************/
'''


class NewBasicAuth(BasicAuth):
    def __init__(self, app):
        BasicAuth(app)

    def check_credentials(self, username, password):
        """This function is called to check if a username /
        password combination is valid.
        """
        user = None
        if username != "":
            # Calling DB and fetching userdetails
            user = userdetails_API_query(username)
            print "id ", user['_id']
            if user != None:
                #u = app.config['BASIC_AUTH_USERNAME'] = user['username']
                #pwd = app.config['BASIC_AUTH_PASSWORD'] = user['pw_hash']
                # print " u & pwd",username
                if user['username'] == username and check_password_hash(user['pw_hash'], password):
                    g.user = user['_id'], username, user['email']
                    return True
                print "g.user", g.user
        return False


basic_auth = NewBasicAuth(app)

'''
/*************************************/
    HTTP BASIC AUTH ENDS HERE
/*************************************/
'''

'''
/*************************************/
            API CODE
/*************************************/
'''


@app.route('/api/statuses/home_timeline')
@basic_auth.required
def home_timeline(TTL=30):
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    if not g.user:
        return jsonify(Status_code=status.HTTP_401_UNAUTHORIZED)
    # user = userdetails_query()
    print"inside home_time", g.user[0]
    # messages=query()
    followed = mongo.db.users.find_one(
        {'_id': g.user[0]}, {'follows': 1})
    if followed is None:
        followed = {'follows': []}

    ############### Redis ###############
    # Create a hash key
    message_json = ""
    hash = hashlib.sha224(message_json).hexdigest()
    key = "home_timeline" + hash
    print "Created Key\t : %s" % key

    ############### REDIS SESSION CODE #####################
    # Check if data is in cache.
    if (R_SERVER.get(key)):
        print "** Messages returned from Redis Cache **"
        return cPickle.loads(R_SERVER.get(key))
    else:
        print "** Messages returned from MongoDB **"
        messages = mongo.db.message.find(
            {'$or': [
                {'author_id': g.user[0]},
                {'author_id': {'$in': followed['follows']}}
            ]}).sort('pub_date', -1)

        print "API MSG", messages
        get_data = []
        for row in messages:
            # print row['username']
            get_data.append({'user': row['username'], 'message': row['text'],
                             'pub_date': format_datetime(row['pub_date'])})
            # for item in row:
            # print get_data

            # get_data.append({row})
        message_json = jsonify(
            messages=get_data, Status_code=status.HTTP_200_OK)

        R_SERVER.set(key, cPickle.dumps(message_json))
        R_SERVER.expire(key, TTL)

        return message_json


@app.route('/api/statuses/public_timeline')
@basic_auth.required
def newpublic_timeline(TTL=60):
    """Displays the latest messages of all users."""

    message_json = ""
    hash = hashlib.sha224(message_json).hexdigest()
    key = "public_timeline_key:" + hash
    # print "Created Key\t : %s" % key

############### REDIS SESSION CODE #####################

    # Check if data is in cache.
    if (R_SERVER.get(key)):
        print "** Messages returned from Redis Cache **"
        return cPickle.loads(R_SERVER.get(key))
    else:
        print "** Messages returned from MongoDB **"
        messages = public_timeline_query()
        data = []
        # print messages
        for row in messages:
            data.append({'user': row['username'], 'message': row['text'],
                         'pub_date': format_datetime(row['pub_date'])})

        public_timeline_JSON = jsonify(
            messages=data, Status_code=status.HTTP_200_OK)
        R_SERVER.set(key, cPickle.dumps(public_timeline_JSON))
        R_SERVER.expire(key, TTL)
        return public_timeline_JSON


@app.route('/api/statuses/user_timeline/<username>')
@basic_auth.required
def user_tweets(username, TTL=30):
    """Display's a users tweets."""
    # profile_user = query_db('select * from user where username = ?',
    #                         [username], one=True)
    profile_user = userdetails_API_query(username)
    print "profile ", profile_user
    if profile_user is None:
        abort(404)
    followed = False

    if g.user:
        followed = mongo.db.users.find_one(
            {'_id': g.user[0]}, {'follows': profile_user['_id']}) is not None
        # followed = query_db('''select 1 from follower where
        #     follower.who_id = ? and follower.whom_id = ?''',
        #                     [g.user[0], profile_user['user_id']],
        #                     one=True) is not None
    # Create a hash key
    user_profile = ""
    hash = hashlib.sha224(user_profile).hexdigest()
    key = "user_timeline_key" + hash
    # print "Created Key\t : %s" % key

############### REDIS SESSION CODE #####################

    # Check if data is in cache.
    if (R_SERVER.get(key)):
        print "** Messages returned from Redis Cache **"
        return cPickle.loads(R_SERVER.get(key))

    else:
        print "** Messages returned from MongoDB **"
        messages = user_query(profile_user)
        data = []
        # print messages
        for row in messages:
            data.append({'user': row['username'], 'message': row['text'],
                         'pub_date': format_datetime(row['pub_date'])})
        # print data
        user_profile = jsonify(messages=data, Status_code=status.HTTP_200_OK)

        R_SERVER.set(key, cPickle.dumps(user_profile))
        R_SERVER.expire(key, TTL)
        return user_profile


@app.route('/api/friendships/create')
@basic_auth.required
def follow_friend():
    """Adds the current user as follower of the given user."""
    print "followuser"
    username = request.args.get('username')
    print "JSON Data", username
    # username= req_data[username]
    whom_id = get_user_id(username)
    print "whom_id:", whom_id
    if whom_id is None:
        abort(404)
    follow_query(whom_id)
    flash('You are now following "%s"' % username)
    name = {'name of following user': username}
    R_SERVER.delete(user_timeline_key)
    return jsonify(Username=name, Status_code=status.HTTP_200_OK)


@app.route('/api/friendships/<username>')
@basic_auth.required
def unfollow_friend(username):
    """Removes the current user as follower of the given user."""

    if not g.user:
        print "401"
        abort(401)
    whom_id = get_user_id(username)
    print whom_id
    if whom_id is None:
        abort(404)
    unfollow_query(whom_id)
    flash('You are no longer following "%s"' % username)
    name = {'name of unfollowing user': username}
    ############### REDIS cache invalidate #####################
    R_SERVER.delete(user_timeline_key)
    return jsonify(Username=name, Status_code=status.HTTP_200_OK)


@app.route('/api/statuses/update')
@basic_auth.required
def add_new_message():
    """Registers a new message for the user."""
    print "test"

    msg = request.args.get('text')
    # req_data= request.get_json()
    # text = req_data['text']
    print "msg data:", msg
    print "user id: ", g.user
    if 'user_id' == "":
        abort(status.HTTP_401_UNAUTHORIZED)

    if msg:
        print msg
        # db = get_db()
        # db.execute('''insert into message (author_id, text, pub_date)
        #           values (?, ?, ?)''', (g.user[0], msg,
        #                                 int(time.time())))
        # db.commit()
        data = mongo.db.message.insert(
            {'author_id': g.user[0], 'username': g.user[1], 'email': g.user[2], 'text': msg, 'pub_date': int(time.time())})
        print "API UPDATE DATA", data
        flash('Your message was recorded')
        # username = g.user
        # data=[]
        username = g.user[1]
        print "username", username
        # data.append({'username':row[2]})
        # print data

        Jobj = {'user_id': g.user[0], 'username': username, 'msg': msg}
        ############### REDIS cache invalidate #####################
        R_SERVER.delete(user_timeline_key)
        return jsonify(messages=Jobj, Status_code=status.HTTP_200_OK)


@app.route('/api/account/verify_credentials', methods=['GET', 'DELETE'])
@basic_auth.required
def user_login(TTL=60):
    """Logs the user in."""
    # auth = request.authorization
    # username = auth.username
    # password = auth.password
    username = request.args.get('username')
    password = request.args.get('password')
    print 'user', username
    print 'pass', password

    if g.user:
        print "g.user:", g.user
        # return jsonify(URL=url_for('home_timeline'))
    # Create a hash key
    message_json = ""
    hash = hashlib.sha224(message_json).hexdigest()
    key = "Login_API_Cache" + hash
    print "Created Key\t : %s" % key

    # Check if data is in cache.
    if (R_SERVER.get(key)):
        print "** Messages returned from Redis Cache **"
        return cPickle.loads(R_SERVER.get(key))

    if username != None:
        print "session"
        error = None
        if request.method == 'GET':
            print g.user
            print username
            user = userdetails_API_query(username)
            print "query", user
            if user is None:
                error = 'Invalid username'
                return jsonify(Status_code=status.HTTP_401_UNAUTHORIZED, username=username, error=error)
            elif not check_password_hash(user['pw_hash'],
                                         password):
                error = 'Invalid password'
                return jsonify(Status_code=status.HTTP_401_UNAUTHORIZED, username=username, error=error)
            else:
                print "** Messages returned from MongoDB **"
                flash('You were logged in')
                session['user_id'] = user['_id']
                username = {'Username_logged_in': username}

                ############### REDIS SESSION CODE #####################

                message_json = jsonify(
                    Status_code=status.HTTP_200_OK, username=username)
                R_SERVER.set(key, cPickle.dumps(message_json))
                R_SERVER.expire(key, TTL)

                return message_json
    else:
        print"logout", g.user[1]
        flash('You were logged out')
        session.pop('user_id', None)
        username = {'Username_logged_out': g.user[1]}
        return jsonify(URL=url_for('newpublic_timeline'), Username=username, Status_code=status.HTTP_200_OK)


'''
/******************************/
    API CODE ENDS HERE
/******************************/
'''

'''
/******************************/
    OLD ROUTE OF MINITWIT APP
/******************************/
'''


@app.route('/')
def timeline():
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    # if not g.user:
    #    print "IT IS NOT USER"
    #    return redirect(url_for('public_timeline'))
    #messages = query()
    # followed = mongo.db.users.find_one(
    #     {'_id': session['user_id']}, {'follows': 1})
    # if followed is None:
    #     followed = {'follows': []}
    # messages = mongo.db.message.find(
    #     {'$or': [
    #         {'author_id': session['user_id']},
    #         {'author_id': {'$in': followed['follows']}}
    #     ]}).sort('pub_date', -1)
    # print "inside time msg", messages
    # print "inside timeline", g.user['email']
    # print "IT IS USER"

    user_ID = before_request()
    if user_ID != None:
        user_ID = str(g.user['_id'])
    if not g.user:
        return redirect(url_for('public_timeline'))

    ############### REDIS SESSION CODE #####################

    if redis_obj.get(user_ID):
        print "Data from REdis cache"
        return render_template('timeline.html', messages=pickle.loads(redis_obj.get(user_ID)))
    else:
        messages = query()
        redis_obj.setex(session['user_id'], pickle.dumps(messages), 30)
        print "Data from REdis cache"
        return render_template('timeline.html', messages=messages)

    # return render_template('timeline.html', messages=messages)


@app.route('/public')
def public_timeline(TTL=10):
    """Displays the latest messages of all users."""
    keyName = "public_timeline"
    ############### REDIS SESSION CODE #####################

    if redis_obj.get(keyName):
        print("** Messages from Redis Cache **")
        key = pickle.loads(redis_obj.get(keyName))
        return render_template('timeline.html', messages=key)
    else:
        messages = public_timeline_query()
        print("** Messages from mongoDB **")
        redis_obj.setex(keyName, pickle.dumps(messages), 60)
        return render_template('timeline.html', messages=messages)


@app.route('/<username>')
def user_timeline(username):
    """Display's a users tweets."""
    # profile_user = query_db('select * from user where username = ?',
    # [username], one=True)
    user_ID = before_request()
    user_ID = None
    if user_ID != None:
        user_ID = str(g.user['_id'])
    profile_user = mongo.db.users.find_one({'username': username})
    # print "inside username", profile_user
    if profile_user is None:
        abort(404)
    followed = False
    if g.user:
        # followed = query_db('''select 1 from follower where
        #     follower.who_id = ? and follower.whom_id = ?''',
        #     [session['user_id'], profile_user['user_id']],
        #     one=True) is not None
        followed = mongo.db.users.find_one(
            {'_id': session['user_id'],
             'follows': {'$in': [profile_user['_id']]}}) is not None
    if redis_obj.get(profile_user):
        pKey = pickle.loads(redis_obj.get(profile_user))
        return render_template('timeline.html', messages=pKey, followed=followed,
                               profile_user=profile_user)
    else:
        if g.user:
            redis_obj.setex(session['user_id'], pickle.dumps(
                user_query(profile_user)), 60)
    return render_template('timeline.html', messages=user_query(profile_user), followed=followed,
                           profile_user=profile_user)


@app.route('/<username>/follow')
def follow_user(username):
    """Adds the current user as follower of the given user."""
    user_ID = before_request()
    user_ID = None
    if user_ID != None:
        user_ID = str(g.user['_id'])
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    mongo.db.users.update({'_id': g.user['_id']}, {
                          '$push': {'follows': whom_id}})
    flash('You are now following "%s"' % username)
    if redis_obj.get(user_ID):
        return redirect(url_for('user_timeline', username=username, userId=pickle.loads(r.get(user_ID))))
    else:
        redis_obj.delete(str(g.user['_id']))
        print "Invalidating cache after Follow"
        return redirect(url_for('user_timeline', username=username))


@app.route('/<username>/unfollow')
def unfollow_user(username):
    """Removes the current user as follower of the given user."""
    user_ID = before_request()
    user_ID = None
    if user_ID != None:
        user_ID = str(g.user['_id'])
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    mongo.db.users.update({'_id': g.user['_id']}, {
                          '$pull': {'follows': whom_id}})
    flash('You are no longer following "%s"' % username)
    if redis_obj.get(user_ID):
        return redirect(url_for('user_timeline', username=username, userId=pickle.loads(redis_obj.get(user_ID))))
    else:
        redis_obj.delete(session['user_id'])
        print "Invalidating cache after Unfollow"
        return redirect(url_for('user_timeline', username=username))


"""
##################################################

 Like unlike logic Start

##################################################
"""

############################## LIke Unlike Logic start ##################################


@app.route('/<username>/like')
def like_comment(username):
    """Adds Likes to messages."""

    user_ID = before_request()
    user_ID = None
    if user_ID != None:
        user_ID = str(g.user['_id'])

    message_id = request.args.get('message_id')
    profile_usr = request.args.get('profile_usr')
    count = float(1)

    redis_obj.zincrby('add_like', message_id, count)

    print "message ID", message_id

    if redis_obj.get(user_ID):
        return redirect(url_for('timeline', username=profile_usr, userId=pickle.loads(redis_obj.get(user_ID))))
    else:
        """ Invalidating cache """
        redis_obj.delete('leaderboard-key')
        redis_obj.delete(session['user_id'])
        print "Invalidating cache after Like"
        return redirect(url_for('timeline', username=profile_usr))


@app.route('/<username>/unlike')
def unlike_comment(username):
    """Removes likes from messages."""
    user_ID = before_request()
    user_ID = None
    if user_ID != None:
        user_ID = str(g.user['_id'])

    message_id = request.args.get('message_id')
    profile_usr = request.args.get('profile_usr')
    count=float(-1)

    print "username who liked message", username
    print "Id of the message", message_id

    redis_obj.zincrby('add_like', message_id, count)

    print redis_obj.scard(message_id)

    if redis_obj.get(user_ID):
        return redirect(url_for('timeline', username=profile_usr, userId=pickle.loads(redis_obj.get(user_ID))))
    else:
        """ Invalidating cache """
        redis_obj.delete('leaderboard-key')
        redis_obj.delete(session['user_id'])
        print "Invalidating cache after unlike"
        return redirect(url_for('timeline', username=profile_usr))


############################## Like unlike logic end ####################################


@app.route('/api/favorites/create/<id>')
@basic_auth.required
def like_comment_API(id):
    """Adds like to given message_id."""

    count = float(1)
    redis_obj.zincrby('add_like', id, count)

    """ Invalidating cache """
    redis_obj.delete('leaderboard-key')

    return jsonify(username=g.user[1], Message="Success! Message liked successfully. ", Status_code=status.HTTP_200_OK)


### Unlike message ###


@app.route('/api/favorites/destroy/<id>')
@basic_auth.required
def unlike_comment_API(id):
    """Adds like to given message_id."""

    count = float(-1)
    redis_obj.zincrby('add_like', id, count)

    """ Invalidating cache """
    redis_obj.delete('leaderboard-key')
    return jsonify(username=g.user[1], Message="Success! Message unliked successfully. ", Status_code=status.HTTP_200_OK)


"""
##################################################

 Like unlike logic End

##################################################
"""


"""
##################################################

leaderboard logic start

##################################################
"""

# routes


@app.route('/leaderboard')
def leaderboard_timeline(TTL=60):

    keyName = "leaderboard-key"

    leadership_data= redis_obj.zrevrange('add_like',0,-1,withscores=True)

    list_of_users=[]


    if redis_obj.get(keyName):
        print("** Messages from leaderboard Redis Cache **")
        key = pickle.loads(redis_obj.get(keyName))
        return render_template('timeline.html', messages=key)
    else:
        for like in leadership_data:
            message_id=like[0]
            user_record=mongo.db.message.find_one({"_id":ObjectId(message_id)})

            print "line 906 ", user_record

            list_of_users.append({'username':user_record['username'],'email':user_record['email'],'pub_date':user_record['pub_date'],'text':user_record['text'],'score':int(like[1])})


        print("** Messages from  leaderboard DB hit **")
        redis_obj.set(keyName, cPickle.dumps(list_of_users))
        redis_obj.expire(keyName, TTL)
        return render_template('timeline.html', messages=list_of_users)


##API changes

### Unlike message ###
@app.route('/api/favorites/list')
@basic_auth.required
def leaderboard_timeline_API():
    """Adds like to given message_id."""
    keyName = "leaderboard-key"

    leadership_data= redis_obj.zrevrange('add_like',0,-1,withscores=True)
    list_of_users=[]
    if redis_obj.get(keyName):
        print("** Messages from leaderboard Redis Cache **")
        key = pickle.loads(redis_obj.get(keyName))
        user_profile = jsonify(Message="Success! leaderboard details.",
                               leaderboard=key, Status_code=status.HTTP_200_OK)
        return user_profile
    else:
        for like in leadership_data:
            message_id=like[0]
            user_record=mongo.db.message.find_one({"_id":ObjectId(message_id)})
            tmp =user_record['email']
            list_of_users.append({'username':user_record['username'],'email':user_record['email'],'pub_date':user_record['pub_date'],'text':user_record['text'],'score':int(like[1])})


        print("** Messages from  leaderboard DB hit **")
        redis_obj.set(keyName, cPickle.dumps(list_of_users))
        redis_obj.expire(keyName, 60)


    user_profile = jsonify(Message="Success! leaderboard details.",
                           leaderboard=list_of_users, Status_code=status.HTTP_200_OK)

    return user_profile


"""
##################################################

leaderboard logic end

##################################################
"""


@app.route('/add_message', methods=['POST'])
def add_message():
    """Registers a new message for the user."""
    user_ID = str(session['user_id'])
    if 'user_id' not in session:
        abort(401)
    if request.form['text']:
        add_message_query()
        flash('Your message was recorded')
        if redis_obj.get(user_ID):
            redis_obj.delete(user_ID)
            print "Invalidating cache after adding new message"
    return redirect(url_for('timeline'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    # try:
    #     if g.user != None:
    #         user_ID = "Logged " + str(g.user['_id'])
    #         print "insideNone",user_ID
    # except ValueError:
    #         print "try again"
    # if g.user:
    #     print "insideLog"
    #     return redirect(url_for('timeline'))
    user_ID = ""
    if g.user != None:
        user_ID = "Logged " + str(g.user['_id'])
        print "insideNone", user_ID

        ############### REDIS SESSION CODE #####################
        if redis_obj.get(user_ID):
            pKey = pickle.loads(redis_obj.get(user_ID))
            print "insideLog", user_ID
            return redirect(url_for('timeline'), pKey)
    error = None
    if request.method == 'POST':
        user = userdetails_query()
        if user is None:
            error = 'Invalid username'
            # abort(status.HTTP_401_UNAUTHORIZED)
        elif not check_password_hash(user['pw_hash'],
                                     request.form['password']):
            error = 'Invalid password'
            # abort(status.HTTP_401_UNAUTHORIZED)
        else:
            flash('You were logged in')
            session['user_id'] = user['_id']
            logUser = pickle.dumps(list(user))
            # print "logUser", logUser
            redis_obj.setex("Logged " + str(session['user_id']), logUser, 60)
            return redirect(url_for('timeline'))
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif get_user_id(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            # db = get_db()
            # db.execute('''insert into user (
            #   username, email, pw_hash) values (?, ?, ?)''',
            #   [request.form['username'], request.form['email'],
            #   generate_password_hash(request.form['password'])])
            # db.commit()
            mongo.db.users.insert({'username': request.form['username'], 'email': request.form['email'], 'pw_hash': generate_password_hash(
                request.form['password']), 'follows': []})
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('public_timeline'))


'''
/**********************************/
    OLD ROUTE CODE ENDS HERE
/**********************************/
'''
# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url
