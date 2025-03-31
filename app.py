from flask import Flask, request, send_from_directory, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
from models import ActivityLog, User, db
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__, template_folder='templates') # Initializes the Flask application
app.secret_key = os.environ.get('SECRET_KEY') or 'your-secret-key-here' # Important for session security

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///file_sharing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask-login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'Login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Directory where files will be stored
UPLOAD_FOLDER = 'shared files' # File path
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Create a directory if it doesn't exist
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper function for logging activities
def log_activity(action):
    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        user_id = None

    activity = ActivityLog(
        user_id=user_id,
        action=action,
        ip_address=request.remote_addr
    )
    db.session.add(activity)
    db.session.commit()
# Home route: Lists all files
@app.route('/') # Define the root URL ('/') route
def home():
    files = os.listdir(app.config['UPLOAD_FOLDER']) # Lists all files in the shared files directory.
    log_activity("Viewed home page")
    return render_template('index.html', files=files) # Passes the list of files to the index.html template for display

# File upload route
@app.route('/upload', methods=['POST']) # Handles file uploads
@login_required
def upload_file():
    if 'file' not in request.files:  # Checks if file is part of the request
        flash('no file part', 'error')
        return redirect(url_for('home'))
    
    file = request.files['file']
    if file.filename == '':  # Checks if a filename is provided
        flash('No selected file', 'error')
        return redirect(url_for('home'))
    
    if not allowed_file(file.filename):
        flash('File type not allowed', 'error')
        return redirect(url_for('home'))

    # Save the uploaded file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Log activity
    log_activity(f"Uploaded file: {file.filename}")
    flash('File uploaded successfully', 'success')
    return redirect(url_for('home'))
# File download route
@app.route('/download/<filename>') # Defines a dynamic route for downloading files
def download_file(filename):
    if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        flash('File not found', 'error')
        return redirect(url_for('home'))
    
    log_activity(f"Downloaded file: {filename}")
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["Username"]
        password = request.form["Password"]

        # Find user in the database
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id # Store user in session
            return redirect(url_for('home'))
        else:
            return "Invalid credentials", 401
    return render_template("login.html")
@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))
@app.route("/reigster", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form.get("email", "")

        # Check if username exists
        if User.query.filter_by(username=username).first():
            return  "Username already exists", 400
        
        # Create new user
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template("register.html")
if __name__ == "__main__":
    app.run(debug=True) # Starts the Flask development server with debugging enabled