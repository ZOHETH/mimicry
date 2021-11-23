from typing import (
    Dict,
    Text,
    Any,
    Optional,
    Iterator,
    Generator,
    Type,
    List,
    Deque,
    Iterable,
    Union,
    FrozenSet,
    Tuple,
    TYPE_CHECKING,
)


class DialogueStateTracker:
    @classmethod
    def from_events(
            cls,
            sender_id: Text,
            events: List[Event],
            slots: Optional[Iterable[Slot]] = None,
            max_event_history: Optional[int] = None,
            sender_source: Optional[Text] = None,
            domain: Optional[Domain] = None,
    ) -> "DialogueStateTracker":
        """Creates tracker from existing events.

        Args:
            sender_id: The ID of the conversation.
            evts: Existing events which should be applied to the new tracker.
            slots: Slots which can be set.
            max_event_history: Maximum number of events which should be stored.
            sender_source: File source of the messages.
            domain: The current model domain.

        Returns:
            Instantiated tracker with its state updated according to the given
            events.
        """
        tracker = cls(sender_id, slots, max_event_history, sender_source)

        for e in events:
            tracker.update(e, domain)

        return tracker
