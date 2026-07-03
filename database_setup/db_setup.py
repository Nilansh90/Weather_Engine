import pandas as pd
from sqlalchemy import create_engine, Column, Integer, Float, String, Date, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

# 1. Get the directory of the current script (setup_tasks)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Go up one level to the project root
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# 3. Join to find your data
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw')

def create_tables():
    """Create the weather_data table with proper schema"""
    engine = create_engine(DB_URL)
    
    print("[SCHEMA] Creating database schema...")
    
    # SQL to create table with proper data types
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS weather_data (
        id SERIAL PRIMARY KEY,
        date DATE NOT NULL,
        time_gmt_5_30 TIMESTAMP WITH TIME ZONE,
        latitude FLOAT NOT NULL,
        longitude FLOAT NOT NULL,
        city_id INTEGER NOT NULL,
        city_name VARCHAR(100) NOT NULL,
        weather_code INTEGER,
        temp_mean_c FLOAT,
        temp_max_c FLOAT,
        temp_min_c FLOAT,
        wind_speed_max_kmh FLOAT,
        wind_gusts_max_kmh FLOAT,
        wind_direction_dominant_deg FLOAT,
        shortwave_radiation_sum_mj_m2 FLOAT,
        daylight_duration_s FLOAT,
        precipitation_sum_mm FLOAT,
        cloud_cover_mean_pct FLOAT,
        cloud_cover_max_pct FLOAT,
        cloud_cover_min_pct FLOAT,
        dew_point_mean_c FLOAT,
        dew_point_max_c FLOAT,
        dew_point_min_c FLOAT,
        relative_humidity_mean_pct FLOAT,
        relative_humidity_max_pct FLOAT,
        relative_humidity_min_pct FLOAT,
        pressure_msl_mean_hpa FLOAT,
        pressure_msl_max_hpa FLOAT,
        pressure_msl_min_hpa FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    with engine.connect() as conn:
        conn.execute(text(create_table_sql))
        conn.commit()
        print("[SCHEMA] [OK] Weather data table created/verified")
    
    # Create index on frequently queried columns
    create_index_sql = """
    CREATE INDEX IF NOT EXISTS idx_weather_city_date ON weather_data(city_id, date);
    CREATE INDEX IF NOT EXISTS idx_weather_date ON weather_data(date);
    """
    
    with engine.connect() as conn:
        for idx_stmt in create_index_sql.split(';'):
            if idx_stmt.strip():
                conn.execute(text(idx_stmt))
        conn.commit()
        print("[SCHEMA] [OK] Indexes created")


def load_data():
    """Load all CSV files from raw data directory into database"""
    engine = create_engine(DB_URL)
    
    print(f"\n[DATA] Loading CSV files from: {RAW_DATA_DIR}")
    
    csv_files = sorted([f for f in os.listdir(RAW_DATA_DIR) if f.endswith(".csv")])
    
    if not csv_files:
        print("[ERROR] No CSV files found!")
        return
    
    print(f"[DATA] Found {len(csv_files)} CSV file(s)\n")
    
    total_rows = 0
    
    for i, filename in enumerate(csv_files, 1):
        filepath = os.path.join(RAW_DATA_DIR, filename)
        print(f"[{i}/{len(csv_files)}] Loading {filename}...")
        
        try:
            df = pd.read_csv(filepath)
            
            # Data type conversions
            print(f"     Converting data types...")
            
            # Convert date column to datetime.date
            df['date'] = pd.to_datetime(df['date']).dt.date
            
            # Convert time_gmt_5_30 to datetime
            df['time_gmt_5_30'] = pd.to_datetime(df['time_gmt_5_30'])
            
            # Convert numeric columns to float (handle NaN)
            float_cols = [col for col in df.columns if col not in 
                         ['date', 'time_gmt_5_30', 'city_id', 'weather_code', 'city_name', 'latitude', 'longitude']]
            for col in float_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Ensure integer columns
            df['city_id'] = df['city_id'].astype(int)
            if 'weather_code' in df.columns:
                df['weather_code'] = df['weather_code'].fillna(0).astype(int)
            
            # Ensure string columns
            df['city_name'] = df['city_name'].astype(str)
            
            rows_count = len(df)
            print(f"     Inserting {rows_count} rows...")
            
            # Load to database
            df.to_sql('weather_data', engine, if_exists='append', index=False, method='multi', chunksize=1000)
            
            total_rows += rows_count
            print(f"     [OK] Successfully loaded {rows_count} rows from {filename}")
            
        except Exception as e:
            print(f"     [ERROR] Failed to load {filename}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n[COMPLETE] Total rows inserted: {total_rows}")
    print(f"[COMPLETE] All CSV files loaded to database!")


if __name__ == "__main__":
    print("="*80)
    print("[INIT] Starting database setup and data ingestion...")
    print("="*80)
    
    create_tables()
    load_data()
    
    print("\n" + "="*80)
    print("[SUCCESS] Database setup completed!")
    print("="*80)