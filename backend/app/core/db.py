from sqlmodel import create_engine

from app.core.config import settings

# pool_pre_ping tests each pooled connection before handing it out, so a connection the
# database has closed (for example after a database restart) is replaced instead of failing.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
