import json
import os
from datetime import datetime, timezone
from tzlocal import get_localzone
import pytz

from web3 import Web3
from dotenv import load_dotenv
from .credentials import WEB3_PROVIDER_URL

load_dotenv()
ADMIN_PRIVATE_KEY = os.getenv("ADMIN_PRIVATE_KEY")


class Blockchain:
    _ABI_DIR = f'{os.getcwd()}/contract/ABI.json'
    sepolia = 11155111

    def __init__(self, wallet_address, contract_address):
        self._read_ABI()
        self._wallet_address = wallet_address
        self._contract_address = contract_address

        self.w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))
        self.w3.eth.default_account = self._wallet_address

        self._contract_instance = self.w3.eth.contract(
            abi=self._ABI,
            address=self._contract_address
        )

    def _read_ABI(self):
        with open(self._ABI_DIR) as ABI_file:
            self._ABI = json.loads(ABI_file.read())

    def _get_nonce(self):
        return self.w3.eth.get_transaction_count(self._wallet_address)

    def local_to_utc_timestamp(self, local_timestamp: int) -> int:
        local_tz = get_localzone()
        local_dt = datetime.fromtimestamp(local_timestamp).replace(tzinfo=local_tz)
        utc_dt = local_dt.astimezone(pytz.utc)
        return int(utc_dt.timestamp())
    
    def generate_candidate_hash(candidate_id, name, position_id):
        """
        Generates a keccak256 hash for a candidate using their id, name, and position.
        """
        input_string = f"{candidate_id}:{name}:{position_id}"
        return Web3.keccak(text=input_string).hex()

    def set_voting_time(self, private_key, start_unix_time, end_unix_time):
        print(" [set_voting_time] Building transaction...")

        start_utc = self.local_to_utc_timestamp(start_unix_time)
        end_utc = self.local_to_utc_timestamp(end_unix_time)

        try:
            tx = self._contract_instance.functions.setVotingTime(
                start_utc,
                end_utc
            ).build_transaction({
                "gasPrice": self.w3.eth.gas_price,
                "chainId": self.sepolia,
                "from": self._wallet_address,
                "nonce": self._get_nonce()
            })
            return (True, self._send_tx(tx, private_key))
        except Exception as e:
            return (False, str(e))

    def extend_time(self, private_key, new_end_time):
        try:
            tx = self._contract_instance.functions.extendVotingTime(
                new_end_time
            ).build_transaction({
                "gasPrice": self.w3.eth.gas_price,
                "chainId": self.sepolia,
                "from": self._wallet_address,
                "nonce": self._get_nonce()
            })
            return (True, self._send_tx(tx, private_key))
        except Exception as e:
            return (False, str(e))

    def vote(self, private_key, position_id, voter_hash, candidate_hash):
        print(" [vote] Building transaction...")
        try:
            tx = self._contract_instance.functions.vote(
                int(position_id),
                f'0x{voter_hash}',
                f'0x{candidate_hash}'
            ).build_transaction({
                "gasPrice": self.w3.eth.gas_price,
                "gas": 2000000,
                "chainId": self.sepolia,
                "from": self._wallet_address,
                "nonce": self._get_nonce()
            })
            return (True, self._send_tx(tx, private_key))
        except Exception as e:
            return (False, str(e))

    def get_votes(self, position_id, candidate_hash):
        'Returns number of votes a candidate has in a given position'
        try:
            return self._contract_instance.functions.getVotes(
                int(position_id),
                f'0x{candidate_hash}'
            ).call()
        except Exception as e:
            return f"Error fetching votes: {str(e)}"

    def register_candidate(self, private_key, position_id, candidate_hash):
        'Admin-only: Registers a candidate hash under a specific position'
        try:
            tx = self._contract_instance.functions.registerCandidate(
                int(position_id),
                f'0x{candidate_hash}'
            ).build_transaction({
                "gasPrice": self.w3.eth.gas_price,
                "chainId": self.sepolia,
                "from": self._wallet_address,
                "nonce": self._get_nonce()
            })
            return (True, self._send_tx(tx, private_key))
        except Exception as e:
            return (False, str(e))

    def get_candidates(self, position_id):
        try:
            return [
                candidate.hex() for candidate in
                self._contract_instance.functions.getCandidates(position_id).call()
            ]
        except Exception as e:
            return f"Error fetching candidates: {str(e)}"

    def print_current_block_timestamp(self):
        timestamp = self._contract_instance.functions.getCurrentTimestamp().call()
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        print(f"Current contract block.timestamp: {timestamp} ({dt.isoformat()})")

    def _send_tx(self, tx, private_key):
        private_key = f'0x{private_key}'
        print(f" Signing Tx...{private_key}")
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=private_key)
        print(" Sending Tx...")
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(" Waiting for Tx receipt...")
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
        print(tx_receipt['transactionHash'].hex())
        return tx_receipt['transactionHash'].hex()

    def fund_wallet(self, to_address):
        tx = {
            'to': to_address,
            'value': self.w3.to_wei(0.002, 'ether'),
            'gas': 21000,
            'nonce': self._get_nonce(),
            'chainId': self.sepolia,
            'maxFeePerGas': self.w3.eth.gas_price,
            'maxPriorityFeePerGas': self.w3.to_wei(0.00005, 'gwei'),
            'type': 2  # EIP-1559 transaction type
        }
        # print(f"maxFeePerGas: {tx['maxFeePerGas']/1000000}")
        # print(f"maxPriorityFeePerGas: {tx['maxPriorityFeePerGas']/1000000}")    

        try:
            return (True, self._send_tx(tx, ADMIN_PRIVATE_KEY))
        except Exception as e:
            return (False, str(e))

        