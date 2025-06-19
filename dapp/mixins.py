from sqlalchemy import Column, Boolean, event
from sqlalchemy.orm import declared_attr


class LockableMixin:
    """
    Mixin class that adds a 'locked' boolean column and methods to lock/unlock all records.
    Provides class methods to lock, unlock, and check lock status for all instances in a table.
    """

    locked = Column(Boolean, default=False, nullable=False)

    @classmethod
    def lock_all(cls, session):
        """
        Locks all records of the model by setting the 'locked' field to True.

        Args:
            session (Session): SQLAlchemy session to use for the update.
        """
        session.query(cls).update({cls.locked: True})
        session.commit()

    @classmethod
    def unlock_all(cls, session):
        """
        Unlocks all records of the model by setting the 'locked' field to False.

        Args:
            session (Session): SQLAlchemy session to use for the update.
        """
        session.query(cls).update({cls.locked: False})
        session.commit()

    @classmethod
    def is_locked(cls, session):
        """
        Checks if any record of the model is currently locked.

        Args:
            session (Session): SQLAlchemy session to use for the query.

        Returns:
            bool: True if any record is locked, False otherwise.
        """
        return session.query(cls).filter(cls.locked.is_(True)).first() is not None


def prevent_locked_modifications(mapper, connection, target):
    """
    SQLAlchemy event listener that prevents modifications to locked records.

    Raises:
        Exception: If the target record is locked.
    """
    if hasattr(target, "locked") and target.locked:
        raise Exception(
            f"{target.__class__.__name__} is locked and cannot be modified."
        )


def register_lock_events(model_class):
    """
    Registers event listeners to prevent updates or deletions of locked records for a model.

    Args:
        model_class (DeclarativeMeta): The SQLAlchemy model class to protect.
    """
    event.listen(model_class, "before_update", prevent_locked_modifications)
    event.listen(model_class, "before_delete", prevent_locked_modifications)
