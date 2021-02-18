from flask import Flask, render_template
from flask import url_for, escape
from flask_sqlalchemy import SQLAlchemy

import os
import sys
import click

# check system
WINDOWS = sys.platform.startswith('win')
if WINDOWS:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

# app & db
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)

# new command: initdb
@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.') 

# new command: forge
@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()

    username = 'Bill Wang'
    agents = [
        {'name': 'agent 1', 'time': '2021-01-01'},
        {'name': 'agent 2', 'time': '2021-01-02'},
        {'name': 'agent 3', 'time': '2021-02-01'},
    ]

    user = User(username=username)
    db.session.add(user)
    for a in agents:
        agent = Agent(name=a['name'], time=a['time'])
        db.session.add(agent)

    db.session.commit()
    click.echo('Done.')

class User(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    time = db.Column(db.String(60))

@app.route('/hello')
def hello():
    return '<h1>Hello!</h1><img src="http://helloflask.com/totoro.gif">'

@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % escape(name)

@app.route('/test')
def test_url_for():
    print(url_for('hello'))
    print(url_for('user_page', name='bill'))  # /user/bill
    print(url_for('user_page', name='mark'))  # /user/mark
    print(url_for('test_url_for'))  # /test
    print(url_for('test_url_for', num=2)) # /test?num=2
    return 'Test page'

@app.route('/')
def index():
    user = User.query.first()
    agents = Agent.query.all()
    return render_template('index.html', user=user, agents=agents)