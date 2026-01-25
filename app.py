import os
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

# --- Email Configuration ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'virenkanzariya02@gmail.com'
app.config['MAIL_PASSWORD'] = 'msxwuaazwqtsrtgr' # Your 16-digit App Password
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

# --- Frontend Routes ---
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

# --- Form Submission & Email Logic ---
@app.route('/submit-inquiry', methods=['POST'])
def submit_inquiry():
    u_name = request.form.get('name')
    u_email = request.form.get('email')
    u_domain = request.form.get('domain')
    u_msg = request.form.get('message')

    try:
        # Save to Database
        new_inquiry = Inquiry(name=u_name, email=u_email, domain=u_domain, message=u_msg)
        db.session.add(new_inquiry)
        db.session.commit()

        # Send Email Notification to Admin
        msg = Message(
            subject=f"New Mission Request from: {u_name}",
            recipients=['virenkanzariya02@gmail.com'],
            body=f"Admin Alert!\n\nA new collaboration request has been received.\n\n"
                 f"Name: {u_name}\n"
                 f"Email: {u_email}\n"
                 f"Domain: {u_domain}\n"
                 f"Message: {u_msg}\n\n"
                 f"Please log in to Mission Control to manage this inquiry."
        )
        mail.send(msg)
        flash("Mission Intelligence Received. Our team will contact you soon.", "success")
    except Exception as e:
        print(f"Error: {e}")
        flash("Data saved locally, but email transmission failed.", "warning")
    
    return redirect(url_for('collaborate'))

# --- Admin Authentication ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'nexgen2026':
            session['logged_in'] = True
            return redirect(url_for('mission_control'))
        flash("Invalid Credentials. Access Denied.", "danger")
    return render_template('login.html')

@app.route('/mission-control')
def mission_control():
    if not session.get('logged_in'): 
        return redirect(url_for('login'))
    return render_template('admin.html', projects=Project.query.all(), inquiries=Inquiry.query.all())

# --- CRUD Operations (Add & Delete) ---
@app.route('/admin/add-project', methods=['POST'])
def add_project():
    if not session.get('logged_in'): return redirect(url_for('login'))
    new_p = Project(
        name=request.form.get('name'),
        icon=request.form.get('icon'),
        category=request.form.get('category'),
        version=request.form.get('version'),
        stack=request.form.get('stack'),
        desc=request.form.get('desc'),
        logic=request.form.get('logic')
    )
    db.session.add(new_p)
    db.session.commit()
    flash("New system architecture deployed successfully!", "success")
    return redirect(url_for('mission_control'))

@app.route('/admin/delete-project/<int:id>')
def delete_project(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    p = Project.query.get(id)
    if p:
        db.session.delete(p)
        db.session.commit()
        flash("System de-initialized and removed.", "danger")
    return redirect(url_for('mission_control'))

@app.route('/admin/delete-inquiry/<int:id>')
def delete_inquiry(id):
    if not session.get('logged_in'): return redirect(url_for('login'))
    inq = Inquiry.query.get(id)
    if inq:
        db.session.delete(inq)
        db.session.commit()
        flash("Transmission log cleared.", "info")
    return redirect(url_for('mission_control'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)