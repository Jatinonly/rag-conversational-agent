from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, Conversation, Message

# We created a new engine and a session because this way the tests are isolated and won't pollute your actual database.
engine = create_engine("sqlite:///:memory:")
TestSession = sessionmaker(bind=engine)

Base.metadata.create_all(engine)


def test_conversation_persistence():
    conversation_id = "test-conversation"

    with TestSession() as db:
        conversation = Conversation(id=conversation_id)
        db.add(conversation)

        db.add(
            Message(
                conversation_id=conversation_id,
                role="user",
                content="What is JWT?",
            )
        )

        db.add(
            Message(
                conversation_id=conversation_id,
                role="assistant",
                content="JWT is a JSON Web Token.",
            )
        )

        db.commit()

    with TestSession() as db:
        conversation = db.get(
            Conversation,
            conversation_id,
        )

        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.id)
            .all()
        )

        assert conversation is not None
        assert len(messages) == 2
        assert messages[0].role == "user"
        assert messages[1].role == "assistant"
