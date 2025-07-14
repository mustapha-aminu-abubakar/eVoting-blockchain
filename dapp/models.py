from flask_login import UserMixin
from .mixins import LockableMixin, register_lock_events  # <- import
from dapp.db import database
from datetime import datetime
import time


class Otp(database.Model, LockableMixin):
    id = database.Column(database.Integer, primary_key=True)

    username_hash = database.Column(database.String(64), unique=True, nullable=False)

    otp = database.Column(database.String(88), nullable=False)

    def __repr__(self) -> str:
        return f"""
        OTPs (
            id: {self.id}
            username_hash_hex: {self.username_hash}
            otp: {self.otp}
        )
        """


class Voter(database.Model, LockableMixin, UserMixin):
    id = database.Column(database.Integer, primary_key=True)

    username_hash = database.Column(database.String(64), unique=True, nullable=False)

    email_encrypted = database.Column(
        database.String(88), nullable=False, unique=True, default=""
    )

    password = database.Column(database.String(88), nullable=False)

    wallet_address = database.Column(
        database.String(42), unique=True, nullable=False, default=""
    )

    private_key_encrypted = database.Column(
        database.String(88), nullable=False, default=""
    )

    # vote_status = database.Column(
    #     database.Integer,
    #     nullable=False,
    #     default=0
    # )

    voter_status = database.Column(database.Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"""
        Voter (
            id: {self.id}
            username_hash: {self.username_hash}
            password: {self.password}
            email_encrypted: {self.email_encrypted}
            wallet_address: {self.wallet_address}
            private_key_encrypted: {self.private_key_encrypted}
            voter_status: {self.voter_status}
            is active: {self.voter_status}
        )
        """


class Candidate(database.Model, LockableMixin):
    id = database.Column(database.Integer, primary_key=True)

    name = database.Column(database.String(100), nullable=False)

    position_id = database.Column(
        database.Integer, database.ForeignKey("position.id"), nullable=False
    )

    vote_count = database.Column(database.Integer, default=0)

    candidate_status = database.Column(database.Boolean, nullable=False, default=True)

    # ✅ Add this field
    candidate_hash = database.Column(
        database.String(66),  # 0x-prefixed hex string of 32 bytes
        unique=True,
        nullable=False,
    )

    position = database.relationship("Position", backref="candidates")

    def __repr__(self) -> str:
        return f"""
        Candidate(
            id: {self.id}
            position_id: {self.position_id}
            name: {self.name}
            vote_count: {self.vote_count}
            candidate_status: {self.candidate_status}
            candidate_hash: {self.candidate_hash}
        )
        """

    def as_dict(self):
        return {
            "id": self.id,
            "position_id": self.position_id,
            "name": self.name,
            "vote_count": self.vote_count,
            "candidate_status": self.candidate_status,
            "candidate_hash": self.candidate_hash,
        }


class Position(database.Model, LockableMixin):
    id = database.Column(database.Integer, primary_key=True)

    position = database.Column(database.String(100), nullable=False, unique=False)

    def __repr__(self) -> str:
        return f"""
        Position(
            id: {self.id}
            postion: {self.position}
        )
        """


class Election(database.Model, LockableMixin):
    id = database.Column(database.Integer, primary_key=True)

    contract_address = database.Column(database.String(42), unique=True)

    status = database.Column(database.Boolean, nullable=False, default=False)

    def __repr__(self) -> str:
        return f"""
        Election(
            id: {self.id}
            contract_address: {self.contract_address}
            status: {self.status}
        )
        """


class Vote(database.Model, LockableMixin):
    id = database.Column(database.Integer, primary_key=True)

    position_id = database.Column(
        database.Integer, database.ForeignKey("position.id"), nullable=False
    )

    voter_hash = database.Column(database.String(66), nullable=False)

    candidate_hash = database.Column(database.String(66), nullable=False)

    date_time_ts = database.Column(
        database.Integer,
        nullable=False,
    )

    wallet_address = database.Column(database.String(64), nullable=False, unique=False)

    position = database.relationship("Position", backref="votes")

    def __repr__(self) -> str:
        return f"""
        Vote(
            id: {self.id}
            position_id: {self.position_id}
            voter_hash: {self.voter_hash}
            candidate_hash: {self.candidate_hash}
            date_time_ts: {self.date_time_ts}
            wallet_address: {self.wallet_address}
        )
        """


class Result(database.Model, LockableMixin):
    id = database.Column(database.Integer, primary_key=True)

    position_id = database.Column(database.Integer, nullable=False)

    position = database.Column(database.String(100), nullable=False)

    candidate_name = database.Column(database.String(100), nullable=False)

    candidate_hash = database.Column(
        database.String(66),
        database.ForeignKey("candidate.candidate_hash"),
        nullable=False,
    )

    vote_count = database.Column(database.Integer, default=0)

    is_winner = database.Column(database.Boolean, nullable=False, default=False)

    candidate = database.relationship("Candidate", backref="results")

    def __repr__(self) -> str:
        return f"""
        Result(
            id: {self.id}
            position_id: {self.position_id}
            candidate_hash: {self.candidate_hash}
            vote_count: {self.vote_count}
            is_winner: {self.is_winner}
            position: {self.position}
            candidate_name: {self.candidate_name}
        )
        """


class Transaction(database.Model, LockableMixin):
    txn_type = database.Column(database.String(66))
    
    txn_hash = database.Column(database.String(66), primary_key=True)

    status = database.Column(database.Boolean, default=False)

    sender = database.Column(database.String(66))

    gas = database.Column(database.Integer)

    txn_ts = database.Column(database.Integer, nullable=False, default=int(time.time()))

    def __repr__(self) -> str:
        return f"""
            Transaction(
                transaction hash: {self.txn_hash}
                transaction type: {self.txn_type}
                status: {self.status}
                sender wallet: {self.sender}
                gas used: {self.gas}
                transaction timestamp: {self.txn_ts}
            )
            """


register_lock_events(Otp)
register_lock_events(Voter)
register_lock_events(Candidate)
register_lock_events(Position)
register_lock_events(Election)
register_lock_events(Vote)
register_lock_events(Result)
register_lock_events(Transaction)
