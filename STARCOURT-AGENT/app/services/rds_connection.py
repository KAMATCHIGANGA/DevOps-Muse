import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from dotenv import load_dotenv

load_dotenv()

database_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("RDS_USERNAME"),
    password=os.getenv("RDS_PASSWORD"),
    host=os.getenv("RDS_HOST"),
    port=int(os.getenv("RDS_PORT", "5432")),
    database=os.getenv("RDS_DATABASE"),
)

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10},
)


def get_registered_username(email: str):
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT username
                FROM public.user
                WHERE email = :email
                LIMIT 1
            """),
            {"email": email},
        )
        row = result.fetchone()

    return row[0] if row else None


if __name__ == "__main__":
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("RDS connection successful!")
        print(
            "Registered username:",
            get_registered_username("piper@piper.com")
        )
    except Exception as e:
        print("RDS connection failed:", e)