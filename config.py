import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'f222b590f87733a5b55dccc1c9050bd4cbc4fe82a2428459'
    
    # Update the database URI to use an environment variable
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False




"""""
import os

class Config:
    
    #Configuration class for the Flask application.
    #Contains database URI and a secret key for session management.
    
    # Secret key for signing session cookies and other security-related needs.
    # It's important to keep this value secret.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'f222b590f87733a5b55dccc1c9050bd4cbc4fe82a2428459'

    # Database configuration for PostgreSQL.
    # Replace the connection details with your actual PostgreSQL database credentials.
    # Format: postgresql://<user>:<password>@<host>:<port>/<dbname>
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or
        'postgresql://postgres:123654@localhost:5432/contacts_db'
    )

    # Disable modification tracking to save resources as we don't use this feature.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
"""