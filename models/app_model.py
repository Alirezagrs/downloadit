from typing import TypeVar
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import String, create_engine, DateTime, select, asc

T = TypeVar("UrlString", bound=str)
engine = create_engine("sqlite:///app.db")


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "user_table"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    video: Mapped[T] = mapped_column(String, nullable=True)
    photo: Mapped[T] = mapped_column(String, nullable=True)
    music: Mapped[T] = mapped_column(String, nullable=True)
    file: Mapped[T] = mapped_column(String, nullable=True)
    downloaded_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)


def read():
    """Function for CLI mode to show status of downloads"""
    with Session(engine) as session:
        total_download = 0
        data = session.scalars(select(UserModel).order_by(asc(UserModel.downloaded_at)))
        for d in data:
            if d.video:
                total_download += 1
                print(f"{d.video} downloaded at {d.downloaded_at}")

            if d.photo:
                total_download += 1
                print(f"{d.photo} downloaded at {d.downloaded_at}")

            if d.music:
                total_download += 1
                print(f"{d.music} downloaded at {d.downloaded_at}")

            if d.file:
                total_download += 1
                print(f"{d.file} downloaded at {d.downloaded_at}")

        print("+" * 100)
        print(f"count of downloads : {total_download}")
