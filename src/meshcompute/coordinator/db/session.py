"""SQLAlchemy engine/session creation for the coordinator."""
from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import Session,sessionmaker
from meshcompute.common.settings import get_settings

@lru_cache
def session_factory():
    """Return a process-local session factory with stale connection checks."""
    engine=create_engine(get_settings().sync_database_url,pool_pre_ping=True,pool_size=10,max_overflow=20)
    return sessionmaker(bind=engine,autoflush=False,expire_on_commit=False,class_=Session)
