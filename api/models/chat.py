import datetime

from sqlalchemy import Column, String, Integer, ARRAY, ForeignKey, Table
from sqlalchemy.orm import relationship

from api.database import Base
from api.models.mixins import IdMixin, TimeStampMixin


class Chat(Base, IdMixin, TimeStampMixin):
    __tablename__ = 'chat'
    name = Column(String(255))
    user_ids = Column(ARRAY(Integer))
    
    users = relationship("User",
                         secondary=lambda: Table(
                             'chat_users',
                             Base.metadata,
                             Column('chat_id', Integer, ForeignKey('chat.id')),
                             Column('user_id', Integer, ForeignKey('user.id'))
                         ))


class Message(Base, IdMixin, TimeStampMixin):
    __tablename__ = 'message'
    chat_id = Column(Integer, ForeignKey('chat.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    text = Column(String(255))
    
    def dict(self):
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'user_id': self.user_id,
            'text': self.text,
            'created': self.created.strftime('%Y-%m-%d %H:%M:%S'),
            'modified': self.modified.strftime('%Y-%m-%d %H:%M:%S'),
        }
