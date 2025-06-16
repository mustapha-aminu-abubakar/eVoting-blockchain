import csv
import hashlib
import json
import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from web3 import Web3
from .cryptography import encrypt_object
from .ethereum import Blockchain
from .models import Candidate, Position, Voter, Election
from .db import database
from .db_operations import fetch_admin_wallet_address, fetch_contract_address

load_dotenv()
ADMIN_PRIVATE_KEY = os.getenv("ADMIN_PRIVATE_KEY")

def init_candidates(path, db, Candidate):
    blockchain = Blockchain(
        fetch_admin_wallet_address(),
        fetch_contract_address()
    )
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        next(csv_reader)

        for row in csv_reader:
            candidate_hash = Web3.keccak(text=f'{row[1]}-{row[2]}')
            _, msg = blockchain.register_candidate(
                ADMIN_PRIVATE_KEY, 
                row[2], 
                candidate_hash
                )
            
            print(f"Candidate {row[1]} registration status: {msg}, candidate_hash: {candidate_hash.hex()}")
            db.session.add(Candidate(
                id=row[0], 
                name=row[1], 
                position_id=row[2],
                candidate_hash=candidate_hash.hex())
            )
        db.session.commit()


def init_positions(path, db, Position):
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        next(csv_reader)

        for row in csv_reader:
            db.session.add(Position(id=row[0], position=row[1]))
        db.session.commit()


def setup_admin(path, db, Users, Election):
    print("Setting up admin user...")
    with open(path) as json_file:
        admin_user_details = json.loads(json_file.read())
        db.session.add(
            Users(
                username_hash = Web3.keccak(text=admin_user_details["username"]).hex(),
                password=generate_password_hash(admin_user_details["passwd"]), 
                wallet_address=admin_user_details["wallet"],
                voter_status=False,
            )
        )
        db.session.add(
            Election(contract_address=admin_user_details["contract_address"])
        )
        db.session.commit()


def create_app():
    WORKING_DIRECTORY = os.getcwd()
    DB_NAME = "offchain77.sqlite"
    CANDIDATES_DIR = f"{WORKING_DIRECTORY}/CSV/candidates.csv"
    POSITIONS_DIR = f"{WORKING_DIRECTORY}/CSV/positions.csv"
    ADMIN_DIR = f"{WORKING_DIRECTORY}/admin/admin.json"

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.config["EPOCH"] = not os.path.exists(f"{WORKING_DIRECTORY}/instance/{DB_NAME}")
    # app.config['EPOCH'] = not os.path.exists(DB_NAME)
    app.config["SQLALCHEMY_ECHO"] = False

    database.init_app(app)

    from . import models

    with app.app_context():
        database.create_all()

        if app.config["EPOCH"]:
            print("Creating database")
            setup_admin(ADMIN_DIR, database, models.Voter, models.Election)
            init_candidates(
                CANDIDATES_DIR,
                database,
                models.Candidate,
            )
            init_positions(POSITIONS_DIR, database, models.Position)
            print("Database created and admin user added.")

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
