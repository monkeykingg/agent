from flask import Flask
from flask import escape
from flask import url_for, escape

app = Flask(__name__)

@app.route('/')
@app.route('/index')
@app.route('/home')
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
