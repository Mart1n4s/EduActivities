from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.authentication import (AuthenticationBackend, AuthCredentials, BaseUser)
from views.auth import get_current_user
from views import auth, viewer, profile, organizer, admin
from contextlib import asynccontextmanager
from database import Database

@asynccontextmanager
async def lifespan(app: FastAPI):
    Database.connect_db()
    yield
    Database.close_db()

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
app.add_middleware(SessionMiddleware, secret_key="SECRET_KEY")

class User(BaseUser):
    def __init__(self, username: str, role: str) -> None:
        self.username = username
        self.role = role

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username

class JWTAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        try:
            user = await get_current_user(
                request.cookies.get("access_token")
            )
            return (
                AuthCredentials(["authenticated"]),
                User(user.username, user.role)
            )
        except Exception:
            return None


app.add_middleware(AuthenticationMiddleware, backend=JWTAuthBackend())

@app.get("/")
async def home(request: Request):
    if request.user.is_authenticated:
        user = await get_current_user(request.cookies.get("access_token"))
        if user.role == "viewer":
            return RedirectResponse(url="/viewer", status_code=303)
        elif user.role == "organizer":
            return RedirectResponse(url="/organizer", status_code=303)
        elif user.role == "admin":
            return RedirectResponse(url="/admin", status_code=303)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Home Page"}
    )

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(viewer.router, tags=["viewer"])
app.include_router(profile.router, tags=["profile"])
app.include_router(organizer.router, tags=["organizer"])
app.include_router(admin.router, tags=["admin"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
