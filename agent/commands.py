import click
from datetime import datetime, timedelta

from agent import app, db
from agent.models import User, Agent

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

        {'name': 'agent 1', 
         'time': str(datetime.now() - timedelta(1)), 
         'info': '{"Access":"0", "URI":"shelter", "Port":"default", "Address":"localhost", "Status":"inactive", "Capacity":"100"}', 
         'onto': 'http://ontology.eil.utoronto.ca/tove/shelter.owl'},

        {'name': 'agent 2', 
         'time': str(datetime.now()), 
         'info': '{"Access":"1", "URI":"shelter", "Port":"default", "Address":"localhost", "Status":"active", "Capacity":"200"}', 
         'onto': 'http://www.lesfleursdunormal.fr/static/_downloads/pizza_onto.owl'}

    ]

    user = User(username=username, password_hash=pw)
    db.session.add(user)
    for a in agents:
        agent = Agent(name=a['name'], time=a['time'], info=a['info'], onto=a['onto'])
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