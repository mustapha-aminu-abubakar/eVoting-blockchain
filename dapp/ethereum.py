import json
import os
from datetime import datetime, timezone
from tzlocal import get_localzone
import pytz

from web3 import Web3
from dotenv import load_dotenv
from collections import defaultdict
from .credentials import WEB3_PROVIDER_URL
from .db_operations import get_offchain_results, add_txn
from .models import Candidate, Position

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
        return self.w3.eth.get_transaction_count(self._wallet_address, 'pending')

    def local_to_utc_timestamp(self, _timestamp: str) -> int:
        # local_tz = get_localzone()
        # local_dt = datetime.fromtimestamp(local_timestamp).replace(tzinfo=local_tz)
        # utc_dt = local_dt.astimezone(pytz.utc)
        # return int(utc_dt.timestamp())
        # Parse string to naive datetime
        print(f'Timestamp: {_timestamp}')
        local_naive_dt = datetime.strptime(_timestamp, "%Y-%m-%dT%H:%M")
        # Get local timezone
        local_tz = get_localzone()
        # Localize the naive datetime
        local_dt = local_tz.localize(local_naive_dt)
        # Convert to UTC
        utc_dt = local_dt.astimezone(pytz.utc)
        print(f"Local time: {local_dt.isoformat()} UTC time: {utc_dt.isoformat()}")
        print(f"Local timestamp: {local_dt.timestamp()} UTC timestamp: {utc_dt.timestamp()}")
        # Return UTC timestamp
        return int(utc_dt.timestamp())
    
    def to_utc_timestamp(self, dt_str, tz_name):
        naive = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M")
        local = pytz.timezone(tz_name).localize(naive)
        return int(local.astimezone(pytz.utc).timestamp())
    

    def set_voting_time(self, start_unix_time, end_unix_time, tz, private_key=ADMIN_PRIVATE_KEY):
        print(" [set_voting_time] Building transaction...")

        start_ts_utc = self.to_utc_timestamp(start_unix_time, tz)
        end_ts_utc = self.to_utc_timestamp(end_unix_time, tz)

        try:
            tx = self._contract_instance.functions.setVotingTime(
                start_ts_utc,
                end_ts_utc
            ).build_transaction({
                "gasPrice": int(self.w3.eth.gas_price * 1.2),
                "chainId": self.sepolia,
                "from": self._wallet_address,
                "nonce": self._get_nonce()
            })
            tx_receipt = self._send_tx(tx, private_key)
            return (bool(tx_receipt['status']), tx_receipt['transactionHash'].hex())
        except Exception as e:
            return (False, str(e))
         

    def extend_time(self, new_end_time, private_key=ADMIN_PRIVATE_KEY):
        try:
            tx = self._contract_instance.functions.extendVotingTime(
                new_end_time
            ).build_transaction({
                "gasPrice": int(self.w3.eth.gas_price * 1.2),
                "chainId": self.sepolia,
                "from": self._wallet_address,
                "nonce": self._get_nonce()
            })
            tx_receipt = self._send_tx(tx, private_key)
            return (bool(tx_receipt['status']), tx_receipt['transactionHash'].hex())
        except Exception as e:
            return (False, str(e))
        
    def get_voting_time(self):
        try:
            start_unix, end_unix = self._contract_instance.functions.getVotingTime().call()
            
            # Convert to readable datetime in UTC
            start_time = datetime.utcfromtimestamp(start_unix, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            end_time = datetime.utcfromtimestamp(end_unix, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

            return {
                "start_unix": start_unix,
                "end_unix": end_unix,
                "start_time": start_time,
                "end_time": end_time
            }

        except Exception as e:
            return {"error": str(e)}

    def vote(self, private_key, position_id, voter_hash, candidate_hash):
        print(f''' 
              [vote] Building transaction...
              Voter Hash: {voter_hash}
              Candidate Hash: {candidate_hash}
              Position ID: {position_id}
              ''')
        try:
            tx = self._contract_instance.functions.vote(
                int(position_id),
                Web3.to_bytes(hexstr=voter_hash),
                Web3.to_bytes(hexstr=candidate_hash)
            ).build_transaction({
                "gasPrice": int(self.w3.eth.gas_price * 1.2),
                "gas": 2000000,
                "chainId": self.sepolia,
                "from": self._wallet_address,
                "nonce": self._get_nonce()
            })
            tx_receipt = self._send_tx(tx, private_key)
            return (bool(tx_receipt['status']), tx_receipt['transactionHash'].hex())
        except Exception as e:
            return (False, str(e))

    # def get_votes(self, position_id, candidate_hash):
    #     'Returns number of votes a candidate has in a given position'
    #     try:
    #         return self._contract_instance.functions.getVotes(
    #             int(position_id),
    #             f'0x{candidate_hash}'
    #         ).call()
    #     except Exception as e:
    #         return f"Error fetching votes: {str(e)}"

    def register_candidate(self, private_key, position_id, candidate_hash):
        'Admin-only: Registers a candidate hash under a specific position'
        try:
            tx = self._contract_instance.functions.registerCandidate(
                int(position_id),
                candidate_hash
            ).build_transaction({
                "gasPrice": int(self.w3.eth.gas_price * 1.2),
                "chainId": self.sepolia,
                "from": self._wallet_address,
                "nonce": self._get_nonce()
            })
            tx_receipt = self._send_tx(tx, private_key)
            return (bool(tx_receipt['status']), tx_receipt['transactionHash'].hex())
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
        # print(" Sending Tx...")
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        # print(" Waiting for Tx receipt...")
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
        add_txn(tx_receipt['transactionHash'].hex(),
                bool(tx_receipt['status']),
                tx_receipt['from'],
                int(tx_receipt['gasUsed']))
        # print(f"{bool(tx_receipt['status'])} gasused: {tx_receipt['gasUsed']}")
        print(tx_receipt)
        # AttributeDict(
        # {'blockHash': HexBytes('0x51e8a2e2b1d1f095d1e2e9df37211252df596f9a566509d930aaf48fd6785079'), 
        # 'blockNumber': 8566631, 'contractAddress': None, 'cumulativeGasUsed': 8433315, 
        # 'effectiveGasPrice': 13822442, 'from': '0x6C0aFB8EbF46bEDf452d6eA73A6C9E3afBF66bA5', 
        # 'gasUsed': 34260, 'logs': [], 'logsBloom': HexBytes('0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'), 
        # 'status': 1, 'to': '0xd7B62Ae4E9C442D4611449bb3f57Cd8B25D1b210', 
        # 'transactionHash': HexBytes('0xd641e321c64b7e22211a84b63a1d6f193c4bcdeb0fb2cf1051fa7b3ca19a1fd5'), 
        # 'transactionIndex': 64, 'type': 0})
        return tx_receipt

    def fund_wallet(self, to_address):
        try:
            tx = {
                'to': to_address,
                'value': self.w3.to_wei(0.002, 'ether'),
                'gas': 21000,
                'nonce': self._get_nonce(),
                'chainId': self.sepolia,
                'maxFeePerGas': int(self.w3.eth.gas_price * 1.2),
                'maxPriorityFeePerGas': self.w3.eth.gas_price // 2,
                'type': 2  # EIP-1559 transaction type
            }
            # print(f"maxFeePerGas: {tx['maxFeePerGas']/1000000}")
            # print(f"maxPriorityFeePerGas: {tx['maxPriorityFeePerGas']/1000000}")    

            tx_receipt = self._send_tx(tx, ADMIN_PRIVATE_KEY)
            return (bool(tx_receipt['status']), tx_receipt['transactionHash'].hex())
        except Exception as e:
            return (False, str(e))
        
    def get_onchain_results(self):
        results = {}
        for candidate in Candidate.query.all():
            # candidate_hash_bytes32 = candidate.candidate_hash  # assuming you stored the hash
            count = self._contract_instance.functions.getVoteCounts(
                candidate.position_id, 
                Web3.to_bytes(hexstr=candidate.candidate_hash)
                ).call()
            results[candidate.id] = candidate.as_dict() 
            results[candidate.id]['vote_count'] = count
            # results[candidate.id]['candidate_hash'] = results[candidate.id]['candidate_hash'].hex()
            results[candidate.id]['position'] = candidate.position.position
            # print(f"Candidate {candidate_hash} ({candidate.id}) has {count} votes on-chain.")
        # print(results)
        print(f'On-chain results: {results} \n\n')
        return results
    
    
    def group_candidates_by_position(self):
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
        print(f'Grouped results {dict(grouped)}')
        return dict(grouped) 
    
    def get_all_votes(self):
        try:
            all_votes = self._contract_instance.functions.getAllVotes().call()
            print(f"All votes fetched: {all_votes}")
            return all_votes
        except Exception as e:
            return f"Error fetching all votes: {str(e)}"
    
    def publish(self):
        try:
            # offchain = get_offchain_results()
            # results = self.group_candidates_by_position()
            

            # for cid in offchain:
            #     if offchain[cid] != onchain.get(cid, 0):
            #         raise Exception(f"Mismatch for candidate {cid}: offchain {offchain[cid]}, onchain {onchain.get(cid, 0)}")

            # If matched, finalize on-chain
            tx = self._contract_instance.functions.publishResults().build_transaction({
                "from": self.w3.eth.default_account,
                "nonce": self._get_nonce(),
                "chainId": self.sepolia,
                "gas": 200000,
                "maxFeePerGas": int(self.w3.eth.gas_price * 1.2),
                "maxPriorityFeePerGas": self.w3.eth.gas_price // 2
            })

            tx_receipt = self._send_tx(tx, ADMIN_PRIVATE_KEY)
            return (bool(tx_receipt['status']), tx_receipt['transactionHash'].hex())
        except Exception as e:
            return (False, str(e), None)
    
    def get_voting_time(self):
        try:
            now = self._contract_instance.functions.getCurrentTimestamp().call()
            start = self._contract_instance.functions.startVotingTime().call()
            end = self._contract_instance.functions.endVotingTime().call()
            print (f"Current time: {now}, Start time: {start}, End time: {end}")
        except Exception as e:
            return (False, str(e))
        
    def has_user_voted(self, position_id, voter_hash):
        try:
            return self._contract_instance.functions.hasUserVoted(position_id, voter_hash).call()
        except Exception as e:
            return (False, str(e))    
    