#!/usr/bin/env python
"""
Script to initialize and check the database contents.
"""
import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

# Import the database models
from abidance.database.models import Base, Trade, Strategy, OHLCV

# Database path
DB_PATH = os.path.join('data', 'abidance.db')
DB_URL = f"sqlite:///{DB_PATH}"

def init_db():
    """Initialize the database if it doesn't exist."""
    print(f"Initializing database at {DB_PATH}")
    engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)
    return engine

def check_db_tables(engine):
    """Check what tables exist in the database."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("\nTables in the database:")
    for table in tables:
        print(f"- {table}")
    return tables

def check_table_contents(engine, table_name):
    """Check the contents of a specific table."""
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.scalar()
        print(f"\nTable '{table_name}' has {count} rows")
        
        if count > 0:
            # Show a sample of the data (first 5 rows)
            result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 5"))
            rows = result.fetchall()
            print(f"\nSample data from '{table_name}':")
            for row in rows:
                print(row)

def main():
    """Main function to initialize and check the database."""
    # Initialize the database
    engine = init_db()
    
    # Check what tables exist
    tables = check_db_tables(engine)
    
    # Check the contents of each table
    for table in tables:
        check_table_contents(engine, table)
    
    print("\nDatabase check complete.")

if __name__ == "__main__":
    main() 