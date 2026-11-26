import uuid

from sqlmodel import Field, SQLModel


class Vote(SQLModel, table=True):
    """One user's upvote on one template. The two ids together are the primary key, so a user
    can vote on a template only once."""

    user_id: uuid.UUID = Field(
        foreign_key="user.id", primary_key=True, ondelete="CASCADE"
    )
    template_id: uuid.UUID = Field(
        foreign_key="template.id", primary_key=True, index=True, ondelete="CASCADE"
    )
