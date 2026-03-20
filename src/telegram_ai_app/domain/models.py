from dataclasses import dataclass


@dataclass(frozen=True)
class InboundMessage:
    chat_id: str
    user_id: str
    message_id: str
    text: str
    session_key: str


@dataclass(frozen=True)
class ConversationTurn:
    role: str
    content: str


@dataclass(frozen=True)
class OutboundMessage:
    chat_id: str
    text: str
