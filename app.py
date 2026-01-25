import os
import smtplib # Extra safety mate
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = "nexgen_ultra_pro_max_2026"

# --- Database Configuration ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'nexgen_v4.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Email Configuration (Render Fix) ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465 # Port 587 badle 465 vadhu stable che Render par
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'virenkanzariya02@gmail.com'
app.config['MAIL_PASSWORD'] = 'msxwuaazwqtsrtgr' 
app.config['MAIL_DEFAULT_SENDER'] = 'virenkanzariya02@gmail.com'

mail = Mail(app)

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

# Render mate automatic table creation
with app.app_context():
    db.create_all()

# --- Routes ---
@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/innovation-suite')
def solutions(): 
    try:
        projects = Project.query.all()
    except:
        projects = []
    return render_template('solutions.html', projects=projects)

@app.route('/collaborate')
def collaborate(): 
    return render_template('collaborate.html')

@app.route('/philosophy')
def philosophy(): 
    return render_template('philosophy.html')

# --- FORM SUBMISSION (ERROR PROOF) ---
@app.route('/submit-inquiry', methods=['POST'])
def submit_inquiry():
    u_name = request.form.get('name')
    u_email = request.form.get('email')
    u_domain = request.form.get('domain')
    u_msg = request.form.get('message')

    # Step 1: Pehla Database ma save karo (Aa fail nahi thay)
    try:
        new_inquiry = Inquiry(name=u_name, email=u_email, domain=u_domain, message=u_msg)
        db.session.add(new_inquiry)
        db.session.commit()
        
        # Step 2: Email mokalva try karo (Jo fail thay to site crash nahi thay)
        try:
            msg = Message(
                subject=f"New Mission Request: {u_name}",
                recipients=['virenkanzariya02@gmail.com'],
                body=f"Name: {u_name}\nEmail: {u_email}\nMessage: {u_msg}"
            )
            mail.send(msg)
            flash("Mission Intelligence Received! Email Sent.", "success")
        except Exception as mail_err:
            print(f"Email Error: {mail_err}")
            flash("Message saved, but email notification failed. We will check it manually.", "warning")

    except Exception as db_err:
        print(f"Database Error: {db_err}")
        flash("System failure. Please try again later.", "danger")
    
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
    if not session.get('logged_in'): 
        return redirect(url_for('login'))
    return render_template('admin.html', projects=Project.query.all(), inquiries=Inquiry.query.all())

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
