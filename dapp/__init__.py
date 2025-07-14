import csv 
import json
import sys
import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from web3 import Web3
from .cryptography import encrypt_object
from .ethereum import Blockchain
from .db import database
from .db_operations import fetch_admin_wallet_address, fetch_contract_address

# Load admin private key from environment variable
load_dotenv()
ADMIN_PRIVATE_KEY = os.getenv("ADMIN_PRIVATE_KEY")


def init_candidates(path, db, Candidate):
    """
    Registers candidates from a CSV file to both the blockchain and the local database.

    For each candidate in the CSV file, this function:
    - Hashes the candidate's name and position.
    - Registers the candidate on the blockchain using the admin's credentials.
    - Adds the candidate to the local database if blockchain registration is successful.

    Args:
        path (str): Path to the candidates CSV file.
        db (SQLAlchemy): Database instance to add candidates.
        Candidate (Model): Candidate model/table in the database.
    """
    
    # Creates a blockchain object using admin credentials
    blockchain = Blockchain(fetch_admin_wallet_address(), fetch_contract_address())
    
    # Opens the csv file
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        next(csv_reader)

        for row in csv_reader:
            candidate_hash = Web3.keccak(text=f"{row[1]}-{row[2]}") # Hashes candidate name and position
           
           # Registers a candidate on-chain, signed by admin
            status, msg = blockchain.register_candidate(
                ADMIN_PRIVATE_KEY, row[2], candidate_hash
            )

            # sys.stdout.write(f'Candidate {row[1]} registration status: {msg}, candidate_hash: {candidate_hash.hex()} \n')
            # If the candidate was successfully registered on-chain, add them to the database
            if status:
                db.session.add(
                    Candidate(
                        id=row[0],
                        name=row[1],
                        position_id=row[2],
                        candidate_hash=candidate_hash.hex(),
                    )
                )
                sys.stdout.write(f' \r Successfully registered candidate {row[1]} \n')
            
        db.session.commit()


def init_positions(path, db, Position):
    """
    Adds election positions from a CSV file to the local database.

    Reads each position from the CSV file and inserts it into the database.

    Args:
        path (str): Path to the positions CSV file.
        db (SQLAlchemy): Database instance to add positions.
        Position (Model): Position model/table in the database.
    """
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        next(csv_reader)

        for row in csv_reader:
            db.session.add(Position(id=row[0], position=row[1])) # Adds position to database
        db.session.commit()


def setup_admin(path, db, Users, Election):
    """
    Sets up the admin user and election contract in the database.

    Reads admin user details and contract address from a JSON file, then adds the admin user
    and election contract to the database.

    Args:
        path (str): Path to the JSON file containing admin user details.
        db (SQLAlchemy database): Database instance to add the admin user and election contract.
        Users (Model): User model/table in the database.
        Election (Model): Election model/table in the database.
    """
    print("Setting up admin user...")
    with open(path) as json_file:
        admin_user_details = json.loads(json_file.read())
        
        # Add admin user to database
        db.session.add(
            Users(
                username_hash=Web3.keccak(text=admin_user_details["username"]).hex(), # Hashes the username
                password=generate_password_hash(admin_user_details["passwd"]), # Hashes the password
                wallet_address=admin_user_details["wallet"],
                voter_status=False, # Prevents admin from voting
            )
        )
        db.session.add(
            Election(contract_address=admin_user_details["contract_address"]) # Adds election contract to database
        )
        db.session.commit()


def create_app():
    """
    Creates and configures the Flask application for the eVoting blockchain project.

    - Sets up application configuration, database, and login management.
    - Initializes the database and populates it with admin, candidates, and positions if running for the first time.
    - Registers Flask blueprints for main, auth, and admin modules.

    Returns:
        Flask: The configured Flask application instance.
    """
    
    WORKING_DIRECTORY = os.getcwd() # Gets the current working directory
    DB_NAME = "offchain87.sqlite" # Database name
    CANDIDATES_DIR = f"{WORKING_DIRECTORY}/CSV/candidates.csv" # Candidates CSV file path
    POSITIONS_DIR = f"{WORKING_DIRECTORY}/CSV/positions.csv" # Positions CSV file path
    ADMIN_DIR = f"{WORKING_DIRECTORY}/admin/admin.json" # Admin user details JSON file path

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.config["EPOCH"] = not os.path.exists(f"{WORKING_DIRECTORY}/instance/{DB_NAME}")
    app.config["SQLALCHEMY_ECHO"] = False

    database.init_app(app)

    from . import models

    with app.app_context():
        database.create_all() # Creates the database tables if they do not exist

        if app.config["EPOCH"]:
            sys.stdout.write("Creating database \n")
            setup_admin(ADMIN_DIR, database, models.Voter, models.Election)
            init_candidates(
                CANDIDATES_DIR,
                database,
                models.Candidate,
            )
            init_positions(POSITIONS_DIR, database, models.Position)
            sys.stdout.write("Database created and admin user added \n")
            sys.stdout.flush()

    login_manager = LoginManager()
    login_manager.login_view = "auth.index"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return models.Voter.query.get(int(user_id))

    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint)

    from .admin import admin as admin_blueprint

    app.register_blueprint(admin_blueprint)

    return app
