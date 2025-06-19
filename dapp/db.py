# Import the SQLAlchemy extension for Flask
from flask_sqlalchemy import SQLAlchemy

# Create a SQLAlchemy database instance to be used throughout the application.
# This instance will be initialized with the Flask app in the app factory.
database = SQLAlchemy()