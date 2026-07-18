from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.config import settings

# Construct the async Postgres URL from your environment variables
# Note: 'db' is the hostname of the postgres container on the Docker network
SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@db:5432/{settings.POSTGRES_DB}"

# The engine manages the actual connection pool to the database
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# The session factory spits out temporary sessions for our API routes to use
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)