import hashlib
import random
import string
import time
from datetime import datetime

from .role import UserRole


def is_admin(user):
    """
    Checks if the given user is an admin.

    Args:
        user: The user object to check.

    Returns:
        bool: True if the user is an admin, False otherwise.
    """
    if user.id == UserRole.ADMIN_ID:
        return True
    return False


def validate_signin(username, password):
    """
    Validates the username and password for sign-in.

    Args:
        username (str): The username to validate.
        password (str): The password to validate.

    Returns:
        tuple: (bool, str) indicating validity and an error message if invalid.
    """
    if len(username) < 3:
        return (False, "Invalid username")

    if not password:
        return (False, "Invalid password")

    return (True, "")


def validate_signup(username, password, confirm_password):
    """
    Validates the signup form data.

    Args:
        username (str): The username to validate.
        password (str): The password to validate.
        confirm_password (str): The confirmation password.

    Returns:
        tuple: (bool, str) indicating validity and an error message if invalid.
    """
    if len(username) < 3:
        return (False, "Invalid username")
    if not password:
        return (False, "Invalid password")
    if confirm_password != password:
        return (False, "Confirm password does not match")

    return (True, "")


def generate_opt(length):
    """
    Generates a numeric OTP (One-Time Password) of the specified length.

    Args:
        length (int): The length of the OTP.

    Returns:
        str: The generated OTP.
    """
    otp = ""
    for _ in range(length):
        otp += random.choice(string.digits)
    return otp


def sha256_hash(username):
    """
    Computes the SHA-256 hash of the given username.

    Args:
        username (str): The username to hash.

    Returns:
        str: The hexadecimal SHA-256 hash.
    """
    return hashlib.sha256(bytes(username, "UTF-8")).hexdigest()


def count_total_vote_cast(voters):
    """
    Counts the total number of voters who have cast their vote.

    Args:
        voters (list): List of voter objects.

    Returns:
        int: The total number of votes cast.
    """
    total_vote_cast = 0
    for voter in voters:
        if voter.vote_status:
            total_vote_cast += 1
    return total_vote_cast


def validate_result_hash(voters, hash_from_blockchain):
    """
    Validates the result hash by comparing the computed hash with the blockchain hash.

    Args:
        voters (list): List of voter objects.
        hash_from_blockchain (str): The hash value from the blockchain.

    Returns:
        bool: True if the hashes match, False otherwise.
    """
    if not voters:
        blank_hash = "0000000000000000000000000000000000000000000000000000000000000000"
        return hash_from_blockchain == blank_hash

    hash_concat = ""
    vote_cast_nonce = 0
    for voter in voters:
        hash_concat += voter.username_hash
        vote_cast_nonce += voter.id

    result_hash = sha256_hash(hash_concat + str(vote_cast_nonce))
    print(f"   result_hash: {result_hash} ")
    print(f"   blockchain_hash: {hash_from_blockchain} ")
    return result_hash == hash_from_blockchain


def build_vote_cast_hash(
    selected_candidate, current_voter, voters_by_selected_candidate
):
    """
    Builds the vote cast hash for a candidate and voter.

    Args:
        selected_candidate: The candidate object.
        current_voter: The current voter object.
        voters_by_selected_candidate (list): List of voters who voted for the candidate.

    Returns:
        tuple: (str, str) The candidate hash and the vote cast hash.
    """

    # If first voter
    if not voters_by_selected_candidate:
        return (
            sha256_hash(selected_candidate.name + str(selected_candidate.id)),
            sha256_hash(current_voter.username_hash + str(current_voter.id)),
        )

    hash_concat = ""
    vote_cast_nonce = 0

    flag = True
    for voter in voters_by_selected_candidate:
        if flag and current_voter.id < voter.id:
            print(current_voter)
            flag = False
            hash_concat += current_voter.username_hash
            vote_cast_nonce += current_voter.id
        print(voter)
        hash_concat += voter.username_hash
        vote_cast_nonce += voter.id

    if flag:
        hash_concat += current_voter.username_hash
        vote_cast_nonce += current_voter.id

    return (
        sha256_hash(selected_candidate.name),
        sha256_hash(hash_concat + str(vote_cast_nonce)),
    )


def count_max_vote_owner_id(candidates):
    """
    Counts the total votes and finds the candidate IDs with the maximum votes.

    Args:
        candidates (list): List of candidate objects.

    Returns:
        tuple: (int, list) Total vote count and list of candidate IDs with max votes.
    """
    max_vote_owner_id = []
    total_vote_count = 0
    if candidates:
        max_vote = candidates[0].vote_count

        for candidate in candidates:
            total_vote_count += candidate.vote_count
            if candidate.vote_count == max_vote:
                max_vote_owner_id.append(candidate.id)

    return (total_vote_count, max_vote_owner_id)


def convert_to_unix_timestamp(timestamp_value):
    """
    Converts a timestamp string to a Unix timestamp.

    Args:
        timestamp_value (str): The timestamp string in '%Y-%m-%dT%H:%M' format.

    Returns:
        int: The Unix timestamp.
    """
    timestamp_value_obj = datetime.strptime(timestamp_value, "%Y-%m-%dT%H:%M")
    return int(time.mktime(timestamp_value_obj.timetuple()))
