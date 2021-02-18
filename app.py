from flask import Flask, render_template
from flask import escape
from flask import url_for, escape

app = Flask(__name__)

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

username = 'Bill Wang'
agents = [
    {'name': 'agent 1', 'time': '2021-01-01'},
    {'name': 'agent 2', 'time': '2021-01-02'},
    {'name': 'agent 3', 'time': '2021-02-01'},
]

@app.route('/')
def index():
    return render_template('index.html', username=username, agents=agents)