# Import necessary modules
from fastapi import FastAPI, HTTPException, Form, UploadFile, Depends, status
from pymongo import MongoClient
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from models import Users
import models
from passlib.context import CryptContext
from typing import Annotated
from pydantic import EmailStr

# Create a FastAPI instance
app = FastAPI()

# Create database tables based on the models
models.Base.metadata.create_all(bind=engine)

# Connect to MongoDB and set up the database and collection
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["sample"]
mongo_collection = mongo_db["user_profile"]

# Create a bcrypt context for hashing passwords
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Function to get a database session using Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Annotated dependency for the database session
db_dependency = Annotated[Session, Depends(get_db)]

# Route to register a new user
@app.post("/register_user/", tags=['user_registration'])
async def register_user(db: db_dependency,
                        profile_pic: UploadFile,
                        full_name: str = Form(...),
                        email: EmailStr = Form(...),
                        phone: str = Form(...),
                        password: str = Form(...)
                        ):
    if len(phone) != 10 or not phone.isdigit():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid phone number. Please enter a 10-digit numeric phone number.")
    
    existing_user = db.query(Users).filter(Users.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Insert the user data into PostgreSQL
    new_user = Users(
        fullname=full_name,
        email=email,
        Phone=phone,
        password=bcrypt_context.hash(password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Store the user's image in MongoDB as bytes
    image_data = await profile_pic.read()
    user_image_id = mongo_collection.insert_one({
        "user_id": new_user.id,
        "image": image_data
    }).inserted_id

    return {
        "user": new_user,
        "profile_pic": str(user_image_id)
    }

# Route to get user details by user ID
@app.get("/get_user_details/{user_id}", tags=['user_details'])
async def get_user_details(user_id: int, db: db_dependency):
    user = db.query(Users).filter(Users.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile_pic = mongo_collection.find_one({"user_id": user.id})
    if profile_pic is not None:
        profile_pic_id = str(profile_pic["_id"])
    else:
        profile_pic_id = None

    return {
        "user_id": user.id,
        "full_name": user.fullname,
        "email": user.email,
        "phone": user.Phone,
        "profile_picture_id": profile_pic_id
    }
