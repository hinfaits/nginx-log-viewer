"""
This file defines all the database models used in this app.
For no particular reason the stock SQLAlchemy API is used
    instead of the Flask-SQLAlchemy API
Related reading - http://stackoverflow.com/questions/19119725/how-to-use-flask-sqlalchemy-with-existing-sqlalchemy-model/19121073#19121073
"""

from sqlalchemy import Column, String, Text, Integer, Float, DateTime, Boolean, ForeignKey, Sequence
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import logging

import nginx_log_viewer.utils as utils

Base = declarative_base()


def init():
    """
    Call this function to initialize the database
    """
    args = utils.get_args()
    engine = create_engine(args.database)

    logging.info("Emptying and initializing database.")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


class Log(Base):
    __tablename__ = 'log'
    id = Column(Integer, primary_key=True)
    path = Column(Text)
    name = Column(Text)
    record = relationship("Record")

    def __getattr__(self, key):
        if key == 'pathname':
            return self.path + self.name
        else:
            raise AttributeError


class Record(Base):
    __tablename__ = 'record'
    id = Column(Integer, primary_key=True)
    raw = Column(Text)
    ip_int = Column(Integer)
    user = Column(Text)
    time = Column(DateTime)
    status = Column(Integer)
    bytes_sent = Column(Integer)
    referrer = Column(Text)
    user_agent = Column(Text)
    gzip_ratio = Column(Float)
    file_id = Column(Integer, ForeignKey('log.id'))
    request = relationship("Request", uselist=False, back_populates="record")

    def __getattr__(self, key):
        if key == 'ip':
            return utils.int_to_ip(self.ip_int)
        else:
            raise AttributeError


class Request(Base):
    __tablename__ = 'request'
    id = Column(Integer, primary_key=True)
    method = Column(Text)
    resource = Column(Text)
    protocol = Column(Text)
    record_id = Column(Integer, ForeignKey('record.id'))
    record = relationship("Record", back_populates="request")

    def __str__(self):
        return "{} {} {}".format(method, resource, protocol)


init()
