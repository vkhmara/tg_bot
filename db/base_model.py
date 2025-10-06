import json
from typing import Optional, Self, Type
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.sql.expression import ColumnOperators
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy import Column, DateTime, desc, inspect, text
from db.base import db_decorator


class CustomBase:
    created_date = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    modified_date = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )

    def __repr__(self):
        return json.dumps(self.__dict__, default=str)

    @classmethod
    def get_filters(
        cls,
        **filter_kwargs,
    ) -> list[BinaryExpression]:
        criterion = [
            (
                None
                if value is None
                else ColumnOperators.__eq__(
                    getattr(cls, field),
                    value,
                )
            )
            for field, value in filter_kwargs.items()
        ]
        criterion = [x for x in criterion if x is not None]
        return criterion

    @classmethod
    @db_decorator
    def filter(
        cls,
        db: Session,
        optional: bool = False,
        many: bool = False,
        custom_criterion: list = None,
        order_by_created_date: bool = True,
        **filter_kwargs,
    ) -> Optional[Self | list[Self]]:
        criterion = cls.get_filters(**filter_kwargs) + (custom_criterion or [])
        filter_query = db.query(cls).filter(*criterion)
        if order_by_created_date:
            filter_query = filter_query.order_by(desc(cls.created_date))

        if many:
            return filter_query.all()

        instance = filter_query.one_or_none()
        if not instance and not optional:
            raise Exception(f"No {cls} Instance With Filters: {filter_kwargs}")
        return instance

    @classmethod
    @db_decorator
    def update_instance(
        cls,
        db: Session,
        filters: dict,
        data: dict,
    ):
        """
        Fetches an instance by filters, updates its fields with data,
        saves to db, and returns the object.
        """
        instance = cls.filter(db=db, **filters)
        if not instance:
            raise Exception(f"No {cls.__name__} instance found with filters: {filters}")
        instance.update(**data)
        instance.save_to_db(db=db)
        return instance

    @classmethod
    def all_columns(cls):
        return [column.name for column in inspect(cls).c]

    @classmethod
    @db_decorator
    def get_all(
        cls,
        db: Session,
    ):
        return [
            {col: getattr(obj, col, None) for col in cls.all_columns()}
            for obj in db.query(cls).all()
        ]

    def update(
        self,
        **new_fields,
    ):
        for field, value in new_fields.items():
            setattr(self, field, value)

    @db_decorator
    def save_to_db(
        self,
        db: Session,
    ):
        try:
            db.add(self)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        db.refresh(self)
        return self


Base: Type[CustomBase] = declarative_base(cls=CustomBase)
