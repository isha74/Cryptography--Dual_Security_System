from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import json
from datetime import datetime
import sys

# Add the src directory to the path to import our crypto modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from encryption import encrypt_file
from decryption import decrypt_file
from key_manager import generate_rsa_keys
from database import add_user, get_user_by_username, get_user_by_email, get_user_by_id

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
"""
Remove SQLAlchemy usage; persist users in Excel via helpers from database.py
"""

# Resolve important directories
SRC_DIR = Path(__file__).resolve().parent
BASE_DIR = SRC_DIR.parent

# Always use a single, absolute uploads directory at the project root
app.config['UPLOAD_FOLDER'] = str(BASE_DIR / 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Create upload directory (root-level uploads)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class User(UserMixin):
    def __init__(self, id, username, email, password_hash, is_active=True):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.is_active = is_active

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

"""
Remove FileOperation model; you can reintroduce Excel-backed logging later if needed.
"""

@login_manager.user_loader
def load_user(user_id):
    data = get_user_by_id(int(user_id))
    if not data:
        return None
    return User(
        id=data.get('id'),
        username=data.get('username'),
        email=data.get('email'),
        password_hash=data.get('password_hash'),
        is_active=bool(data.get('is_active', True))
    )

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        data = get_user_by_username(username)
        
        if data and check_password_hash(data.get('password_hash', ''), password):
            user = User(
                id=data.get('id'),
                username=data.get('username'),
                email=data.get('email'),
                password_hash=data.get('password_hash'),
                is_active=bool(data.get('is_active', True))
            )
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('signup.html')
        
        if get_user_by_username(username):
            flash('Username already exists', 'error')
            return render_template('signup.html')

        if get_user_by_email(email):
            flash('Email already registered', 'error')
            return render_template('signup.html')
        
        # Create new user in Excel
        password_hash = generate_password_hash(password)
        created = add_user(username=username, email=email, password_hash=password_hash)
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', operations=[])

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

@app.route('/encrypt', methods=['POST'])
@login_required
def encrypt_file_web():
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Perform encryption and get path to output file
            encrypted_path = encrypt_file(file_path)
            encrypted_filename = os.path.basename(encrypted_path)
            
            # Clean up uploaded file
            os.remove(file_path)
            
            return jsonify({'message': 'File encrypted successfully!', 'download_url': url_for('download_file', filename=encrypted_filename)})
        except Exception as e:
            os.remove(file_path)
            return jsonify({'error': str(e)}), 500

@app.route('/decrypt', methods=['POST'])
@login_required
def decrypt_file_web():
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            
            # Determine output filename
            if filename.endswith('_encrypted.bin'):
                # Remove _encrypted.bin and add _decrypted.bin
                base_name = filename.replace('_encrypted.bin', '')
                output_filename = base_name + '_decrypted.bin'
            else:
                # For files that don't follow the _encrypted.bin pattern
                name, ext = os.path.splitext(filename)
                output_filename = f"{name}_decrypted{ext}"
            
            # Always write decrypted output into the root uploads folder
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            
            # Ensure uploads directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            # Perform decryption
            try:
                decrypt_file(file_path, output_path)
                
                # Debug: check if file was created
                print(f"Decryption completed. Output file: {output_filename}")
                print(f"Output path: {output_path}")
                print(f"File exists: {os.path.exists(output_path)}")
                print(f"Uploads directory: {app.config['UPLOAD_FOLDER']}")
                print(f"Uploads directory exists: {os.path.exists(app.config['UPLOAD_FOLDER'])}")
                
                # List files in uploads directory for debugging
                if os.path.exists(app.config['UPLOAD_FOLDER']):
                    files_in_uploads = os.listdir(app.config['UPLOAD_FOLDER'])
                    print(f"Files in uploads directory: {files_in_uploads}")
                
                # Verify file was actually created
                if not os.path.exists(output_path):
                    raise Exception(f"Decryption failed: output file was not created at {output_path}")
                    
            except Exception as decrypt_error:
                print(f"Decryption error: {str(decrypt_error)}")
                raise decrypt_error
            
            # Clean up uploaded file (temporary encrypted upload under root uploads)
            try:
                os.remove(file_path)
            except Exception as _:
                pass
            
            return jsonify({'message': 'File decrypted successfully!', 'download_url': url_for('download_file', filename=output_filename)})
        except Exception as e:
            os.remove(file_path)
            return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    # Candidate search paths (absolute): root uploads, src/uploads (legacy), src/output
    candidate_paths = [
        os.path.join(app.config['UPLOAD_FOLDER'], filename),
        str(SRC_DIR / 'uploads' / filename),
        str(SRC_DIR / 'output' / filename),
    ]

    print(f"Looking for file to download: {filename}")
    for p in candidate_paths:
        print(f"Check: {p} exists={os.path.exists(p)}")
        if os.path.exists(p):
            return send_file(p, as_attachment=True)

    # As a final fallback, scan the root uploads dir for similarly named files
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        try:
            files_in_uploads = os.listdir(app.config['UPLOAD_FOLDER'])
            similar = [f for f in files_in_uploads if filename.replace('.bin','') in f or f.replace('.bin','') in filename]
            print(f"Similar in root uploads: {similar}")
            if similar:
                p = os.path.join(app.config['UPLOAD_FOLDER'], similar[0])
                if os.path.exists(p):
                    return send_file(p, as_attachment=True)
        except Exception as e:
            print(f"Error scanning uploads: {e}")

    flash(f'File not found: {filename}', 'error')
    return redirect(url_for('dashboard'))

@app.route('/generate-keys')
@login_required
def generate_keys():
    try:
        generate_rsa_keys()
        flash('RSA keys generated successfully!', 'success')
    except Exception as e:
        flash(f'Error generating keys: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
