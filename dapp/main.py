from flask import Blueprint, flash, redirect, render_template, request, url_for, session, jsonify
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
from .ethereum import Blockchain, get_voting_time
from .role import ElectionStatus
from .validator import (
    build_vote_cast_hash,
    count_max_vote_owner_id,
    is_admin,
    sha256_hash,
)
from .cryptography import encrypt_object, decrypt_object
from datetime import datetime, timezone


main = Blueprint("main", __name__)

@main.route("/home")
@login_required
def home():
    # Use module-level get_voting_time() to fetch UNIX timestamps
    start_time_iso = None
    try:
        res = get_voting_time()
        if (
            isinstance(res, tuple)
            and len(res) == 2
            and isinstance(res[0], int)
        ):
            start_unix, _end_unix = res
            start_time_iso = datetime.fromtimestamp(start_unix, tz=timezone.utc).isoformat()
    except Exception:
        start_time_iso = None

    return render_template("home.html", start_time=start_time_iso)


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
            # Ensure status is a strict boolean; treat non-boolean (e.g., error tuple) as False
            if isinstance(status, bool):
                has_voted_for_position[position.id] = status
            else:
                has_voted_for_position[position.id] = False
        except Exception as e:
            flash(
                f"Error checking vote status for position {position.position}: {str(e)}"
            )
            has_voted_for_position[position.id] = False

    return render_template(
        "election.html",
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
    - Handles potential database errors gracefully
    """
    try:
        # Fetch all published results from database
        results = fetch_all_results()
        
        # Add helper data for template rendering
        for r in results:
            if hasattr(r, 'vote_count') and hasattr(r, 'position'):
                # Mark winner for positions
                r.is_winner = False
                if r.vote_count > 0:
                    # Find max votes for this position
                    position_results = [x for x in results if x.position == r.position]
                    max_votes = max(x.vote_count for x in position_results)
                    if r.vote_count == max_votes:
                        r.is_winner = True

        return render_template("liveresult.html", results=results)
    except Exception as e:
        flash(f"Error fetching election results: {str(e)}", "error")
        return render_template("liveresult.html", results=[])


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


@main.route("/vote")
@login_required
def vote():
    """
    Renders voting page with all positions and their blockchain-registered candidates.
    Only one candidate can be voted per position; disables UI if user already voted.
    """
    if is_admin(current_user):
        return redirect(url_for("auth.index"))

    blockchain = Blockchain(current_user.wallet_address, fetch_contract_address())

    positions = fetch_all_positions()
    positions_data = []
    has_voted_for_position = {}

    for position in positions:
        # Check vote status on-chain
        try:
            status = blockchain.has_user_voted(
                position.id, Web3.to_bytes(hexstr=current_user.username_hash)
            )
            has_voted_for_position[position.id] = bool(status) if isinstance(status, bool) else False
        except Exception:
            has_voted_for_position[position.id] = False

        # Pull candidate hashes from chain and map to DB records
        candidate_objs = []
        try:
            candidate_hashes = blockchain.get_candidates(position.id)
            for _hash in candidate_hashes:
                candidate = fetch_candidate_by_hash(_hash)
                if candidate:
                    candidate_objs.append(candidate)
        except Exception:
            candidate_objs = []

        positions_data.append(
            {
                "id": position.id,
                "name": position.position,
                "candidates": candidate_objs,
                "has_voted": has_voted_for_position[position.id],
            }
        )

    return render_template(
        "voting.html",
        positions_data=positions_data,
        user=current_user,
    )


@main.route("/submit_votes", methods=["POST"])
@login_required
def submit_votes():
    """
    Accepts a JSON payload with an array of { position_id, candidate_id } and
    casts votes sequentially. Stops on first failure and reports status.
    """
    if is_admin(current_user):
        return jsonify({"success": False, "message": "Admins cannot vote"}), 403

    try:
        data = request.get_json(force=True)
        votes = data.get("votes", [])
        if not isinstance(votes, list) or not votes:
            return jsonify({"success": False, "message": "No votes provided"}), 400
    except Exception:
        return jsonify({"success": False, "message": "Invalid payload"}), 400

    # Prepare for on-chain voting
    blockchain = Blockchain(current_user.wallet_address, fetch_contract_address())
    private_key = decrypt_object(current_user.private_key_encrypted)

    for item in votes:
        try:
            position_id = int(item.get("position_id"))
            candidate_id = int(item.get("candidate_id"))
        except Exception:
            return jsonify({"success": False, "message": "Invalid vote entry"}), 400

        # Resolve candidate_hash from DB
        candidate = fetch_candidate_by_id(candidate_id)
        if not candidate:
            return jsonify({"success": False, "message": f"Candidate {candidate_id} not found"}), 404

        # Check if already voted for position
        try:
            has_voted = blockchain.has_user_voted(
                position_id, Web3.to_bytes(hexstr=current_user.username_hash)
            )
            if isinstance(has_voted, bool) and has_voted:
                continue  # skip silently; alternatively, fail fast
        except Exception:
            pass

        # Cast vote
        ok, msg = blockchain.vote(
            private_key,
            position_id,
            current_user.username_hash,
            candidate.candidate_hash,
        )
        if not ok:
            return jsonify({"success": False, "message": msg}), 500

    return jsonify({"success": True})


@main.route("/submit_vote", methods=["POST"])
@login_required
def submit_vote():
    """
    Submits a single vote { position_id, candidate_id } and returns JSON status.
    Intended for step-by-step UI feedback on the client side.
    """
    if is_admin(current_user):
        return jsonify({"success": False, "message": "Admins cannot vote"}), 403

    try:
        data = request.get_json(force=True)
        position_id = int(data.get("position_id"))
        candidate_id = int(data.get("candidate_id"))
    except Exception:
        return jsonify({"success": False, "message": "Invalid payload"}), 400

    # Resolve candidate
    candidate = fetch_candidate_by_id(candidate_id)
    if not candidate:
        return jsonify({"success": False, "message": "Candidate not found"}), 404

    blockchain = Blockchain(current_user.wallet_address, fetch_contract_address())

    # Avoid duplicate votes per position
    try:
        hv = blockchain.has_user_voted(position_id, Web3.to_bytes(hexstr=current_user.username_hash))
        if isinstance(hv, bool) and hv:
            return jsonify({"success": True, "message": "Already voted"})
    except Exception:
        pass

    private_key = decrypt_object(current_user.private_key_encrypted)
    ok, msg = blockchain.vote(
        private_key,
        position_id,
        current_user.username_hash,
        candidate.candidate_hash,
    )
    return jsonify({"success": bool(ok), "message": msg})
