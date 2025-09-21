from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "sqlite:///project.db"


def get_db() -> Session:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=True,
    )
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    return db


def db_decorator(func):
    @wraps(func)
    def inner_func(*args, **kwargs):
        if "db" in kwargs:
            return func(*args, **kwargs)
        with get_db() as db_conn:
            kwargs["db"] = db_conn
            return func(
                *args,
                **kwargs,
            )

    return inner_func
