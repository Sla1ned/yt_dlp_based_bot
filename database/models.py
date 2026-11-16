from sqlalchemy import BigInteger, DateTime, func, String
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = ("users")

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    username: Mapped[str] = mapped_column(String, nullable=False)

    subscription_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    def __repr__(self) -> str:
        return f"<User id={self.id} sub_until={self.subscription_until}>"

class Group(Base):
    __tablename__ = ("groups")

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    group_name: Mapped[str] = mapped_column(String, nullable=True)

    subscription_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    def __repr__(self) -> str:
        return f"<Group id={self.id} sub_until={self.subscription_until}>"
