import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, MetaData

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def delete_all_tables():
    """Delete all tables from the database"""
    engine = create_engine(DB_URL)
    
    # Reflect the database to get all existing tables
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    # Drop all tables
    metadata.drop_all(engine)
    print("✓ All tables deleted successfully.")

def delete_specific_table(table_name):
    """Delete a specific table from the database"""
    engine = create_engine(DB_URL)
    inspector = inspect(engine)
    
    existing_tables = inspector.get_table_names()
    
    if table_name in existing_tables:
        metadata = MetaData()
        metadata.reflect(bind=engine)
        metadata.tables[table_name].drop(engine)
        print(f"✓ Table '{table_name}' deleted successfully.")
    else:
        print(f"✗ Table '{table_name}' not found.")

def list_all_tables():
    """List all tables currently in the database"""
    engine = create_engine(DB_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if tables:
        print("Tables in database:")
        for table in tables:
            print(f"  - {table}")
    else:
        print("No tables found in database.")
    
    return tables

if __name__ == "__main__":
    # List current tables
    print("Current tables:")
    list_all_tables()
    
    # Uncomment below to delete all tables
    #delete_all_tables()

