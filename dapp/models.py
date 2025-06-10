from flask_login import UserMixin

from dapp.db import database


class Otp(database.Model):
    id = database.Column(
        database.Integer,
        primary_key=True
    )

    username_hash = database.Column(
        database.String(64),
        unique=True,
        nullable=False
    )

    otp = database.Column(
        database.String(88),
        nullable=False
    )

    def __repr__(self) -> str:
        return f'''
        OTPs (
            id: {self.id}
            username_hash: {self.username_hash}
            otp: {self.otp}
        )
        '''


class Voter(database.Model, UserMixin):
    id = database.Column(
        database.Integer,
        primary_key=True
    )

    username_hash = database.Column(
        database.String(64),
        unique=True,
        nullable=False
    )

    email_encrypted = database.Column(
        database.String(88),
        nullable = False,
        unique = True,
        default = ''
    )

    password = database.Column(
        database.String(88),
        nullable=False
    )

    wallet_address = database.Column(
        database.String(42),
        unique=True,
        nullable=False,
        default=''
    )

    private_key_encrypted = database.Column(
        database.String(88),
        nullable=False,
        default=''
    )

    # vote_status = database.Column(
    #     database.Integer,
    #     nullable=False,
    #     default=0
    # )

    voter_status = database.Column(
        database.Boolean,
        nullable=False,
        default=True
    )

    def __repr__(self) -> str:
        return f'''
        Voter (
            id: {self.id}
            username_hash: {self.username_hash}
            password: {self.password}
            email_encrypted: {self.email_encrypted}
            wallet_address: {self.wallet_address}
            private_key_encrypted: {self.private_key_encrypted}
            voter_status: {self.voter_status}
        )
        '''


class Candidate(database.Model):
    id = database.Column(
        database.Integer,
        primary_key=True
    )

    # username = database.Column(
    #     database.String(64),
    #     unique=True
    # )

    name = database.Column(
        database.String(100),
        nullable=False
    )
    
    position_id = database.Column(
        database.Integer,
        database.ForeignKey('position.id'), 
        nullable=False
    )


    vote_count = database.Column(
        database.Integer,
        default=0
    )

    candidate_status = database.Column(
        database.Boolean,
        nullable=False,
        default=True
    )
    
    # ✅ Add this field
    candidate_hash = database.Column(
        database.String(66),  # 0x-prefixed hex string of 32 bytes
        unique=True,
        nullable=False
    )

    position = database.relationship("Position", backref="candidates")

    def __repr__(self) -> str:
        return f'''
        Candidate(
            id: {self.id}
            position_id: {self.position_id}
            name: {self.name}
            vote_count: {self.vote_count}
            candidate_status: {self.candidate_status}
            candidate_hash: {self.candidate_hash}
        )
        '''

class Position(database.Model):
    id = database.Column(
        database.Integer,
        primary_key=True
    )

    position = database.Column(
        database.String(100),
        nullable=False,
        unique=False
    )
    
    def __repr__(self) -> str:
        return f'''
        Position(
            id: {self.id}
            postion: {self.position}
        )
        '''

class Election(database.Model):
    id = database.Column(
        database.Integer,
        primary_key=True
    )

    contract_address = database.Column(
        database.String(42),
        unique=True
    )

    status = database.Column(
        database.Boolean,
        nullable=False,
        default=False
    )

    def __repr__(self) -> str:
        return f'''
        Election(
            id: {self.id}
            contract_address: {self.contract_address}
            status: {self.status}
        )
        '''

class Vote(database.Model):
    id = database.Column(database.Integer, primary_key=True)

    voter_id = database.Column(
        database.Integer,
        database.ForeignKey('voter.id'),
        nullable=False
    )

    position_id = database.Column(
        database.Integer,
        database.ForeignKey('position.id'),
        nullable=False
    )

    candidate_id = database.Column(
        database.Integer,
        database.ForeignKey('candidate.id'),
        nullable=False
    )
    
    vote_hash = database.Column(
        database.String(66),  # 0x-prefixed hex string of 32 bytes
        unique=True,
        nullable=False
    )

    __table_args__ = (
        database.UniqueConstraint('voter_id', 'position_id', name='unique_vote_per_position'),
    )
    
    voter = database.relationship('Voter', backref='votes')
    candidate = database.relationship('Candidate', backref='votes')

    def __repr__(self) -> str:
        return f'''
        Vote(
            id: {self.id}
            voter_id: {self.voter_id}
            position_id: {self.position_id}
            candidate_id: {self.candidate_id}
            vote_hash: {self.vote_hash} 
        )
        '''
