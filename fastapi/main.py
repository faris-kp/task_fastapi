# Import necessary modules and libraries
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile
from pydantic import BaseModel, EmailStr, validator
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from models import Users, Profile
from passlib.context import CryptContext
import os

# Create a FastAPI instance
app = FastAPI()

# Create database tables based on the models
models.Base.metadata.create_all(bind=engine)

# Create a bcrypt context for hashing passwords
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Define a Pydantic model for creating a new user
class CreateUserRequset(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str
    phone: str

# Define a Pydantic model for the response when getting user information
class getresponce(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    phone: str

    # Validator to check and format the phone number
    @validator('phone')
    def validate_phone(cls, phone):
        if len(phone) != 10 or not phone.isdigit():
            raise ValueError("Invalid phone number. Please enter a 10-digit numeric phone number.")
        return phone

# Define a Pydantic model for uploading a profile picture
class ProfilePictureRequset(BaseModel):
    profile_picture: UploadFile
    user_id: int

# Define a Pydantic model for the user response with profile picture path
class UserResponce(getresponce):
    profile_picture_path: str

# Function to get a database session using Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Annotated dependency for database session
db_dependency = Annotated[Session, Depends(get_db)]

# Route to create a new user
@app.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequset):
    # Check if the email and phone number are already registered
    existing_email = db.query(Users).filter(Users.email == create_user_request.email).first()
    existing_phone = db.query(Users).filter(Users.Phone == create_user_request.phone).first()
    
    if existing_email:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Email already registered")
    if existing_phone:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Phone number already registered")
    
    # Create a new user model and add it to the database
    create_user_model = Users(
        fullname=create_user_request.username,
        firstname=create_user_request.first_name,
        lastname=create_user_request.last_name,
        email=create_user_request.email,
        password=bcrypt_context.hash(create_user_request.password),
        Phone=create_user_request.phone
    )
    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    return {
        "user": create_user_model.fullname,
        "Message": "user created successfully"
    }

# Route to get user information by user ID
@app.get("/users/{user_id}", response_model=UserResponce)
async def get_user(user_id: int, db: db_dependency):
    # Query the user and their profile picture
    db_user = db.query(Users).filter(Users.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    
    if profile is None:
        raise HTTPException(status_code=400, detail="This user has not uploaded images, please upload them.")
    
    profile_picture_path = profile.profile_picture if profile else None

    user_data = {
        "id": db_user.id,
        "first_name": db_user.firstname,
        "last_name": db_user.lastname,
        "username": db_user.fullname,
        "email": db_user.email,
        "phone": db_user.Phone,
        "profile_picture_path": profile_picture_path
    }

    return UserResponce(**user_data)

# Route to upload a profile picture for a user
@app.post("/upload-profile-picture/")
async def upload_profile_picture(user_id: int, profile_picture: UploadFile, db: db_dependency):
    db_user = db.query(Users).filter(Users.id == user_id).first()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    upload_dir = "profile_pictures"

    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    file_extension = profile_picture.filename.split(".")[-1]
    file_path = f"profile_pictures/{user_id}.{file_extension}"

    with open(file_path, "wb") as f:
        f.write(profile_picture.file.read())

    new_profile = Profile(profile_picture=file_path, user_id=user_id)
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return {"message": "Profile picture uploaded successfully"}
