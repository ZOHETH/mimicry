import sqlalchemy.exc

import contextlib
import json
import logging
from asyncio import AbstractEventLoop
from typing import Any, Dict, Optional, Text, Generator

from sqlalchemy.orm import Session
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy import Column, Integer, String
from sqlalchemy import Text as SqlAlchemyText  # to avoid name clash with typing.Text

logger = logging.getLogger(__name__)


class EventBroker:
    """Base class for any event broker implementation."""

    def publish(self, event: Dict[Text, Any]) -> None:
        """Publishes a json-formatted Rasa Core event into an event queue."""
        raise NotImplementedError("Event broker must implement the `publish` method.")

    def is_ready(self) -> bool:
        """Determine whether or not the event broker is ready.

        Returns:
            `True` by default, but this may be overridden by subclasses.
        """
        return True

    async def close(self) -> None:
        """Close the connection to an event broker."""
        # default implementation does nothing
        pass


class SQLEventBroker(EventBroker):
    """Save events into an SQL database.

    All events will be stored in a table called `events`.

    """

    Base: DeclarativeMeta = declarative_base()

    class SQLBrokerEvent(Base):
        """ORM which represents a row in the `events` table."""
        __tablename__ = "events"
        id = Column(Integer, primary_key=True)
        sender_id = Column(String(255))
        data = Column(SqlAlchemyText)

    def __init__(
            self,
            dialect: Text = "sqlite",
            host: Optional[Text] = None,
            port: Optional[int] = None,
            db: Text = "events.db",
            username: Optional[Text] = None,
            password: Optional[Text] = None,
    ) -> None:
        """Initializes `SQLBrokerEvent`."""

        import sqlalchemy.orm

        engine_url = URL(
            dialect, username, password, host, port, database=db
        )

        logger.debug(f"SQLEventBroker: Connecting to database: '{engine_url}'.")

        self.engine = sqlalchemy.create_engine(engine_url)
        self.Base.metadata.create_all(self.engine)
        self.sessionmaker = sqlalchemy.orm.sessionmaker(bind=self.engine)

    @contextlib.contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations."""
        session = self.sessionmaker()
        try:
            yield session
        finally:
            session.close()

    def publish(self, event: Dict[Text, Any]) -> None:
        """Publishes a json-formatted Rasa Core event into an event queue."""
        with self.session_scope() as session:
            session.add(
                self.SQLBrokerEvent(
                    sender_id=event.get("sender_id"), data=json.dumps(event)
                )
            )
            session.commit()
