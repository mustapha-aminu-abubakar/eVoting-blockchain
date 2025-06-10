from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from web3 import Web3

from .db_operations import (add_new_vote_record, fetch_all_active_candidates,
                            fetch_candidate_by_id,
                            fetch_candidate_by_id_restricted,
                            fetch_contract_address, fetch_election,
                            fetch_election_result, fetch_voter_by_id,
                            fetch_voters_by_candidate_id,
                            fetch_all_positions,
                            fetch_position_by_id,
                            fetch_candidate_by_position_id,
                            has_voted_for_position)
from .ethereum import Blockchain
from .role import ElectionStatus
from .validator import build_vote_cast_hash, count_max_vote_owner_id, is_admin, sha256_hash
from .cryptography import encrypt_object, decrypt_object


main = Blueprint('main', __name__)


# @main.route('/candidates')
# @login_required
# def candidates():
#     'Shows the active candidate list and voter details'

#     # Access deny for ADMIN
#     if is_admin(current_user):
#         return redirect(url_for('auth.index'))

#     candidates = fetch_all_active_candidates()

#     return render_template(
#         'candidates.html',
#         user=current_user,
#         candidates=candidates
#     )

# def position_status(position_id):
#     'Check if the user has voted for the position'
    
#     # Access deny for ADMIN
#     if is_admin(current_user):
#         return redirect(url_for('auth.index'))

#     return has_voted_for_position(current_user.id, position_id)

@main.route('/positions')
@login_required
def positions():
    'Shows the contested positions'
    
    # Access deny for ADMIN
    if is_admin(current_user):
        return redirect(url_for('auth.index'))
    
    positions = fetch_all_positions()
    return render_template(
        'positions.html',
        user=current_user,
        positions=positions,
        has_voted_for_position=has_voted_for_position
    )
    
    
@main.route('/positions/<int:position_id>')
@login_required
def position(position_id):
    'Shows the contested position details'

    # Access deny for ADMIN
    if is_admin(current_user):
        return redirect(url_for('auth.index'))

    position = fetch_position_by_id(position_id)
    candidates = fetch_candidate_by_position_id(position_id)
    
    has_voted_for_position_id = request.args.get('has_voted_for_position_id', default=False, type=lambda v: v.lower() == 'true')

    
    if not position or not candidates:
        flash('Position or candidates not found')
        return redirect(url_for('main.positions'))
    
    return render_template(
        'candidates.html',
        user=current_user,
        position=position,
        has_voted_for_position_id=has_voted_for_position_id,
        candidates=candidates
    )
    
    
    
@main.route('/cast_vote/<int:candidate_id>')
@login_required
def cast_vote(candidate_id):
    'When any vote button clicked'

    # Access deny for ADMIN
    if is_admin(current_user):
        return redirect(url_for('auth.index'))

    # selected_candidate = fetch_candidate_by_id_restricted(candidate_id)
    private_key = decrypt_object(current_user.private_key_encrypted)

    # Get candidate and voter
    selected_candidate = fetch_candidate_by_id(candidate_id)
    voter = fetch_voter_by_id(current_user.id)
    vote_hash = Web3.keccak(text=f'{voter.id}-{selected_candidate.id}').hex()
    
    # Check if user has already voted a candidate for this position
    status, msg = add_new_vote_record(voter, selected_candidate, vote_hash)
    if not status:
        flash(msg)
        return redirect(url_for('main.positions'))

    # Generate hash
    # candidate_hash, vote_hash = build_vote_cast_hash(
    #     selected_candidate,
    #     voter,
    #     fetch_voters_by_candidate_id(selected_candidate.id)
    # )

    print(f'''
        voter: {voter}
        candidate hash: {selected_candidate.candidate_hash}
        vote_hash: {vote_hash}
        private_key: {private_key}
    ''')

    # Sending transaction for vote cast
    blockchain = Blockchain(voter.wallet_address, fetch_contract_address())
    status, tx_msg = blockchain.vote(
        private_key, 
        selected_candidate.position_id, 
        voter.username_hash, 
        selected_candidate.candidate_hash
        )

    if status:
        flash(f'Transaction confirmed: {tx_msg}')
        add_new_vote_record(voter, selected_candidate, vote_hash)
    else:
        flash(f'Transaction failed: {tx_msg}')


    # return render_template(
    #     'candidates_confirm.html',
    #     selected_candidate=selected_candidate,
    #     private_key=private_key
    # )
    return redirect(url_for('main.positions'))



# @main.route('/cast_vote/<int:candidate_id>/confirm', methods=['POST'])
# @login_required
# def cast_vote_confirm(candidate_id):
#     '''
#     Confirm the vote
#     Take the private key of the voter to sign to transaction
#     '''

#     # Access deny for ADMIN
#     if is_admin(current_user):
#         return redirect(url_for('auth.index'))

#     # Voter private key
#     private_key = request.form.get('private_key').strip()

#     # Get candidate and voter
#     selected_candidate = fetch_candidate_by_id(candidate_id)
#     voter = fetch_voter_by_id(current_user.id)

#     # Generate hash
#     candidate_hash, vote_hash = build_vote_cast_hash(
#         selected_candidate,
#         voter,
#         fetch_voters_by_candidate_id(selected_candidate.id)
#     )

#     print(f'''
#         candidate hash: {candidate_hash}
#         vote_hash: {vote_hash}
#     ''')

#     # Sending transaction for vote cast
#     blockchain = Blockchain(voter.wallet_address, fetch_contract_address())
#     status, tx_msg = blockchain.vote(private_key, candidate_hash, vote_hash)

#     if status:
#         flash(f'Transaction confirmed: {tx_msg}')
#         add_new_vote_record(voter, selected_candidate)
#     else:
#         flash(f'Transaction failed: {tx_msg}')

#     return redirect(url_for('main.candidates'))


@main.route('/result')
def result():
    'Show the election result if published'

    # If not public
    election = fetch_election()
    if election.status == ElectionStatus.PRIVATE:
        flash('The result has not been released yet')
        return redirect(url_for('auth.index'))

    # Find the max vote count and IDs of the winners
    candidates = fetch_election_result()
    _, max_vote_owner_id = count_max_vote_owner_id(candidates)

    return render_template(
        'result.html',
        candidates=candidates,
        max_vote_owner_id=max_vote_owner_id
    )
