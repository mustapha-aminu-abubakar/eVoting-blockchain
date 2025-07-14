import json
import sys
import os
from datetime import datetime, timezone
from tzlocal import get_localzone
import pytz

from web3 import Web3
from dotenv import load_dotenv
from collections import defaultdict
from .credentials import WEB3_PROVIDER_URL
from .db_operations import (
    get_offchain_results,
    add_txn,
    update_voter_wallet_by_username,
    fetch_admin_wallet_address,
    fetch_contract_address,
)
from .cryptography import encrypt_object
from .models import Candidate, Position
from eth_account import Account


load_dotenv()
ADMIN_PRIVATE_KEY = os.getenv("ADMIN_PRIVATE_KEY")


class Blockchain:
    """
    A class to interact with the Ethereum blockchain for the eVoting system.
    Provides methods for voting, candidate registration, time management, and result publishing.
    """

    _ABI_DIR = f"{os.getcwd()}/contract/ABI.json"
    sepolia = 11155111

    def __init__(self, wallet_address, contract_address):
        """
        Initializes the Blockchain object with wallet and contract addresses.
        Sets up the Web3 provider and contract instance.

        Args:
            wallet_address (str): The wallet address to use for transactions.
            contract_address (str): The deployed contract address.
        """
        self._read_ABI()
        self._wallet_address = wallet_address
        self._contract_address = contract_address

        self.w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))
        self.w3.eth.default_account = self._wallet_address

        self._contract_instance = self.w3.eth.contract(
            abi=self._ABI, address=self._contract_address
        )
        print(self.w3.is_connected())
        print(self.w3.eth.chain_id)  # Should match Sepolia's ID (11155111)


    def _read_ABI(self):
        """
        Reads the contract ABI from the ABI.json file and loads it for contract interaction.
        """
        with open(self._ABI_DIR) as ABI_file:
            self._ABI = json.loads(ABI_file.read())

    def _get_nonce(self):
        """
        Retrieves the current transaction count (nonce) for the wallet address.

        Returns:
            int: The current nonce.
        """
        return self.w3.eth.get_transaction_count(self._wallet_address, "pending")

    def local_to_utc_timestamp(self, _timestamp: str) -> int:
        """
        Converts a local time string to a UTC timestamp.

        Args:
            _timestamp (str): Local time in '%Y-%m-%dT%H:%M' format.

        Returns:
            int: UTC timestamp.
        """
        local_naive_dt = datetime.strptime(_timestamp, "%Y-%m-%dT%H:%M")
        local_tz = get_localzone()  # Get local timezone
        local_dt = local_tz.localize(local_naive_dt)  # Localize the naive datetime
        utc_dt = local_dt.astimezone(pytz.utc)  # Convert to UTC
        # Return UTC timestamp
        return int(utc_dt.timestamp())

    def to_utc_timestamp(self, dt_str, tz_name):
        """
        Converts a datetime string and timezone name to a UTC timestamp.

        Args:
            dt_str (str): Datetime string in '%Y-%m-%dT%H:%M' format.
            tz_name (str): Timezone name.

        Returns:
            int: UTC timestamp.
        """
        naive = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M")
        local = pytz.timezone(tz_name).localize(naive)
        return int(local.astimezone(pytz.utc).timestamp())

    def set_voting_time(
        self, start_unix_time, end_unix_time, tz, private_key=ADMIN_PRIVATE_KEY
    ):
        """
        Sets the voting start and end times on the blockchain.

        Args:
            start_unix_time (str): Start time as a string.
            end_unix_time (str): End time as a string.
            tz (str): Timezone name.
            private_key (str): Admin's private key for signing the transaction.

        Returns:
            tuple: (bool, str) indicating success and transaction hash or error.
        """
        print("[set_voting_time] Building transaction...")

        start_ts_utc = self.to_utc_timestamp(start_unix_time, tz)
        end_ts_utc = self.to_utc_timestamp(end_unix_time, tz)

        try:
            tx = self._contract_instance.functions.setVotingTime(
                start_ts_utc, end_ts_utc
            ).build_transaction(
                {
                    "chainId": self.sepolia,
                    "from": self._wallet_address,
                    "nonce": self._get_nonce(),
                    "gas": 100000,
                    "maxFeePerGas": int(self.w3.eth.gas_price * 1.2),
                    "maxPriorityFeePerGas": self.w3.eth.gas_price // 2,
                    "type": 2,  # EIP-1559 transaction type
                }
            )
            print(f"start time {start_ts_utc}, end time {end_ts_utc} ")
            tx_receipt = self._send_tx('Start election', tx, private_key)
            return (bool(tx_receipt["status"]), tx_receipt["transactionHash"].hex())
        except Exception as e:
            return (False, str(e))

    def extend_time(self, new_end_time, private_key=ADMIN_PRIVATE_KEY):
        """
        Extends the voting end time on the blockchain.

        Args:
            new_end_time (int): New end time as a UTC timestamp.
            private_key (str): Admin's private key.

        Returns:
            tuple: (bool, str) indicating success and transaction hash or error.
        """
        print("[extend_time] Building transaction...")
        try:
            tx = self._contract_instance.functions.extendVotingTime(
                new_end_time
            ).build_transaction(
                {
                    "chainId": self.sepolia,
                    "from": self._wallet_address,
                    "nonce": self._get_nonce(),
                    "gas": 100000,
                    "maxFeePerGas": int(self.w3.eth.gas_price * 1.2),
                    "maxPriorityFeePerGas": self.w3.eth.gas_price // 2,
                    "type": 2,  # EIP-1559 transaction type
                }
            )
            tx_receipt = self._send_tx('Extend election', tx, private_key)
            return (bool(tx_receipt["status"]), tx_receipt["transactionHash"].hex())
        except Exception as e:
            return (False, str(e))

    # def get_voting_time(self):
    #     """
    #     Retrieves the voting start and end times from the blockchain.

    #     Returns:
    #         dict: Contains start and end times in both unix and readable formats, or error.
    #     """
    #     try:
    #         start_unix, end_unix = (
    #             self._contract_instance.functions.getVotingTime().call()
    #         )

    #         # Convert to readable datetime in UTC
    #         start_time = datetime.utcfromtimestamp(
    #             start_unix, tz=timezone.utc
    #         ).strftime("%Y-%m-%d %H:%M:%S UTC")
    #         end_time = datetime.utcfromtimestamp(end_unix, tz=timezone.utc).strftime(
    #             "%Y-%m-%d %H:%M:%S UTC"
    #         )

    #         return {
    #             "start_unix": start_unix,
    #             "end_unix": end_unix,
    #             "start_time": start_time,
    #             "end_time": end_time,
    #         }

    #     except Exception as e:
    #         return {"error": str(e)}

    def vote(self, private_key, position_id, voter_hash, candidate_hash):
        """
        Casts a vote for a candidate in a given position.

        Args:
            private_key (str): Voter's private key.
            position_id (int): Position ID.
            voter_hash (str): Voter's hash.
            candidate_hash (str): Candidate's hash.

        Returns:
            tuple: (bool, str) indicating success and transaction hash or error.
        """
        print(
            f""" 
              [vote] Building transaction...
              Voter Hash: {voter_hash}
              Candidate Hash: {candidate_hash}
              Position ID: {position_id}
              """
        )
        try:
            tx = self._contract_instance.functions.vote(
                int(position_id),
                Web3.to_bytes(hexstr=voter_hash),
                Web3.to_bytes(hexstr=candidate_hash),
            ).build_transaction(
                {
                    "chainId": self.sepolia,
                    "from": self._wallet_address,
                    "nonce": self._get_nonce(),
                    "gas": 100000,
                    "maxFeePerGas": int(self.w3.eth.gas_price * 1.2),
                    "maxPriorityFeePerGas": self.w3.eth.gas_price // 2,
                    "type": 2,  # EIP-1559 transaction type
                }
            )
            tx_receipt = self._send_tx('Cast vote', tx, private_key)
            return (bool(tx_receipt["status"]), tx_receipt["transactionHash"].hex())
        except Exception as e:
            return (False, str(e))

    def register_candidate(self, private_key, position_id, candidate_hash):
        """
        Registers a candidate for a position on the blockchain (admin only).

        Args:
            private_key (str): Admin's private key.
            position_id (int): Position ID.
            candidate_hash (str): Candidate's hash.

        Returns:
            tuple: (bool, str) indicating success and transaction hash or error.
        """
        print("[register_candidate] Building transaction...")
        try:
            tx = self._contract_instance.functions.registerCandidate(
                int(position_id), candidate_hash
            ).build_transaction(
                {
                    "chainId": self.sepolia,
                    "from": self._wallet_address,
                    "nonce": self._get_nonce(),
                    "gas": 100000,
                    "maxFeePerGas": int(self.w3.eth.gas_price * 1.2),
                    "maxPriorityFeePerGas": self.w3.eth.gas_price // 2,
                    "type": 2,  # EIP-1559 transaction type
                }
            )
            tx_receipt = self._send_tx('Register candidate', tx, private_key)
            return (bool(tx_receipt["status"]), tx_receipt["transactionHash"].hex())
        except Exception as e:
            return (False, str(e))

    def get_candidates(self, position_id):
        """
        Retrieves all candidate hashes for a given position from the blockchain.

        Args:
            position_id (int): Position ID.

        Returns:
            list[str]: List of candidate hashes as hex strings, or error message.
        """
        try:
            return [
                candidate.hex()
                for candidate in self._contract_instance.functions.getCandidates(
                    position_id
                ).call()
            ]
        except Exception as e:
            return f"Error fetching candidates: {str(e)}"

    def print_current_block_timestamp(self):
        """
        Prints the current block timestamp from the contract in UTC.
        """
        timestamp = self._contract_instance.functions.getCurrentTimestamp().call()
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        print(f"Current contract block.timestamp: {timestamp} ({dt.isoformat()})")

    def _send_tx(self, tx_type, tx, private_key):
        """
        Signs and sends a transaction to the blockchain, waits for receipt, and logs it.

        Args:
            tx (dict): The transaction dictionary.
            private_key (str): The private key to sign the transaction.

        Returns:
            dict: The transaction receipt.
        """
        sys.stdout.write(f' \r Signing Tx ...{private_key} ')
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=private_key)
        sys.stdout.write(f' \r Sending Tx ... ')
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        sys.stdout.write(f' \r Waiting for Tx receipt ... ')
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)

        # Log transaction, add to off-chain database
        add_txn(
            tx_type,
            tx_receipt["transactionHash"].hex(),
            bool(tx_receipt["status"]),
            tx_receipt["from"],
            int(tx_receipt["gasUsed"]),
        )
        sys.stdout.write(f' \r Transaction receipt: {tx_receipt.transactionHash.hex()} ')
        sys.stdout.flush()
        return tx_receipt

    def fund_wallet(self, to_address):
        """
        Sends Ether to a specified address to fund a wallet.

        Args:
            to_address (str): The recipient's wallet address.

        Returns:
            tuple: (bool, str) indicating success and transaction hash or error.
        """
        print("[fund_wallet] Buiding transaction ... ")
        try:
            # Use Web3.to_wei for ETH to wei conversion
            estimated_eth = 0.002  # Estimate: registering a candidate costs ~0.002 ETH
            tx = {
                "to": to_address,
                "value": self.w3.to_wei(estimated_eth, "ether") * Candidate.query.count(),  # 0.002 ETH in wei
                "gas": 21000,
                "nonce": self._get_nonce(),
                "chainId": self.sepolia,
                "maxFeePerGas": int(self.w3.eth.gas_price * 1.2),
                "maxPriorityFeePerGas": self.w3.eth.gas_price // 2,
                "type": 2,  # EIP-1559 transaction type
            }
            # print(f"maxFeePerGas: {tx['maxFeePerGas']/1000000}")
            # print(f"maxPriorityFeePerGas: {tx['maxPriorityFeePerGas']/1000000}")

            tx_receipt = self._send_tx('Fund user wallet', tx, ADMIN_PRIVATE_KEY)
            return (bool(tx_receipt["status"]), tx_receipt["transactionHash"].hex())
        except Exception as e:
            return (False, str(e))

    def get_onchain_results(self):
        """
        Retrieves the vote counts for all candidates from the blockchain.

        Returns:
            dict: Mapping of candidate IDs to their result data.
        """
        results = {}
        for candidate in Candidate.query.all():
            count = self._contract_instance.functions.getVoteCounts(
                candidate.position_id, Web3.to_bytes(hexstr=candidate.candidate_hash)
            ).call()
            results[candidate.id] = candidate.as_dict()
            results[candidate.id]["vote_count"] = count
            results[candidate.id]["position"] = candidate.position.position
        # print(f'On-chain results: {results} \n\n')
        return results

    def group_candidates_by_position(self):
        """
        Groups candidates by position and marks the winner(s) for each position.

        Returns:
            dict: Mapping of position names to lists of candidate result data.
        """
        grouped = defaultdict(list)
        results = self.get_onchain_results()

        for candidate in results.values():
            grouped[candidate["position"]].append(candidate)

        # Mark winners
        for position, candidates in grouped.items():
            max_votes = max(c["vote_count"] for c in candidates)
            for c in candidates:
                c["is_winner"] = c["vote_count"] == max_votes
        # print(f"Grouped candidates by position: {grouped}")
        print(f"Grouped results {dict(grouped)}")
        return dict(grouped)

    def get_all_votes(self):
        """
        Retrieves all votes from the blockchain.

        Returns:
            list or str: List of all votes or error message.
        """
        try:
            all_votes = self._contract_instance.functions.getAllVotes().call()
            print(f"All votes fetched: {all_votes}")
            return all_votes
        except Exception as e:
            return f"Error fetching all votes: {str(e)}"

    def publish(self):
        """
        Publishes the election results on the blockchain.

        Returns:
            tuple: (bool, str) indicating success and transaction hash or error.
        """
        print("[publish] Building transaction ...")
        try:
            # If matched, finalize on-chain
            tx = self._contract_instance.functions.publishResults().build_transaction(
                {
                    "from": self.w3.eth.default_account,
                    "nonce": self._get_nonce(),
                    "chainId": self.sepolia,
                    "gas": 100000,
                    "maxFeePerGas": int(self.w3.eth.gas_price * 1.2),
                    "maxPriorityFeePerGas": self.w3.eth.gas_price // 2,
                    "type": 2,  # EIP-1559 transaction type
                }
            )

            tx_receipt = self._send_tx('Publish result', tx, ADMIN_PRIVATE_KEY)
            return (bool(tx_receipt["status"]), tx_receipt["transactionHash"].hex())
        except Exception as e:
            return (False, str(e), None)

    # def get_voting_time(self):
    #     """
    #     Prints the current, start, and end voting times from the contract.

    #     Returns:
    #         tuple: (bool, str) indicating success or error.
    #     """
    #     try:
    #         now = self._contract_instance.functions.getCurrentTimestamp().call()
    #         start = self._contract_instance.functions.startVotingTime().call()
    #         end = self._contract_instance.functions.endVotingTime().call()
    #         print(
    #             f"Current time: {datetime.fromtimestamp(now)}, Start time: {datetime.fromtimestamp(start)}, End time: {(datetime.fromtimestampend)}"
    #         )
    #     except Exception as e:
    #         return (False, str(e))

    def has_user_voted(self, position_id, voter_hash):
        """
        Checks if a user has already voted for a given position.

        Args:
            position_id (int): Position ID.
            voter_hash (bytes): Voter's hash as bytes.

        Returns:
            bool or tuple: True if voted, False or (False, str) on error.
        """
        try:
            return self._contract_instance.functions.hasUserVoted(
                position_id, voter_hash
            ).call()
        except Exception as e:
            return (False, str(e))


def fund_new_user_wallet(username_hash):
    """
    Creates a new wallet for a user, funds it, and updates the user's wallet info in the database.

    Args:
        wallet (str): The admin's wallet address.
        contract_add (str): The contract address.
        username_hash (str): The user's username hash.

    Returns:
        tuple: (bool, str) indicating success and a message.
    """
    
    # Create user wallet
    new_wallet = Account.create()
    address = new_wallet.address
    private_key = new_wallet.key.hex()
    print(f"New wallet address: {address}")
    print(f"New wallet private key: {private_key}")

    blockchain = Blockchain(fetch_admin_wallet_address(), fetch_admin_wallet_address())

    # Fund wallet address
    status, msg = blockchain.fund_wallet(address)

    if status:  # If wallet successfully funded, update wallet info
        user_wallet_update, e = update_voter_wallet_by_username(
            username_hash, address, encrypt_object(private_key)
        )

    return (user_wallet_update, e)
    
def get_voting_time():
        """
        Retrieves the voting start and end times from the blockchain.

        Returns:
            dict: Contains start and end times in both unix and readable formats, or error.
        """
        
        blockchain = Blockchain(fetch_admin_wallet_address(), fetch_admin_wallet_address())

        try:
            start_unix, end_unix = blockchain._contract_instance.functions.getVotingTime().call()

            return (start_unix,end_unix)

        except Exception as e:
            return (False, str(e))