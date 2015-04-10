import datetime

from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    Text,
    Unicode,
    )

import transaction

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension(), expire_on_commit=False))
Base = declarative_base()

class MyMixin():

    @classmethod
    def add(cls, session, **kwargs):
        with transaction.manager:
            thing = cls(**kwargs)
            session.add(thing)
            transaction.commit()
        return thing

    @classmethod
    def get_all(cls, session):
        things = session.query(
            cls,
        ).all()
        return things

    @classmethod
    def get_by_id(cls, session, id):
        thing = session.query(
            cls,
        ).filter(
            cls.id == id,
        ).first()
        return thing

    @classmethod
    def delete_by_id(cls, session, id):
        with transaction.manager:
            thing = cls.get_by_id(id)
            session.delete(thing)
            transaction.commit()
        return thing

class Customers(Base, MyMixin):

    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)

    name = Column(Unicode(256))
    description = Column(Unicode(256))

    accounts = relationship('Accounts', lazy='joined', backref='customer')

class Accounts(Base, MyMixin):

    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)

    customer_id = Column(Integer, ForeignKey('customers.id'))
    #customer = relationship('Customers', lazy='subquery', backref='accounts')

    name = Column(Unicode(256))
    description = Column(Unicode(256))


