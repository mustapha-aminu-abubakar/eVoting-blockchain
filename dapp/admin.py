import sys

from flask import Blueprint, flash, redirect, render_template, request, url_for, session
from flask_login import current_user, login_required

from .db_operations import (ban_candidate_by_id, ban_voter_by_id,
                            fetch_admin_wallet_address, fetch_all_voters,
                            fetch_contract_address, fetch_election,
                            fetch_election_result, count_votes_by_voter,
                            fetch_election_result_restricted,
                            fetch_voters_by_candidate_id, publish_result,
                            count_total_votes_cast, count_total_possible_votes,
                            fetch_all_positions, add_votes, add_results, fetch_all_candidates,
                            fetch_all_votes, fetch_all_transactions)
from .ethereum import Blockchain
from .role import ElectionStatus
from .models import Candidate, Voter, Vote, Result
from .db import database
from .validator import (convert_to_unix_timestamp, count_max_vote_owner_id,
                        count_total_vote_cast, is_admin, sha256_hash,
                        validate_result_hash)
from datetime import datetime

admin = Blueprint('admin', __name__)


@admin.route('/admin_panel')
@login_required
def admin_panel():
    """
    Renders the admin panel with election, voter, candidate, and transaction data.

    Only accessible to admin users. Fetches all relevant information from the database and blockchain,
    then renders the admin panel template with this data.
    """

    # Access deny for non-admin users
    if not is_admin(current_user):
        return redirect(url_for('auth.index'))

    # Create a blockchain object
    blockchain = Blockchain(
        fetch_admin_wallet_address(),
        fetch_contract_address()
    )
    # Fetch important information
    election = fetch_election()
    voters = fetch_all_voters()
    total_votes_possible = count_total_possible_votes()
    votes = fetch_all_votes()
    candidates = fetch_all_candidates()
    positions = fetch_all_positions()
    txns = fetch_all_transactions()

    return render_template(
        'admin_panel.html',
        election_status=election.status,
        candidates=candidates,
        txns=txns,
        total_votes_possible=total_votes_possible,
        votes=votes,
        ts_to_dt=datetime.utcfromtimestamp
    )

@admin.route('/publish')
@login_required
def publish_results():
    """
    Publishes the election results to the blockchain and displays grouped results.

    Only accessible to admin users. Calls the blockchain to publish results, fetches and prints grouped results and votes,
    and handles exceptions by flashing error messages.
    """
    # Access denied for non-admin users
    if not is_admin(current_user):
        return redirect(url_for('auth.index'))
    try:
        blockchain = Blockchain( # Create Blockchain object
            fetch_admin_wallet_address(), 
            fetch_contract_address()
        )
        status, tx_receipt = blockchain.publish() # Publish on-chain election results
    except Exception as e:
        flash(str(e), 'error')
        status = False
    
    # If publish successful, fetch election aggregated results and all votes cast
    if status:       
        results = blockchain.group_candidates_by_position() 
        votes = blockchain.get_all_votes()   

        print(f'Fetched results for {len(results)} positions')
        print(f'Fetched {len(votes)} votes')
        
        try: # Adds aggregated results to local database
            sys.stdout.write('Writing results to database ...   \n')
            add_results(results)
        except Exception as e:
            print(f'Could not enter results: {e}')
            
        try: # Adds fetched votes to local database
            sys.stdout.write('Adding votes to database ...   \n')
            add_votes(votes)    
        except Exception as e:
            print(f'Could not enter votes: {e}')
        
        # Locks Voter, Vote and Result models, preventing manipulation
        Voter.lock_all(database.session)
        Vote.lock_all(database.session)
        Result.lock_all(database.session)
        sys.stdout.write(f'Voter model is_locked: {Voter.is_locked(database.session)}')
        sys.stdout.write(f'Votes model is_locked: {Vote.is_locked(database.session)}')
        sys.stdout.write(f'Result model is_locked: {Result.is_locked(database.session)}')
        flash(f"Results published. Tx: {tx_receipt}")
    
    return redirect(url_for('admin.admin_panel'))

@admin.route('/block_candidate/<int:candidate_id>')
@login_required
def block_candidate(candidate_id):
    """
    Blocks or unblocks a candidate by their ID.

    Only accessible to admin users. Toggles the candidate's status and flashes a message indicating the new status.
    
    Args:
        candidate_id (int): The ID of the candidate to block or unblock.
    """
    # Access deny for other
    if not is_admin(current_user):
        return redirect(url_for('auth.index'))

    candidate = ban_candidate_by_id(candidate_id)
    flash(
        f"Candidate {candidate.name} ({candidate.username}) is {'Unblocked' if candidate.candidate_status else 'Blocked'}"
    )
    return redirect(url_for('admin.admin_panel'))


@admin.route('/block_voter/<int:voter_id>')
@login_required
def block_voter(voter_id):
    """
    Blocks or unblocks a voter by their ID.

    Only accessible to admin users. Toggles the voter's status and flashes a message indicating the new status.
    
    Args:
        voter_id (int): The ID of the voter to block or unblock.
    """

    # Access deny for other
    if not is_admin(current_user):
        return redirect(url_for('auth.index'))

    voter = ban_voter_by_id(voter_id)
    flash(
        f"Voter ({voter.username_hash}) is {'Unblocked' if voter.voter_status else 'Blocked'}"
    )
    return redirect(url_for('admin.admin_panel'))


@admin.route('/update_time', methods=['POST'])
@login_required
def update_time_post():
    """
    Extends or updates the end time of the election.

    Only accessible to admin users. Processes form data to update the election's start and end times on the blockchain.
    """
    # Access deny for other
    if not is_admin(current_user):
        return redirect(url_for('auth.index'))

    # Get new time and private key input
    start_time = request.form.get('start_time').strip()
    end_time = request.form.get('end_time').strip()
    tz = request.form.get('tz').strip()
    private_key = request.form.get('private_key').strip()
    
    print(f'[flask UI] Start time: {start_time}, End time: {end_time}, timezone: {tz}')

    blockchain = Blockchain(
        fetch_admin_wallet_address(),
        fetch_contract_address()
    )

    def show_flash_msg(status, tx_msg):
        """
        Displays a flash message indicating the status of a blockchain transaction.

        Args:
            status (bool): Whether the transaction was successful.
            tx_msg (str): The transaction hash or message.
        """
        if status:
            flash(f'[Updated] Tx HASH: {tx_msg}')
        else:
            flash(f'[Failed] Tx HASH: {tx_msg}')

    if not private_key:
        flash('Private key empty')
        return redirect(url_for('admin.admin_panel'))
    elif start_time and end_time:
        # Sending transaction for setting start and end time of election
        status, tx_msg = blockchain.set_voting_time(
            start_time,
            end_time,
            tz
        )
        show_flash_msg(status, tx_msg)

    elif end_time:
        # Sending transaction for extending the time
        status, tx_msg = blockchain.extend_time(
            convert_to_unix_timestamp(end_time)
        )
        show_flash_msg(status, tx_msg)
    times = blockchain.get_voting_time()
    print(times)

    return redirect(url_for('admin.admin_panel'))
