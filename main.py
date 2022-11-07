from datetime import timedelta
from fastapi import FastAPI, Request, Depends, responses, Form, status, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from jose import jwt, JWTError

from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import HTTPBearer
import crud, models
from forms import RegistrationForm
from database import SessionLocal, engine
from utils import get_flashed_messages, flash
from services import (
    authenticate_user,
    oauth2_scheme,
    get_user,
    manager,
    create_access_token,
)
from schemas import (
    TokenData,
    Token,
    User,
    UserCreate,
)

SECRET_KEY = "25c7d867bbdde3b7c4c1f0207a139765362c3c0d0d366baf53acd507a73182cd"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 
ALGORITHM = "HS256"

oauth2_scheme = HTTPBearer()

middleware = [Middleware(SessionMiddleware, secret_key="SECRET_KEY")]

models.Base.metadata.create_all(bind=engine)

app = FastAPI(middleware=middleware)

# Dependency
def get_db():
    db = SessionLocal()
    yield db
    

app.mount("/static/", StaticFiles(directory="static",html=True), name="static")
templates = Jinja2Templates(directory="templates")
templates.env.globals['get_flashed_messages'] = get_flashed_messages


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user( db=db , username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.get("/", response_class=HTMLResponse)
@app.get("/home", response_class=HTMLResponse)
async def home(
    request:Request,
):
    return templates.TemplateResponse("home.html", {"request":request})


@app.get("/about", response_class=HTMLResponse)
async def about(request:Request):
    return templates.TemplateResponse("about.html", {"request":request})


@app.get("/register", response_class=HTMLResponse)
def register(request:Request):
    return templates.TemplateResponse("/register.html", {"request":request})


@app.post("/register")
async def register(
    request: Request,  
    db: Session = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):

    form = RegistrationForm(request)
    form.username = username
    form.password = password
    form.confirm_password = confirm_password

    if await form.is_valid():
        user = crud.get_user_by_email(email=form.username, db=db)
        if user:
            form.__dict__.get("errors").append("Email already exists")
            return templates.TemplateResponse("/register.html", form.__dict__)
        else:
            user_schema = UserCreate(
                email= form.username, password=form.password
            )
            await crud.create_user(db, user_schema)
            flash(request, "Registration Successful!", "success")
            return templates.TemplateResponse("/register.html", {"request": request})
    return templates.TemplateResponse("/register.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
def login(request:Request):
    return templates.TemplateResponse("/login.html", {"request":request})


@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request, 
    db: Session = Depends(get_db),
    oauth2_scheme = Depends(oauth2_scheme),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = authenticate_user(form_data.username, form_data.password, db)


    if user:

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = manager.create_access_token(
            data = {"sub": user.username}, expires=access_token_expires
        )
        resp = responses.RedirectResponse(
            "/home", status_code=status.HTTP_302_FOUND
        )
        manager.set_cookie(resp, access_token)
        return resp
    else:
        flash(
            request, 
            "Login Unsuccessful. Please check your username and password",
            "danger",
        )
        return templates.TemplateResponse("/login.html", {"request": request})


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)):

    user = authenticate_user(form_data.username, form_data.password,db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


