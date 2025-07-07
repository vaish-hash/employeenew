import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<Employee {self.name}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    duration_months = db.Column(db.Integer, nullable=False)
    start_month = db.Column(db.String(20), nullable=False)
    start_year = db.Column(db.Integer, nullable=False)
    end_month = db.Column(db.String(20), nullable=False)
    end_year = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Project {self.name}>'

# Routes
@app.route('/')
def home():
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')

        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            session['username'] = username
            flash('Logged in successfully!', 'success')
            return jsonify({'success': True, 'redirect_url': url_for('index')})
        else:
            flash('Invalid Credentials. Please try again.', 'error')
            return jsonify({'success': False, 'message': 'Invalid Credentials.'}), 401
    return render_template('login.html')

@app.route('/index')
def index():
    if 'logged_in' in session and session['logged_in']:
        return render_template('index.html', username=session.get('username', 'Guest'))
    else:
        flash('Please log in to access this page.', 'warning')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/members')
def get_employees_page():
    if 'logged_in' in session and session['logged_in']:
        return render_template('members.html')
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('login'))

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)