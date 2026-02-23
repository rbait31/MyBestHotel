"""Модель профиля пользователя."""
from datetime import datetime
import json

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(String(64), primary_key=True)
    profile_json = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
