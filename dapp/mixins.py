from sqlalchemy import Column, Boolean, event
from sqlalchemy.orm import declared_attr

class LockableMixin:
    locked = Column(Boolean, default=False, nullable=False)

    @classmethod
    def lock_all(cls, session):
        session.query(cls).update({cls.locked: True})
        session.commit()

    @classmethod
    def unlock_all(cls, session):
        session.query(cls).update({cls.locked: False})
        session.commit()

    @classmethod
    def is_locked(cls, session):
        return session.query(cls).filter(cls.locked.is_(True)).first() is not None

def prevent_locked_modifications(mapper, connection, target):
    if hasattr(target, 'locked') and target.locked:
        raise Exception(f"{target.__class__.__name__} is locked and cannot be modified.")

def register_lock_events(model_class):
    event.listen(model_class, 'before_update', prevent_locked_modifications)
    event.listen(model_class, 'before_delete', prevent_locked_modifications)
