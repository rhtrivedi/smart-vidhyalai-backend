from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# This is the exact connection string for your Docker setup
# Format: postgresql://user:password@host:port/database_name
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://superadmin:securepassword123@localhost:5432/school_saas_db",
)

if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace(
        "postgres://", "postgresql://", 1
    )

# Create the engine that manages the connection
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a session factory for our API routes
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# The base class that all our future database models will inherit from
Base = declarative_base()


# Dependency to get the database session in our FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
