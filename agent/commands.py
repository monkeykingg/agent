import click

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