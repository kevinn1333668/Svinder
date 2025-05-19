from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Table
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

# Association table for user interests
user_interests = Table(
    'user_interests',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('interest_id', Integer, ForeignKey('interests.id'))
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False)
    invite_codes = relationship("InviteCode", back_populates="creator")
    invited_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    invited_users = relationship("User", backref="inviter", remote_side=[id])

class Profile(Base):
    __tablename__ = 'profiles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    university = Column(String, nullable=False)
    bio = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profile")
    interests = relationship("Interest", secondary=user_interests, back_populates="users")

class Interest(Base):
    __tablename__ = 'interests'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    users = relationship("Profile", secondary=user_interests, back_populates="interests")

class InviteCode(Base):
    __tablename__ = 'invite_codes'
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    is_used = Column(Boolean, default=False)
    used_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    creator = relationship("User", back_populates="invite_codes", foreign_keys=[creator_id])
    user = relationship("User", foreign_keys=[used_by]) 