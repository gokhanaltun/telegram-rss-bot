from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import sessionmaker
from .DB import SingletonDB

Base = SingletonDB.get_base()


def get_session():
    Session = sessionmaker(bind=SingletonDB.get_engine())
    return Session()


class Feed(Base):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text)
    url = Column(Text)
    last_read = Column(Text)

    def __repr__(self) -> str:
        return f"Feed(id={self.id!r}, name={self.name!r}, url={self.url!r}, last_read={self.last_read!r})"

    def __init__(self, name, url, last_read):
        self.name = name
        self.url = url
        self.last_read = last_read


Base.metadata.create_all(SingletonDB.get_engine())
