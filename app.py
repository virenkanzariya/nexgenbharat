import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "nexgen_ultra_pro_max_2026"

# --- Database Configuration ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'nexgen_v4.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Telegram Configuration ---
TELEGRAM_TOKEN = '8248572404:AAE5_ZxX40rPj_Dnep9rp0fpFGpOrvgbKfs'
TELEGRAM_CHAT_ID = '6705656451'

def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram Error: {e}")

# --- Database Models ---
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(10))
    category = db.Column(db.String(50))
    status = db.Column(db.String(20), default="Live")
    version = db.Column(db.String(10))
    tag = db.Column(db.String(50))
    stack = db.Column(db.String(200))
    language = db.Column(db.String(100))
    algorithm = db.Column(db.String(200))
    logic = db.Column(db.String(500))
    desc = db.Column(db.String(500))

class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    domain = db.Column(db.String(100))
    message = db.Column(db.Text, nullable=False)

# --- Routes ---
@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/innovation-suite')
def solutions(): 
    return render_template('solutions.html', projects=Project.query.all())

@app.route('/collaborate')
def collaborate(): 
    return render_template('collaborate.html')

@app.route('/philosophy')
def philosophy(): 
    return render_template('philosophy.html')

@app.route('/submit-inquiry', methods=['POST'])
def submit_inquiry():
    u_name = request.form.get('name')
    u_email = request.form.get('email')
    u_domain = request.form.get('domain')
    u_msg = request.form.get('message')

    try:
        new_inquiry = Inquiry(name=u_name, email=u_email, domain=u_domain, message=u_msg)
        db.session.add(new_inquiry)
        db.session.commit()

        # Telegram Alert
        alert_text = (
            f"🚀 <b>New Mission Request!</b>\n\n"
            f"👤 <b>Name:</b> {u_name}\n"
            f"📧 <b>Email:</b> {u_email}\n"
            f"🎯 <b>Project:</b> {u_domain}\n"
            f"💬 <b>Message:</b> {u_msg}"
        )
        send_telegram_alert(alert_text)
        
        flash("Mission Intelligence Received! Telegram Alert Sent.", "success")
    except Exception as e:
        flash("Data saved locally, but notification failed.", "warning")
    
    return redirect(url_for('collaborate'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'nexgen2026':
            session['logged_in'] = True
            return redirect(url_for('mission_control'))
        flash("Invalid Credentials.", "danger")
    return render_template('login.html')

@app.route('/mission-control')
def mission_control():
    if not session.get('logged_in'): return redirect(url_for('login'))
    return render_template('admin.html', projects=Project.query.all(), inquiries=Inquiry.query.all())

@app.route('/admin/delete-project/<int:id>')
def delete_project(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    p = Project.query.get(id)
    if p:
        db.session.delete(p)
        db.session.commit()
    return redirect(url_for('mission_control'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# --- SERVER STARTUP (Ahi badlav karyo che) ---
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
