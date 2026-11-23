from sqlmodel import Field, SQLModel


class Mod(SQLModel, table=True):
    """One trade stat, e.g. "explicit.stat_3299347043" = "# to maximum Life" (explicit)."""

    id: str = Field(primary_key=True, max_length=100)
    text: str = Field(max_length=300)
    source: str = Field(max_length=30)


class ModPublic(SQLModel):
    """What the API returns for a mod."""

    id: str
    text: str
    source: str
