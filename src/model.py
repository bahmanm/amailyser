'''

@author: Bahman Movaqar
@contact: Bahman AT BahmanM.com
@copyright:  (c) Bahman Movaqar
@license: 
    This file is part of amailyser (The E-mail Analyser).

    amialyser is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    amialyser is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with amialyser.  If not, see <http://www.gnu.org/licenses/>.
    
@version: 0.0.1

'''

from sqlalchemy import Column, ForeignKey, Integer, Unicode, DateTime, String
from sqlalchemy.orm import relationship, backref
import sqlalchemy.ext.declarative, sqlalchemy.orm
import config

###############################################################################
Base = sqlalchemy.ext.declarative.declarative_base()
metadata = Base.metadata
engine = sqlalchemy.create_engine(config.dburl, echo=True)
session = sqlalchemy.orm.sessionmaker(engine)()

###############################################################################
class Message(Base):
    __tablename__ = 'message'

    id = Column(String(255), primary_key=True)
    subject = Column(Unicode(255))
    msgdate = Column(DateTime())
    size = Column(Integer())
    inreplyto = Column(String(255), ForeignKey('message.id'))
    fromcontact_email = Column(String(255), ForeignKey('contact.email'))
    
    replies = relationship('Message', backref=backref('message', remote_side=id))
    recipients = relationship('MsgRecipient', backref='message')

###############################################################################
class Contact(Base):
    __tablename__ = 'contact'

    email = Column(String(255), primary_key=True)
    name = Column(Unicode(255))

###############################################################################    
class MsgRecipient(Base):
    __tablename__ = 'msgrecipient'

    message_id = Column(Integer(), ForeignKey('message.id'), primary_key=True)
    contact_email = Column(String(255), ForeignKey('contact.email'), primary_key=True)
    # either 'to' or 'cc'
    recipient_type = Column(String(2), primary_key=True)

    contact = relationship('Contact', backref='msgreceipent')


###############################################################################
def create_entities():
    session.autoflush = False
    session.autocommit = False
    metadata.create_all(engine)
