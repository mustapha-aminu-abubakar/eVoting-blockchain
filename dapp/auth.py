from flask import Blueprint, flash, redirect, render_template, request, url_for, session
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from web3 import Web3

from .credentials import EMAIL_SERVICE
from .db_operations import (
    add_new_voter_signup,
    delete_OTP,
    fetch_OTP_by_username_hash,
    fetch_voter_by_username_hash,
    fetch_admin_wallet_address,
    fetch_contract_address,
    is_unverified_account,
    is_username_hash_already_exists,
    fetch_encrypted_private_key,
    is_wallet_address_already_exists,
    is_email_already_exists,
    update_voter_wallet_by_username,
)
from .models import Candidate, Position
from .mail_server import MailServer
from .role import AccountStatus
from .validator import (
    generate_opt,
    is_admin,
    sha256_hash,
    validate_signin,
    validate_signup,
)
from .ethereum import Blockchain, fund_new_user_wallet, get_voting_time
from .cryptography import encrypt_object, decrypt_object
from .db import database
from datetime import datetime


auth = Blueprint("auth", __name__)


@auth.route("/")
def index():
    """
    Displays the login page and handles user session redirection.

    - If the user is not authenticated, shows the login page.
    - If the user is an admin, redirects to the admin panel.
    - If the user is a voter, redirects to the candidate positions page.
    - Locks all candidates and positions if not already locked.
    """

    if not Candidate.is_locked(database.session) or not Position.is_locked(
        database.session
    ):
        Candidate.lock_all(
            database.session
        )  # Lock all candidates to prevent modifications
        Position.lock_all(
            database.session
        )  # Lock all positions to prevent modifications

    # Returns to root page if user is not already registered
    if not current_user.is_authenticated:
        return render_template("index.html")

    # Redirects to admin panel if user is admin
    if is_admin(current_user):
        return redirect(url_for("admin.admin_panel"))

    # Redirects to candidate positions page
    return redirect(url_for("main.positions"))


@auth.route("/signup")
def signup():
    """
    Displays the signup page for new voters.
    """
    return render_template("signup.html")


@auth.route("/signin", methods=["POST"])
def signin_post():
    """
    Handles POST requests for user login (voters and admin).

    - Validates credentials and user status.
    - Redirects to OTP verification if needed.
    - Starts a login session and redirects based on user role.
    - Handles blocked users and incorrect credentials.
    """

    # Get the input credentials
    username = request.form.get("username").strip()
    password = request.form.get("pwd").strip()

    # Username HASH
    username_hash = Web3.keccak(text=username).hex()

    # Validate the inputs
    valid, msg = validate_signin(username, password)
    if not valid:
        flash(msg)
        return redirect(url_for("auth.index"))

    # Get the voter details
    voter = fetch_voter_by_username_hash(username_hash)

    # If voter not found in DB
    if not voter:
        flash("User not found!")
        return redirect(url_for("auth.signup"))

    # If OTP is not verified
    if is_unverified_account(username_hash):
        return render_template("otp.html", username_hash=username_hash)

    # Input password check
    if not check_password_hash(voter.password, password):
        flash("Incorrect password")
        return redirect(url_for("auth.index"))

    # If the user is ADMIN
    if is_admin(voter):
        login_user(voter)  # login session
        return redirect(url_for("admin.admin_panel"))

    # If the user is blocked
    if voter.voter_status == AccountStatus.BLOCKED:
        flash(f"{username_hash} is blocked by ADMIN")
        return render_template("error.html", error_msg="BLOCKED")
    
    # Check if voter is trying to sign in within the election window
    start_time, end_time = get_voting_time()
    print(f"Election start time: {start_time}, end time: {end_time}")
    if not start_time or not (start_time <= datetime.utcnow().timestamp() <= end_time):
        flash("Sign in is only allowed during the election window.")
        return render_template("index.html")

    # Start login session
    login_user(voter)
    return redirect(url_for("main.positions"))


@auth.route("/logout")
@login_required
def logout():
    """
    Logs out the current user and redirects to the login page.
    """
    logout_user()
    return redirect(url_for("auth.index"))


@auth.route("/signup", methods=["POST"])
def signup_post():
    """
    Handles POST requests for voter registration.

    - Validates and processes signup form data.
    - Checks for duplicate usernames and emails.
    - Sends OTP to the user's email if email service is enabled.
    - Adds the new voter to the database and prompts for OTP verification.
    """

    # Get input details
    username = request.form.get("username").strip()
    password = request.form.get("pwd").strip()
    confirm_password = request.form.get("cnf_pwd").strip()
    email = request.form.get("email").strip()

    # Create hashs
    username_hash = Web3.keccak(text=username).hex()
    password_hash = generate_password_hash(
        password
    )  # used different hashing technique for easier comparison

    # Validate inputs
    valid, msg = validate_signup(username, password, confirm_password)
    # If inputs are not valid
    if not valid:
        flash(msg)
        return redirect(url_for("auth.signup"))

    # If duplicate username
    if is_username_hash_already_exists(username_hash):
        flash("Already registerd voter")
        return redirect(url_for("auth.index"))

    # if duplicate email address
    if is_email_already_exists(encrypt_object(email)):
        flash("Email is already used")
        return redirect(url_for("auth.signup"))

    # Generates one-time-password, optionally sends it to input email address
    else:
        otp = generate_opt(6)
        print(f"OTP: {otp}")

        if EMAIL_SERVICE:
            mail_agent = MailServer()
            status = mail_agent.send_mail(email, otp)
            print(f"Otp email to {email}: {status}")
            flash(f"Enter the code sent to {email}")

        # Add new user off-chain to DB
        add_new_voter_signup(
            username_hash,
            password_hash,
            encrypt_object(email),
            "",
            "",
            generate_password_hash(otp),
        )

        return render_template("otp.html", username_hash=username_hash)


@auth.route("/verify_otp/<string:username_hash>", methods=["POST"])
def verify_otp_post(username_hash):
    """
    Handles OTP verification for new voter registration.

    - Checks the submitted OTP against the stored value.
    - If correct, completes registration and funds the user's wallet.
    - If incorrect, prompts the user to try again.

    Args:
        username_hash (str): The hash of the username for OTP lookup.
    """

    # Get input OTP
    user_otp = request.form.get("otp").strip()

    otp = fetch_OTP_by_username_hash(username_hash)

    # If not such OTP exist
    if not otp:
        return redirect(url_for("auth.index"))

    if check_password_hash(otp.otp, user_otp):
        delete_OTP(otp)
        status, e = fund_new_user_wallet(username_hash)
        flash("Voter registration complete")
        flash(f"{e}")
        return redirect(url_for("auth.index"))

    flash("Incorrect OTP")
    return render_template("otp.html", username_hash=username_hash)
