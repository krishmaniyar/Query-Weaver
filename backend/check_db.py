"""
Utility script: lists all tables in the configured database.
Run with:  python check_db.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import inspect
from app.db.database import get_engine

engine = get_engine()
inspector = inspect(engine)
tables = inspector.get_table_names()
print("Tables in database:", tables)
