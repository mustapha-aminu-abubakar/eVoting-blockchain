

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from .db_operations import (ban_candidate_by_id, ban_voter_by_id,
                            fetch_admin_wallet_address, fetch_all_voters,
                            fetch_contract_address, fetch_election,
                            fetch_election_result, count_votes_by_voter,
                            fetch_election_result_restricted,
                            fetch_voters_by_candidate_id, publish_result,
                            count_total_votes_cast, count_total_possible_votes,
                            fetch_all_positions)
from .ethereum import Blockchain
from .role import ElectionStatus
from .validator import (convert_to_unix_timestamp, count_max_vote_owner_id,
                        count_total_vote_cast, is_admin, sha256_hash,
                        validate_result_hash)

admin = Blueprint('admin', __name__)


@admin.route('/admin_panel')
@login_required
def admin_panel():
    'Shows the admin panel'

    # Access deny for other
    if not is_admin(current_user):
        return redirect(url_for('auth.index'))

    # Fetch all information
    election = fetch_election()
    voters = fetch_all_voters()
    candidates = fetch_election_result_restricted()
    total_votes_possible = count_total_possible_votes()
    total_votes_cast = count_total_votes_cast()
    positions_count = len(fetch_all_positions())

    # How many voted
    # total_vote_cast = count_total_vote_cast(voters)
    # Max vote and IDs
    total_vote_count, max_vote_owner_id = count_max_vote_owner_id(candidates)

    return render_template(
        'admin_panel.html',
        election_status=election.status,
        candidates=candidates,
        max_vote_owner_id=max_vote_owner_id,
        voters=voters,
        total_voter=len(voters),
        total_vote_count=total_vote_count,
        total_votes_possible=total_votes_possible,
        positions_count=positions_count,
        total_votes_cast=total_votes_cast,
        count_votes_by_voter=count_votes_by_voter,
        # total_vote_cast=total_vote_cast
    )


# @admin.route('/publish')
# @login_required
# def publish():
#     'Publish / Rollback election result'

#     # Access deny for other
#     if not is_admin(current_user):
#         return redirect(url_for('auth.index'))

#     blockchain = Blockchain(
#         fetch_admin_wallet_address(),
#         fetch_contract_address()
#     )

#     candidates = fetch_election_result()
#     for candidate in candidates:
#         voters = fetch_voters_by_candidate_id(candidate.id)
#         # print(voters)

#         # Checking vote counts
#         if candidate.vote_count != len(voters):
#             flash(f'Results tampered for {candidate.name}')
#             return render_template('error.html', error_msg='Vote count mismatch')

#         # Get the hash from the blokchain
#         voteHash_from_blockchain = blockchain.get_hash_by_candidate_hash(
#             sha256_hash(candidate.username)
#         )

#         # Validate the computed hash and bash from blockchain
#         if not validate_result_hash(voters, voteHash_from_blockchain):
#             flash(f'Results tampered for {candidate.name}')
#             return render_template('error.html', error_msg='Voting hash mismatch')

#     election = publish_result()

#     # Notify current status
#     if election.status == ElectionStatus.PUBLIC:
#         flash('Election result is now public')
#     else:
#         flash('Election result is now private')

#     return redirect(url_for('admin.admin_panel'))

@admin.route('/publish')
@login_required
def publish_results():
    if not is_admin(current_user):
        return redirect(url_for('auth.index'))

    try:
        blockchain = Blockchain(
            fetch_admin_wallet_address(),
            fetch_contract_address()
        )
        _, msg = blockchain.publish()
        flash(f"Results published. Tx: {msg}")
    except Exception as e:
        flash(str(e), 'error')

    return redirect(url_for('admin.admin_panel'))

@admin.route('/block_candidate/<int:candidate_id>')
@login_required
def block_candidate(candidate_id):
    'Block / Unblock candidate'

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
    'Block / Unblock voter'

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
    'Extend the end time of the election'

    # Access deny for other
    if not is_admin(current_user):
        return redirect(url_for('auth.index'))

    # Get new time and private key input
    start_time = request.form.get('start_time').strip()
    end_time = request.form.get('end_time').strip()
    private_key = request.form.get('private_key').strip()

    blockchain = Blockchain(
        fetch_admin_wallet_address(),
        fetch_contract_address()
    )

    def show_flash_msg(status, tx_msg):
        if status:
            flash(f'[Updated] Tx HASH: {tx_msg}')
        else:
            flash(f'[Failed] Tx HASH: {tx_msg}')

    if not private_key:
        flash('Private key empty')

    elif start_time and end_time:
        # Sending transaction for setting start and end time of election
        status, tx_msg = blockchain.set_voting_time(
            private_key,
            convert_to_unix_timestamp(start_time),
            convert_to_unix_timestamp(end_time)
        )
        show_flash_msg(status, tx_msg)

    elif end_time:
        # Sending transaction for extending the time
        status, tx_msg = blockchain.extend_time(
            private_key,
            convert_to_unix_timestamp(end_time)
        )
        show_flash_msg(status, tx_msg)

    return redirect(url_for('admin.admin_panel'))
