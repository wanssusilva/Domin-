import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'eyda_dominovip_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dominogame.db'
db = SQLAlchemy(app)
socketio = SocketIO(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('index.html', user=session['user'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['user']).first()
        if user and check_password_hash(user.password, request.form['pass']):
            session['user'] = user.username
            return redirect(url_for('home'))
        return "Erro! Verifique os dados."
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        pw = generate_password_hash(request.form['pass'])
        new = User(username=request.form['user'], password=pw)
        db.session.add(new); db.session.commit()
        return redirect(url_for('login'))
    return render_template('cadastro.html')

@socketio.on('join')
def on_join(data):
    join_room('sala_global')
    emit('status', {'msg': f"{data['user']} entrou na mesa!"}, room='sala_global')

@socketio.on('jogada')
def handle_move(data):
    emit('update_board', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)
