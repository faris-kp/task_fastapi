from fastapi import FastAPI,HTTPException,Depends,status,UploadFile,Form
from pymongo import MongoClient
import models
from database import engine,SessionLocal
from sqlalchemy.orm import Session
from models import Users
from passlib.context import CryptContext
from typing import Annotated
from pydantic import EmailStr


app = FastAPI()

models.Base.metadata.create_all(bind=engine)




mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["sample"]
mongo_collection = mongo_db["user_profile"]


SECRET_KEY = "eyJhbGciOIsInR5cCIiwiI6IkpXVCJ9eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9TJVA95OrM7E2cBab30RMHrHD"
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated = 'auto')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]
    
@app.post("/register_user/",tags=['user_registration'])
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
    print("enterd")
    new_user = Users(
        fullname=full_name,
        email=email,
        Phone=phone,
        password=bcrypt_context.hash(password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    image_data = await profile_pic.read()
# Store the user's image in MongoDB as bytes
    user_image_id = mongo_collection.insert_one({
    "user_id": new_user.id,
    "image": image_data
      }).inserted_id

    # Store the user's image in MongoDB and associate it with the user's ID
    
    print("id",new_user.id)

    print("id cheking",user_image_id)
    
    return {
        "user":new_user,
        "profile_pic":str(user_image_id)
    }
   
    # return { 
    #     "id": new_user.id,
    #     "fullname": new_user.fullname,
    #     "email": new_user.email,
    #     "phone": new_user.Phone,
    #     "password":new_user.password,
    #     "profile_picture_path": str(user_image_id)
    # }
    




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

    



    
    
    
    


