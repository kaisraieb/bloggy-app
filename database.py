from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager

# ad1da8bf50ab3fb235316165031ff698fb17ebc7fef1dca9798057450adbc0c8 (encryption key for db)
# DATABASE_URL = "sqlitecloud://ctypgmojnk.g4.sqlite.cloud:8860/bloggy-db?apikey=acxs9luoOfQijNHCT9nOp4LmglJm5lC0v0uLjZ15rsw"

DATABASE_URL = "sqlite:///./bloggy.db"

engine = create_engine(
  DATABASE_URL,
  poolclass=QueuePool,
  pool_size=5,
  max_overflow=10,
  pool_timeout=30,
  pool_recycle=1800,
  echo=True
)

Session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

@contextmanager
def session_scope():
  session = Session()
  try:
    yield session
    session.commit()
  except Exception:
    session.rollback()
    raise
  finally:
    session.close()