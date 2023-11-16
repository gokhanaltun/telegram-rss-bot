from sqlalchemy import Column, Integer, TEXT, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from .singleton_db import SingletonDb

Base = SingletonDb.get_base()


def get_session():
    Session = sessionmaker(bind=SingletonDb.get_engine())
    return Session()


class User(Base):

    __tablename__ = "users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    chat_id = Column("chat_id", TEXT)
    feeds = relationship("Feed", back_populates="user")

    def __init__(self, chat_id):
        self.chat_id = chat_id


class Feed(Base):

    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(TEXT)
    url = Column(TEXT)
    last_read = Column(TEXT)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="feeds")

    def __init__(self, name, url, last_read, user):
        self.name = name
        self.url = url
        self.last_read = last_read
        self.user = user


Base.metadata.create_all(SingletonDb.get_engine())
