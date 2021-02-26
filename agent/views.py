from flask import render_template, request, url_for, redirect, flash, escape
from flask_login import login_user, login_required, logout_user, current_user

from agent import app, db
from agent.models import User, Agent

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
        info = request.form.get('info')
        onto = request.form.get('onto')

        if not name or not time or len(time) > 60 or len(name) > 60:
            flash('Invalid input.') 
            return redirect(url_for('index'))

        agent = Agent(name=name, time=time, info=info, onto=onto)
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
        info = request.form['info']
        onto = request.form['onto']

        if not name or not time or len(time) > 60 or len(name) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', agent_id=agent_id))

        agent.name = name
        agent.time = time
        agent.info = info
        agent.onto = onto
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