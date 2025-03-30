from flask import Flask, request, send_from_directory, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import os

from models import ActivityLog, User

app = Flask(__name__, template_folder='templates') # Initializes the Flask application

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///file_sharing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Directory where files will be stored
UPLOAD_FOLDER = 'shared files' # File path
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Create a directory if it doesn't exist
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Home route: Lists all files
@app.route('/') # Define the root URL ('/') route
def home():
    files = os.listdir(app.config['UPLOAD_FOLDER']) # Lists all files in the shared files directory.
    return render_template('index.html', files=files) # Passes the list of files to the index.html template for display

# File upload route
@app.route('/upload', methods=['POST']) # Handles file uploads
def upload_file():
    if 'file' not in request.files:  # Checks if file is part of the request
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':  # Checks if a filename is provided
        return "No selected file", 400

    # Save the uploaded file
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))

    # Log activity
    activity = ActivityLog(user_id=1, action=f"Uploaded file: {file.filename}")
    db.session.add(activity)  # Add activity log to the session
    db.session.commit()  # Commit the transaction to the database

    return "File uploaded successfully", 200
# File download route
@app.route('/download/<filename>') # Defines a dynamic route for downloading files
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename) # Sends the requested file from the "UPLOAD_FOLDER" to the user.


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