from .db import database
from .models import Candidate, Election, Otp, Vote, Voter, Position
from .role import AccountStatus, UserRole

# Retrieve section


def fetch_contract_address():
    election = Election.query.filter_by(
        id=1
    ).first()
    return election.contract_address


def fetch_admin_wallet_address():
    admin = Voter.query.filter_by(
        id=UserRole.ADMIN_ID
    ).first()
    return admin.wallet_address


def fetch_election():
    return Election.query.filter_by(
        id=1
    ).first()


# def fetch_voters_by_candidate_id(candidate_id):
#     return Voter.query.filter_by(
#         vote_status=candidate_id
#     ).order_by(Voter.id).all()
def fetch_voters_by_candidate_id(candidate_id):
    return (
        Voter.query
        .join(Vote, Voter.id == Vote.voter_id)
        .filter(Vote.candidate_id == candidate_id)
        .order_by(Voter.id)
        .all()
    )


def fetch_election_result():
    return Candidate.query.filter_by(
        candidate_status=AccountStatus.ACTIVE
    ).order_by(Candidate.vote_count.desc()).all()


def fetch_election_result_restricted():
    return Candidate.query.order_by(Candidate.vote_count.desc()).all()


def fetch_voter_by_username_hash_hex(username_hash_hex):
    return Voter.query.filter_by(
        username_hash_hex=username_hash_hex
    ).first()


def fetch_OTP_by_username_hash_hex(username_hash_hex):
    return Otp.query.filter_by(
        username_hash_hex=username_hash_hex
    ).first()


def fetch_all_voters():
    return Voter.query.filter(
        Voter.id > UserRole.ADMIN_ID
    ).all()


def fetch_candidate_by_id_restricted(candidate_id):
    return Candidate.query.with_entities(
        Candidate.id,
        Candidate.position_id,
        Candidate.name
    ).filter_by(
        id=candidate_id
    ).first()


def fetch_all_active_candidates():
    return Candidate.query.with_entities(
        Candidate.id,
        Candidate.position_id,
        Candidate.name
    ).filter(
        Candidate.candidate_status == AccountStatus.ACTIVE
    ).all()


def fetch_candidate_by_id(candidate_id):
    return Candidate.query.filter_by(
        id=candidate_id
    ).first()


def fetch_voter_by_id(voter_id):
    return Voter.query.filter_by(
        id=voter_id
    ).first()

def fetch_encrypted_private_key(username_hash):
    user = Voter.query.filter_by(username_hash=username_hash).first()
    return user.encrypted_private_key

def fetch_all_positions():
    positions = Position.query.all()
    return positions

def fetch_position_by_id(position_id):
    return Position.query.filter_by(
        id=position_id
    ).first()
    
def fetch_candidate_by_position_id(position_id):
    return Candidate.query.filter_by(
        position_id=position_id
    ).all()
    
def get_offchain_results():
    results = {}
    for candidate in Candidate.query.all():
        vote_count = len(candidate.votes)  # using backref or explicit query
        results[candidate.id] = vote_count
    return results
    
def count_votes_by_voter(voter_id):
    return Vote.query.filter_by(voter_id=voter_id).count()

def count_total_votes_cast():
    return Vote.query.count()

def count_total_possible_votes():
    return Voter.query.count() * Position.query.count()

# Block section


def ban_candidate_by_id(candidate_id):
    candidate = fetch_candidate_by_id(candidate_id)
    candidate.candidate_status = not candidate.candidate_status
    database.session.commit()
    return candidate


def ban_voter_by_id(voter_id):
    voter = fetch_voter_by_id(voter_id)
    voter.voter_status = not voter.voter_status
    database.session.commit()
    return voter

# Check section


def is_unverified_account(username_hash_hex):
    if Otp.query.filter_by(
        username_hash_hex=username_hash_hex
    ).first():
        return True
    return False


def is_username_hash_already_exists(username_hash):
    if Voter.query.filter_by(
        username_hash=username_hash
    ).all():
        return True
    return False


def is_email_already_exists(email):
    if Voter.query.filter_by(
        email_encrypted=email
    ).all():
        return True
    return False


def is_wallet_address_already_exists(wallet_address):
    if Voter.query.filter_by(
        wallet_address=wallet_address
    ).all():
        return True
    return False

def has_voted_for_position(voter_id, position_id):
    if Vote.query.filter_by(voter_id=voter_id, position_id=position_id).first():
        return True
    return False

# Add/Delete section


# def add_new_vote_record(voter, candidate):
#     voter.vote_status = candidate.id
#     candidate.vote_count += 1
#     database.session.commit()

def add_new_vote_record(voter, candidate, vote_hash):
    # Check if voter has already voted for this position
    if Vote.query.filter_by(
        voter_id=voter.id,
        candidate_id=candidate.id,
        position_id=candidate.position_id,
        vote_hash=vote_hash
    ).first():
        return False, "Voter has already voted for this position."

    # Add the new vote
    new_vote = Vote(
        voter_id=voter.id,
        candidate_id=candidate.id,
        position_id=candidate.position_id,
        vote_hash=vote_hash
    )

    candidate.vote_count += 1
    database.session.add(new_vote)
    database.session.commit()
    return True, "Vote recorded successfully."



def add_new_voter_signup(
        username_hash,
        username_hash_hex,
        password_hash,
        email_encrypted,
        wallet_address,
        private_key_encrypted,
        otp
):
    database.session.add(
        Voter(
            username_hash=username_hash,
            username_hash_hex=username_hash_hex,
            password=password_hash,
            email_encrypted=email_encrypted,
            wallet_address=wallet_address,
            private_key_encrypted=private_key_encrypted,
        )
    )
    database.session.add(
        Otp(
            username_hash_hex=username_hash_hex,
            otp=otp
        )
    )
    database.session.commit()


def delete_OTP(otp):
    database.session.delete(otp)
    database.session.commit()

def update_voter_wallet_by_username(username_hash_hex, new_wallet_address, new_encrypted_private_key):
    voter = Voter.query.filter_by(username_hash_hex=username_hash_hex).first()
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
    election = Election.query.filter_by(
        id=1
    ).first()
    election.status = not election.status
    database.session.commit()
    return election
