import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()


class SingletonDb:
    __engine = None
    __base = None

    __SQLITE_DB = os.getenv("SQLITE_DB")

    @classmethod
    def get_engine(cls):
        if cls.__engine is None:
            cls.__engine = create_engine(cls.__SQLITE_DB, echo=False)
        return cls.__engine

    @classmethod
    def get_base(cls):
        if cls.__base is None:
            cls.__base = declarative_base()
        return cls.__base
