# Import SQLAlchemy modules
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Define the database connection URL
URL_DATABASE = 'postgresql://postgres:abcd%401234@localhost:5433/task_user_creation'

# Create a SQLAlchemy database engine with the specified URL
engine = create_engine(URL_DATABASE)

# Create a session factory using sessionmaker
# - autocommit=False: This ensures that changes are not automatically committed to the database.
# - autoflush=False: This disables the automatic flush of the session.
# - bind=engine: Associates the session factory with the database engine.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a declarative base
# Declarative base is a base class for declarative class definitions.
# It is used to define the base class for your data models (database tables).
# You will typically create your database models by subclassing this base.
Base = declarative_base()
