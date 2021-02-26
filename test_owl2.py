import os
import sys
import click

from flask import Flask, render_template
from flask import url_for, escape, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy

import random
import simpy
from owlready2 import *
import datetime

import unittest

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

# ctime = get_ontology("ctime.owl").load()

# shelter = get_ontology("shelter.owl").load()

onto = get_ontology("http://www.lesfleursdunormal.fr/static/_downloads/pizza_onto.owl")
onto.load()

with onto:
    class NonVegetarianPizza(onto.Pizza):
        equivalent_to = [onto.Pizza
                         & ( onto.has_topping.some(onto.MeatTopping)
                            | onto.has_topping.some(onto.FishTopping))]
        def eat(self): print("Beurk! I'm vegetarian!")

print(list(onto.classes()))


test_app = Flask(__name__)
test_app.config['SECRET_KEY'] = 'dev'
test_app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(test_app.root_path), 'test_data.db')
test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

test_db = SQLAlchemy(test_app)



# new command: initdb
@test_app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        test_db.drop_all()
    test_db.create_all()
    click.echo('Initialized database.') 

# new command: forge
@test_app.cli.command()
def forge():
    """Generate fake data."""
    test_db.create_all()

    username = 'Bill Wang'

    agents = [
        {'name': 'agent 1', 'time': '2021-01-01', 'onto': 'http://www.lesfleursdunormal.fr/static/_downloads/pizza_onto.owl'},
        {'name': 'agent 2', 'time': '2021-01-02', 'onto': 'http://www.lesfleursdunormal.fr/static/_downloads/pizza_onto.owl'},
        {'name': 'agent 3', 'time': '2021-02-01', 'onto': 'http://www.lesfleursdunormal.fr/static/_downloads/pizza_onto.owl'},
    ]

    user = User(username=username)
    test_db.session.add(user)
    for a in agents:
        agent = Agent(name=a['name'], time=a['time'], onto=a['onto'])
        test_db.session.add(agent)

    test_db.session.commit()
    click.echo('Done.')


class User(test_db.Model): 
    id = test_db.Column(test_db.Integer, primary_key=True)
    username = test_db.Column(test_db.String(30))
class Agent(test_db.Model):
    id = test_db.Column(test_db.Integer, primary_key=True)
    name = test_db.Column(test_db.String(60))
    time = test_db.Column(test_db.String(60))
    onto = test_db.Column(test_db.String(100))