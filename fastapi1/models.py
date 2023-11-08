# Import necessary modules
from database import Base
from sqlalchemy import Column, Integer, String

# Define a SQLAlchemy model for the "users" table
class Users(Base):
    # Set the table name
    __tablename__ = "users"
    
    # Define columns for the "users" table
    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, unique=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    Phone = Column(String, unique=True)
