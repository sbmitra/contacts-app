import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

# --- App Initialization ---
app = Flask(__name__)
app.config.from_object(Config)

# --- Database Setup ---
db = SQLAlchemy(app)

# --- Login Manager Setup ---
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


# --- Database Models ---

class User(UserMixin, db.Model):
    """User model for storing user details."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    contacts = db.relationship('Contact', backref='owner', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Contact(db.Model):
    """Contact model for storing contact details."""
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Contact {self.first_name} {self.last_name}>'

# --- User Loader for Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    """Loads a user from the database given their ID."""
    return User.query.get(int(user_id))

# --- Routes ---

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    """Displays the user's dashboard with their contacts."""
    contacts = current_user.contacts
    return render_template('dashboard.html', user=current_user, contacts=contacts)

# --- Authentication Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another.', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use another.', 'danger')
            return redirect(url_for('register'))

        new_user = User(first_name=first_name, last_name=last_name, username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            # The flash message for successful login has been removed
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Handles user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Allows a user to edit their profile."""
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.email = request.form.get('email')
        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('edit_profile.html', user=current_user)

# --- Contact Management Routes ---
@app.route('/add_contact', methods=['GET', 'POST'])
@login_required
def add_contact():
    """Handles adding a new contact."""
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone_number = request.form.get('phone_number')
        email = request.form.get('email')
        address = request.form.get('address')
        new_contact = Contact(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            address=address,
            owner=current_user
        )
        db.session.add(new_contact)
        db.session.commit()
        flash('Contact added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_contact.html')

@app.route('/edit_contact/<int:contact_id>', methods=['GET', 'POST'])
@login_required
def edit_contact(contact_id):
    """Handles editing an existing contact."""
    contact = Contact.query.get_or_404(contact_id)
    # Ensure user can only edit their own contacts
    if contact.owner != current_user:
        flash('You are not authorized to edit this contact.', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        contact.first_name = request.form.get('first_name')
        contact.last_name = request.form.get('last_name')
        contact.phone_number = request.form.get('phone_number')
        contact.email = request.form.get('email')
        contact.address = request.form.get('address')
        db.session.commit()
        flash('Contact updated successfully!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('edit_contact.html', contact=contact)

@app.route('/delete_contact/<int:contact_id>', methods=['POST'])
@login_required
def delete_contact(contact_id):
    """Handles deleting a contact."""
    contact = Contact.query.get_or_404(contact_id)
    # Ensure user can only delete their own contacts
    if contact.owner != current_user:
        flash('You are not authorized to delete this contact.', 'danger')
        return redirect(url_for('dashboard'))
    
    db.session.delete(contact)
    db.session.commit()
    flash('Contact deleted successfully.', 'success')
    return redirect(url_for('dashboard'))

# A simple password reset placeholder
# In a real app, this would generate a token and email it to the user.
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    """A placeholder for the password reset functionality."""
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # In a real app, you'd generate a secure token and email a reset link.
            flash('If an account with that email exists, a password reset link has been sent.', 'info')
        else:
            flash('If an account with that email exists, a password reset link has been sent.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html')


# --- Main execution ---
if __name__ == '__main__':
    with app.app_context():
        # This will create the database tables if they don't exist
        db.create_all()
    app.run(debug=True)