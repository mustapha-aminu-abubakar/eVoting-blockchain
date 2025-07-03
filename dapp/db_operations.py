from .db import database
from .models import Candidate, Election, Otp, Vote, Voter, Position, Result, Transaction
from .role import AccountStatus, UserRole

# Retrieve section


def fetch_contract_address():
    """
    Retrieves the contract address of the election from the database.

    Returns:
        str: The contract address.
    """
    election = Election.query.filter_by(id=1).first()
    return election.contract_address


def fetch_admin_wallet_address():
    """
    Retrieves the admin's wallet address from the database.

    Returns:
        str: The admin's wallet address.
    """
    admin = Voter.query.filter_by(id=UserRole.ADMIN_ID).first()
    return admin.wallet_address


def fetch_election():
    """
    Retrieves the election object from the database.

    Returns:
        Election: The election object.
    """
    return Election.query.filter_by(id=1).first()


def fetch_voters_by_candidate_id(candidate_id):
    """
    Retrieves all voters who voted for a specific candidate.

    Args:
        candidate_id (int): The candidate's ID.

    Returns:
        list[Voter]: List of voters.
    """
    return (
        Voter.query.join(Vote, Voter.id == Vote.voter_id)
        .filter(Vote.candidate_id == candidate_id)
        .order_by(Voter.id)
        .all()
    )


def fetch_election_result():
    """
    Retrieves all active candidates ordered by vote count (descending).

    Returns:
        list[Candidate]: List of active candidates.
    """
    return (
        Candidate.query.filter_by(candidate_status=AccountStatus.ACTIVE)
        .order_by(Candidate.vote_count.desc())
        .all()
    )


def fetch_election_result_restricted():
    """
    Retrieves all candidates ordered by vote count (descending).

    Returns:
        list[Candidate]: List of candidates.
    """
    return Candidate.query.order_by(Candidate.vote_count.desc()).all()


def fetch_voter_by_username_hash(username_hash):
    """
    Retrieves a voter by their username hash.

    Args:
        username_hash (str): The voter's username hash.

    Returns:
        Voter: The voter object or None.
    """
    return Voter.query.filter_by(username_hash=username_hash).first()


def fetch_OTP_by_username_hash(username_hash):
    """
    Retrieves the OTP object for a given username hash.

    Args:
        username_hash (str): The voter's username hash.

    Returns:
        Otp: The OTP object or None.
    """
    return Otp.query.filter_by(username_hash=username_hash).first()


def fetch_all_voters():
    """
    Retrieves all voters except the admin.

    Returns:
        list[Voter]: List of voters.
    """
    return Voter.query.filter(Voter.id > UserRole.ADMIN_ID).all()


def fetch_candidate_by_id_restricted(candidate_id):
    """
    Retrieves limited fields for a candidate by ID.

    Args:
        candidate_id (int): The candidate's ID.

    Returns:
        Candidate: The candidate object or None.
    """
    return (
        Candidate.query.with_entities(
            Candidate.id, Candidate.position_id, Candidate.name
        )
        .filter_by(id=candidate_id)
        .first()
    )


def fetch_all_active_candidates():
    """
    Retrieves all active candidates with limited fields.

    Returns:
        list[Candidate]: List of active candidates.
    """
    return (
        Candidate.query.with_entities(
            Candidate.id, Candidate.position_id, Candidate.name
        )
        .filter(Candidate.candidate_status == AccountStatus.ACTIVE)
        .all()
    )


def fetch_all_candidates():
    """
    Retrieves all candidates.

    Returns:
        list[Candidate]: List of all candidates.
    """
    return Candidate.query.all()


def fetch_candidate_by_id(candidate_id):
    """
    Retrieves a candidate by their ID.

    Args:
        candidate_id (int): The candidate's ID.

    Returns:
        Candidate: The candidate object or None.
    """
    return Candidate.query.filter_by(id=candidate_id).first()


def fetch_candidate_by_hash(candidate_hash):
    """
    Retrieves a candidate by their hash.

    Args:
        candidate_hash (str): The candidate's hash.

    Returns:
        Candidate: The candidate object or None.
    """
    return Candidate.query.filter_by(candidate_hash=candidate_hash).first()


def fetch_voter_by_id(voter_id):
    """
    Retrieves a voter by their ID.

    Args:
        voter_id (int): The voter's ID.

    Returns:
        Voter: The voter object or None.
    """
    return Voter.query.filter_by(id=voter_id).first()


def fetch_encrypted_private_key(username_hash):
    """
    Retrieves the encrypted private key for a voter by username hash.

    Args:
        username_hash (str): The voter's username hash.

    Returns:
        str: The encrypted private key.
    """
    user = Voter.query.filter_by(username_hash=username_hash).first()
    return user.encrypted_private_key


def fetch_all_positions():
    """
    Retrieves all positions.

    Returns:
        list[Position]: List of all positions.
    """
    positions = Position.query.all()
    return positions


def fetch_position_by_id(position_id):
    """
    Retrieves a position by its ID.

    Args:
        position_id (int): The position's ID.

    Returns:
        Position: The position object or None.
    """
    return Position.query.filter_by(id=position_id).first()


def fetch_candidate_by_position_id(position_id):
    """
    Retrieves all candidates for a given position.

    Args:
        position_id (int): The position's ID.

    Returns:
        list[Candidate]: List of candidates for the position.
    """
    return Candidate.query.filter_by(position_id=position_id).all()


def get_offchain_results():
    """
    Retrieves the vote count for each candidate from the database.

    Returns:
        dict: Mapping of candidate IDs to vote counts.
    """
    results = {}
    for candidate in Candidate.query.all():
        vote_count = len(candidate.votes)  # using backref or explicit query
        results[candidate.id] = vote_count
    return results


def count_votes_by_voter(voter_id):
    """
    Counts the number of votes cast by a voter.

    Args:
        voter_id (int): The voter's ID.

    Returns:
        int: Number of votes cast.
    """
    return Vote.query.filter_by(voter_id=voter_id).count()


def count_total_votes_cast():
    """
    Counts the total number of votes cast.

    Returns:
        int: Total votes cast.
    """
    return Vote.query.count()


def count_total_possible_votes():
    """
    Calculates the total possible votes (voters x positions).

    Returns:
        int: Total possible votes.
    """
    return Voter.query.count() * Position.query.count()


def fetch_all_results():
    """
    Retrieves all election results.

    Returns:
        list[Result]: List of all results.
    """
    return Result.query.all()


def fetch_vote_by_candidate_id(candidate_id):
    """
    Retrieves all votes for a specific candidate.

    Args:
        candidate_id (int): The candidate's ID.

    Returns:
        list[Vote]: List of votes.
    """
    return Vote.query.filter_by(candidate_id=candidate_id).all()


def fetch_all_votes():
    """
    Retrieves all votes.

    Returns:
        list[Vote]: List of all votes.
    """
    return Vote.query.all()


def fetch_votes_by_candidate_hash(candidate_hash):
    """
    Retrieves all votes for a specific candidate hash.

    Args:
        candidate_hash (str): The candidate's hash.

    Returns:
        list[Vote]: List of votes.
    """
    return Vote.query.filter_by(candidate_hash=candidate_hash)


def fetch_all_transactions():
    """
    Retrieves all blockchain transaction records.

    Returns:
        list[Transaction]: List of all transactions.
    """
    return Transaction.query.order_by(Transaction.txn_ts.desc()).all()


# Block section


def ban_candidate_by_id(candidate_id):
    """
    Toggles the block status of a candidate by their ID.

    Args:
        candidate_id (int): The candidate's ID.

    Returns:
        Candidate: The updated candidate object.
    """
    candidate = fetch_candidate_by_id(candidate_id)
    candidate.candidate_status = not candidate.candidate_status
    database.session.commit()
    return candidate


def ban_voter_by_id(voter_id):
    """
    Toggles the block status of a voter by their ID.

    Args:
        voter_id (int): The voter's ID.

    Returns:
        Voter: The updated voter object.
    """
    voter = fetch_voter_by_id(voter_id)
    voter.voter_status = not voter.voter_status
    database.session.commit()
    return voter


# Check section


def is_unverified_account(username_hash):
    """
    Checks if an account with the given username hash is unverified (has an OTP).

    Args:
        username_hash (str): The voter's username hash.

    Returns:
        bool: True if unverified, False otherwise.
    """
    if Otp.query.filter_by(username_hash=username_hash).first():
        return True
    return False


def is_username_hash_already_exists(username_hash):
    """
    Checks if a username hash already exists in the database.

    Args:
        username_hash (str): The voter's username hash.

    Returns:
        bool: True if the username hash exists, False otherwise.
    """
    if Voter.query.filter_by(username_hash=username_hash).all():
        return True
    return False


def is_email_already_exists(email):
    """
    Checks if an encrypted email already exists in the database.

    Args:
        email (str): The encrypted email.

    Returns:
        bool: True if the email exists, False otherwise.
    """
    if Voter.query.filter_by(email_encrypted=email).all():
        return True
    return False


def is_wallet_address_already_exists(wallet_address):
    """
    Checks if a wallet address already exists in the database.

    Args:
        wallet_address (str): The wallet address.

    Returns:
        bool: True if the wallet address exists, False otherwise.
    """
    if Voter.query.filter_by(wallet_address=wallet_address).all():
        return True
    return False


def has_voted_for_position(voter_id, position_id):
    """
    Checks if a voter has already voted for a specific position.

    Args:
        voter_id (int): The voter's ID.
        position_id (int): The position's ID.

    Returns:
        bool: True if the voter has voted for the position, False otherwise.
    """
    if Vote.query.filter_by(voter_id=voter_id, position_id=position_id).first():
        return True
    return False


# Add/Delete section


def add_results(results):
    """
    Adds election results to the database.

    Args:
        results (dict): Dictionary mapping positions to candidate result data.

    Returns:
        tuple: (bool, str) indicating success and a message.
    """
    new_results = []

    for position, candidates in results.items():
        for candidate in candidates:
            result_entry = Result(
                position_id=candidate["position_id"],
                position=candidate["position"],
                candidate_name=candidate["name"],
                candidate_hash=candidate["candidate_hash"],
                vote_count=candidate["vote_count"],
                is_winner=candidate["is_winner"],
            )
            new_results.append(result_entry)
    database.session.add_all(new_results)
    database.session.commit()
    return True, "Result added successfully."


def add_votes(votes):
    """
    Adds multiple votes to the database.

    Args:
        votes (list): List of vote data tuples.

    Returns:
        tuple: (bool, str) indicating success and a message.
    """
    new_votes = [
        Vote(
            position_id=position_id,
            voter_hash=voter_hash.hex(),
            candidate_hash=candidate_hash.hex(),
            date_time_ts=date_time_ts,
            wallet_address=wallet_address,
        )
        for position_id, voter_hash, candidate_hash, date_time_ts, wallet_address in votes
    ]

    database.session.add_all(new_votes)
    database.session.commit()
    return True, "Vote added successfully."


def add_new_vote_record(voter, candidate, vote_hash):
    """
    Adds a new vote record for a voter and candidate, if not already voted.

    Args:
        voter (Voter): The voter object.
        candidate (Candidate): The candidate object.
        vote_hash (str): The hash of the vote.

    Returns:
        tuple: (bool, str) indicating success and a message.
    """
    if Vote.query.filter_by(
        voter_id=voter.id,
        candidate_id=candidate.id,
        position_id=candidate.position_id,
        vote_hash=vote_hash,
    ).first():
        return False, "Voter has already voted for this position."

    # Add the new vote
    new_vote = Vote(
        voter_id=voter.id,
        candidate_id=candidate.id,
        position_id=candidate.position_id,
        vote_hash=vote_hash,
    )

    candidate.vote_count += 1
    database.session.add(new_vote)
    database.session.commit()
    return True, "Vote recorded successfully."


def add_new_voter_signup(
    username_hash,
    password_hash,
    email_encrypted,
    wallet_address,
    private_key_encrypted,
    otp,
):
    """
    Adds a new voter and their OTP to the database during signup.

    Args:
        username_hash (str): The voter's username hash.
        password_hash (str): The voter's hashed password.
        email_encrypted (str): The voter's encrypted email.
        wallet_address (str): The voter's wallet address.
        private_key_encrypted (str): The voter's encrypted private key.
        otp (str): The OTP for verification.
    """
    database.session.add(
        Voter(
            username_hash=username_hash,
            password=password_hash,
            email_encrypted=email_encrypted,
            wallet_address=wallet_address,
            private_key_encrypted=private_key_encrypted,
        )
    )
    database.session.add(Otp(username_hash=username_hash, otp=otp))
    database.session.commit()


def add_txn(txn_hash, status, sender, gas):
    """
    Adds a new blockchain transaction record to the database.

    Args:
        txn_hash (str): The transaction hash.
        status (str): The transaction status.
        sender (str): The sender's address.
        gas (int): The gas used for the transaction.
    """
    new_txn = Transaction(txn_hash=txn_hash, status=status, sender=sender, gas=gas)
    database.session.add(new_txn)
    database.session.commit()


def delete_OTP(otp):
    """
    Deletes an OTP record from the database.

    Args:
        otp (Otp): The OTP object to delete.
    """
    database.session.delete(otp)
    database.session.commit()


def update_voter_wallet_by_username(
    username_hash, new_wallet_address, new_encrypted_private_key
):
    """
    Updates a voter's wallet address and encrypted private key.

    Args:
        username_hash (str): The voter's username hash.
        new_wallet_address (str): The new wallet address.
        new_encrypted_private_key (str): The new encrypted private key.

    Returns:
        tuple: (bool, str) indicating success and a message.
    """
    voter = Voter.query.filter_by(username_hash=username_hash).first()
    try:
        voter.wallet_address = new_wallet_address
        voter.private_key_encrypted = new_encrypted_private_key
        database.session.commit()
        return True, "Wallet info updated successfully"
    except Exception as e:
        database.session.rollback()
        return False, str(e)


# Publish


def publish_result():
    """
    Toggles the election's published status and commits the change.

    Returns:
        Election: The updated election object.
    """
    election = Election.query.filter_by(id=1).first()
    election.status = not election.status
    database.session.commit()
    return election
