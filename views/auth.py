from fastapi import APIRouter, Request, HTTPException, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi.responses import RedirectResponse
from database import Database
from models.user import AuthUser, LoginData, RegisterData
import bcrypt
from pydantic import BaseModel
from utils.validators import (ERROR_MESSAGES, create_error_response, create_success_response, validate_user_data)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

SECRET_KEY = "SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

@router.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "Register"})


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_user(username: str) -> Optional[AuthUser]:
    user_dict = await Database.get_user_by_username(username)
    if user_dict:
        user_dict = dict(user_dict)
        user_dict["_id"] = str(user_dict["_id"])
        return AuthUser(**user_dict)
    return None

async def authenticate_user(username: str, password: str) -> Optional[AuthUser]:
    user = await get_user(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(access_token: str = Cookie(None, alias="access_token")) -> AuthUser:
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail=ERROR_MESSAGES["not_authenticated"],
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if access_token.startswith('Bearer '):
        access_token = access_token[7:]
    
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=401,
                detail=ERROR_MESSAGES["invalid_credentials"],
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail=ERROR_MESSAGES["invalid_credentials"],
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await get_user(username)
    if not user:
        raise HTTPException(
            status_code=401,
            detail=ERROR_MESSAGES["user_not_found"],
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post("/login")
async def login_for_access_token(login_data: LoginData):
    if not login_data.username or not login_data.password:
        return create_error_response(ERROR_MESSAGES["empty_field"], 400)

    user = await authenticate_user(login_data.username, login_data.password)
    if not user:
        return create_error_response(ERROR_MESSAGES["invalid_credentials"], 401)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    redirect_url = "/viewer" if user.role == "viewer" else "/organizer" if user.role == "organizer" else "/admin"
    response = create_success_response("Login successful", 200)
    response.headers["X-Redirect-URL"] = redirect_url
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return response

@router.post("/register")
async def register(register_data: RegisterData):
    validation_error = validate_user_data(
        register_data.username,
        register_data.name,
        register_data.surname,
        register_data.email,
        register_data.telephone_number,
        register_data.password,
        register_data.role,
        is_update=False,
        confirm_password=register_data.confirm_password
    )
    if validation_error:
        return validation_error
    
    user_data = {
        "username": register_data.username,
        "name": register_data.name,
        "surname": register_data.surname,
        "email": register_data.email,
        "telephone_number": register_data.telephone_number,
        "role": register_data.role,
        "hashed_password": get_password_hash(register_data.password)
    }
    
    if not Database.create_user(user_data):
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    return create_success_response("Registration successful")

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    return response

