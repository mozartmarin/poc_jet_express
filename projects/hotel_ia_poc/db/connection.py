from sqlalchemy import create_engine
import pandas as pd

USER = "neondb_owner"
PASSWORD = "npg_kI8JxhWNynV1"
HOST = "ep-crimson-truth-a407yzlm-pooler.us-east-1.aws.neon.tech"
PORT = "5432"
DB_NAME = "neondb"

DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

def get_reservas():
    query = "SELECT * FROM reservas;"
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df
