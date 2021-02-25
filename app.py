from flask import Flask, render_template
from flask import url_for, escape, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_user
from flask_login import login_required, logout_user, current_user

from werkzeug.security import generate_password_hash, check_password_hash

import os
import sys
import click

import random
import simpy
from owlready2 import *




# check system
WINDOWS = sys.platform.startswith('win')
if WINDOWS:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

# app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)
login_manager = LoginManager(app) 
login_manager.login_view = 'login'








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
    pw = 'password'
    agents = [
        {'name': 'agent 1', 'time': '2021-01-01'},
        {'name': 'agent 2', 'time': '2021-01-02'},
        {'name': 'agent 3', 'time': '2021-02-01'},
    ]

    user = User(username=username, password_hash=pw)
    db.session.add(user)
    for a in agents:
        agent = Agent(name=a['name'], time=a['time'])
        db.session.add(agent)

    db.session.commit()
    click.echo('Done.')

@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('Done.')







@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user

# skip user when render_template
@app.context_processor
def inject_user(): 
    user = User.query.first()
    return dict(user=user)








class User(db.Model, UserMixin): 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    time = db.Column(db.String(60))








@app.route('/hello')
def hello():
    return '<h1>Hello!</h1><img src="http://helloflask.com/totoro.gif">'

@app.route('/user/<username>')
def user_page(username):
    return 'User: %s' % escape(username)

@app.route('/test')
def test_url_for():
    print(url_for('hello'))
    print(url_for('user_page', username='bill'))  # /user/bill
    print(url_for('user_page', username='mark'))  # /user/mark
    print(url_for('test_url_for'))  # /test
    print(url_for('test_url_for', num=2)) # /test?num=2
    return 'Test page'

# main index
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        name = request.form.get('name')
        time = request.form.get('time')
        if not name or not time or len(time) > 60 or len(name) > 60:
            flash('Invalid input.') 
            return redirect(url_for('index'))
        agent = Agent(name=name, time=time)
        db.session.add(agent) 
        db.session.commit()
        flash('Agent added.')
        return redirect(url_for('index'))
    #user = User.query.first()
    agents = Agent.query.all()
    return render_template('index.html', agents=agents)

@app.route('/agent/edit/<int:agent_id>', methods=['GET', 'POST'])
@login_required
def edit(agent_id):
    agent = Agent.query.get_or_404(agent_id)

    if request.method == 'POST': 
        name = request.form['name']
        time = request.form['time']

        if not name or not time or len(time) > 60 or len(name) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', agent_id=agent_id))

        agent.name = name
        agent.time = time
        db.session.commit()
        flash('Agent updated.')
        return redirect(url_for('index'))

    return render_template('edit.html', agent=agent)

@app.route('/agent/delete/<int:agent_id>', methods=['POST'])
@login_required
def delete(agent_id):
    agent = Agent.query.get_or_404(agent_id)
    db.session.delete(agent)
    db.session.commit()
    flash('Agent deleted.')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()
        # check the consistency of username and password
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))

        flash('Invalid username or password.')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))

# @app.route('/settings', methods=['GET', 'POST'])
# @login_required
# def settings():
#     if request.method == 'POST':
#         username = request.form['username']

#         if not username or len(username) > 30:
#             flash('Invalid input.')
#             return redirect(url_for('settings'))

#         # current_user returns the db log of current login user
#         current_user.username = username
#         # equal to below:
#         # user = User.query.first()
#         # user.username = username

#         db.session.commit()
#         flash('Settings updated.')
#         return redirect(url_for('index'))

#     return render_template('settings.html')


@app.errorhandler(404) 
def page_not_found(e):
    #user = User.query.first()
    return render_template('404.html'), 404