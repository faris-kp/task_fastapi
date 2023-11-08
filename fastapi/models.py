# Import necessary modules
from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey

# Define a SQLAlchemy model for the "users" table
class Users(Base):
    # Set the table name
    __tablename__ = "users"
    
    # Define columns for the "users" table
    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, unique=True)
    firstname = Column(String)
    lastname = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    Phone = Column(String, unique=True)

# Define a SQLAlchemy model for the "profiles" table
class Profile(Base):
    # Set the table name
    __tablename__ = "profiles"

    # Define columns for the "profiles" table
    id = Column(Integer, primary_key=True, index=True)
    profile_picture = Column(String)
    
    # Define a foreign key relationship to the "users" table using the "user_id" column
    user_id = Column(Integer, ForeignKey("users.id"))
