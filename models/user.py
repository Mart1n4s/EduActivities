from pydantic import BaseModel
from typing import Optional


class AuthUser(BaseModel):
    username: str
    name: str
    surname: str
    email: str
    telephone_number: str
    role: str
    hashed_password: str

class UserCreateData(BaseModel):
    username: str
    name: str
    surname: str
    email: str
    telephone_number: str
    password: str
    role: str

class UserUpdateData(BaseModel):
    username: str
    name: str
    surname: str
    email: str
    telephone_number: str
    password: Optional[str] = None
    role: str 

class ProfileUpdateData(BaseModel):
    name: str
    surname: str
    email: str
    telephone_number: str

class LoginData(BaseModel):
    username: str
    password: str

class RegisterData(BaseModel):
    username: str
    name: str
    surname: str
    email: str
    telephone_number: str
    password: str
    confirm_password: str
    role: str