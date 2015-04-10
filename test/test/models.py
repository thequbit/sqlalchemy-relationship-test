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

    # modified from:
    #     
    def __json__(self, request):
        """
        Converts all the properties of the object into a dict for use in json.
        You can define the following in your class

        _json_eager_load :
            list of which child classes need to be eagerly loaded. This applies
            to one-to-many relationships defined in SQLAlchemy classes.

        _base_blacklist :
            top level blacklist list of which properties not to include in JSON

        _json_blacklist :
            blacklist list of which properties not to include in JSON

        :param request: Pyramid Request object
        :type request: <Request>
        :return: dictionary ready to be jsonified
        :rtype: <dict>
        """
 
        props = {}
 
        # grab the json_eager_load set, if it exists
        # use set for easy 'in' lookups
        json_eager_load = set(getattr(self, '_json_eager_load', []))
        # now load the property if it exists
        # (does this issue too many SQL statements?)
        for prop in json_eager_load:
            getattr(self, prop, None)
 
        # we make a copy because the dict will change if the database
        # is updated / flushed
        options = self.__dict__.copy()
 
        # setup the blacklist
        # use set for easy 'in' lookups
        blacklist = set(getattr(self, '_base_blacklist', []))
        # extend the base blacklist with the json blacklist
        blacklist.update(getattr(self, '_json_blacklist', []))
 
        for key in options:
            print key
            # skip blacklisted, private and SQLAlchemy properties
            if key in blacklist or key.startswith(('__', '_sa_')):
                continue
 
            # format and date/datetime/time properties to isoformat
            obj = getattr(self, key)
            if isinstance(obj, datetime.datetime):
                props[key] = obj.isoformat()
            else:
                # get the class property value
                attr = getattr(self, key)
                # let see if we need to eagerly load it
                if key in json_eager_load:
                    # this is for SQLAlchemy foreign key fields that
                    # indicate with one-to-many relationships
                    if not hasattr(attr, 'pk') and attr:
                        # jsonify all child objects
                        attr = [x.__json__(request) for x in attr]
                else:
                    # convert all non integer strings to string or if
                    # string conversion is not possible, convert it to
                    # Unicode
                    if attr and not isinstance(attr, (int, float)):
                        try:
                            attr = str(attr)
                        except UnicodeEncodeError:
                            attr = unicode(attr)  # .encode('utf-8')
 
                props[key] = attr
 
        return props

class Customers(Base, MyMixin):

    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)

    name = Column(Unicode)
    description = Column(Unicode)

    accounts = relationship('Accounts', backref='customer')

class Accounts(Base, MyMixin):

    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)

    customer_id = Column(Integer, ForeignKey('customers.id'))

    name = Column(Unicode)
    description = Column(Unicode)


