from flask import Blueprint, flash, redirect, render_template, request, url_for, session
from flask_login import current_user, login_required
from web3 import Web3

from .db_operations import (
    add_new_vote_record,
    fetch_all_active_candidates,
    fetch_candidate_by_id,
    fetch_candidate_by_id_restricted,
    fetch_contract_address,
    fetch_election,
    fetch_election_result,
    fetch_voter_by_id,
    fetch_voters_by_candidate_id,
    fetch_admin_wallet_address,
    fetch_all_positions,
    fetch_position_by_id,
    fetch_candidate_by_position_id,
    has_voted_for_position,
    fetch_candidate_by_hash,
    fetch_all_results,
    fetch_vote_by_candidate_id,
    fetch_votes_by_candidate_hash,
)
from .ethereum import Blockchain
from .role import ElectionStatus
from .validator import (
    build_vote_cast_hash,
    count_max_vote_owner_id,
    is_admin,
    sha256_hash,
)
from .cryptography import encrypt_object, decrypt_object
from datetime import datetime


main = Blueprint("main", __name__)


@main.route("/positions")
@login_required
def positions():
    """
    Displays all contested positions for the current voter.

    - Redirects admin users to the index page.
    - Fetches all positions and checks if the current user has voted for each.
    - Renders the positions page with voting status for each position.
    """

    # Access deny for ADMIN
    if is_admin(current_user):
        return redirect(url_for("auth.index"))

    # Creates blockchain object using user's wallet address
    blockchain = Blockchain(current_user.wallet_address, fetch_contract_address())

    # Fetches all contested positions
    positions = fetch_all_positions()

    # Dict to keep track of each postion and if user has voted in them
    has_voted_for_position = {}

    for position in positions:
        try:
            # Check if user has voted for this position
            status = blockchain.has_user_voted(
                position.id, Web3.to_bytes(hexstr=current_user.username_hash)
            )
            has_voted_for_position[position.id] = status
        except Exception as e:
            flash(
                f"Error checking vote status for position {position.position}: {str(e)}"
            )
            has_voted_for_position[position.id] = False

    return render_template(
        "positions.html",
        user=current_user,
        positions=positions,
        has_voted_for_position=has_voted_for_position,
    )


@main.route("/positions/<int:position_id>")
@login_required
def position(position_id):
    """
    Displays details and candidates for a specific position.

    - Redirects admin users to the index page.
    - Checks if the current user has already voted for this position.
    - If not, fetches the position and its candidates and renders the position details page.

    Args:
        position_id (int): The ID of the position to display.
    """

    # Access deny for ADMIN
    if is_admin(current_user):
        return redirect(url_for("auth.index"))

    # Create blockchain object using user's wallet address
    blockchain = Blockchain(current_user.wallet_address, fetch_contract_address())

    status = blockchain.has_user_voted(
        position_id, Web3.to_bytes(hexstr=current_user.username_hash)
    )
    if status:  # Deny access if user has voted for this position
        flash("You have already voted for this position")
        return redirect(url_for("main.positions"))

    # Fetch all candidates contesting for this postion
    position = fetch_position_by_id(position_id)
    candidates = {}
    candidate_hashes = blockchain.get_candidates(position_id)
    # print(f"Candidate hashes for position {position_id}: {candidate_hashes}")
    for _hash in candidate_hashes:
        candidates[_hash] = fetch_candidate_by_hash(_hash)
    # print(f"candidates: {candidates}")

    # If position or candidates fetch failed
    if not position or not candidates:
        flash("Position or candidates not found")
        return redirect(url_for("main.positions"))

    return render_template(
        "candidates.html", user=current_user, position=position, candidates=candidates
    )


@main.route("/cast_vote/<int:candidate_id>")
@login_required
def cast_vote(candidate_id):
    """
    Handles the vote casting process for a selected candidate.

    - Redirects admin users to the index page.
    - Decrypts the voter's private key.
    - Sends a vote transaction to the blockchain for the selected candidate.

    Args:
        candidate_id (int): The ID of the candidate to vote for.
    """

    # Access deny for ADMIN
    if is_admin(current_user):
        return redirect(url_for("auth.index"))

    # selected_candidate = fetch_candidate_by_id_restricted(candidate_id)
    private_key = decrypt_object(current_user.private_key_encrypted)

    # Get candidate and voter
    selected_candidate = fetch_candidate_by_id(candidate_id)

    # Sending transaction for vote cast
    blockchain = Blockchain(current_user.wallet_address, fetch_contract_address())
    status, tx_msg = blockchain.vote(
        private_key,
        selected_candidate.position_id,
        current_user.username_hash,
        selected_candidate.candidate_hash,
    )
    print(status, tx_msg)

    if status:
        flash(f"Vote successful: {tx_msg}")
        print(
            f"""
        voter hash: {current_user.username_hash}
        candidate hash: {selected_candidate.candidate_hash}
        private_key: {private_key}
        """
        )

        return redirect(url_for("main.positions"))
    else:
        flash(f"Vote failed: {tx_msg}")
        return redirect(url_for("main.cast_vote", candidate_id=candidate_id))


@main.route("/result")
def result():
    """
    Displays the published election results.

    - Fetches all results and renders the results page.
    """

    # Fetches admin published results
    results = fetch_all_results()
    return render_template("result.html", results=results)


@main.route("/results/<candidate_hash>")
def result_by_candidate(candidate_hash):
    """
    Displays the votes for a specific candidate by their hash.

    - Fetches all votes and candidate details for the given candidate hash.
    - Renders the votes by candidate page.

    Args:
        candidate_hash (str): The hash of the candidate.
    """

    # Fetches all votes cast for a candidate
    votes = fetch_votes_by_candidate_hash(candidate_hash)
    candidate = fetch_candidate_by_hash(candidate_hash)
    return render_template(
        "votes_by_candidate.html",
        votes=votes,
        candidate=candidate,
        ts_to_dt=datetime.utcfromtimestamp,
    )
