from sqlalchemy import text
from app.db.database import engine, Base
from app.db import models


def init_db():
    print("Creating pgvector extension...")

    with engine.connect() as connection:
        connection.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector;")
        )
        connection.commit()

    print("Creating tables...")

    Base.metadata.create_all(bind=engine)

    print("Database initialized successfully.")


if __name__ == "__main__":
    init_db()