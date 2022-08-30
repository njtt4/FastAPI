from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles



app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]

@app.get("/")
@app.get("/home", response_class=HTMLResponse)
async def home(request:Request):
    return templates.TemplateResponse("home.html", {"request": request, "posts": posts})


@app.get("/about", response_class=HTMLResponse)
async def home(request:Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def home(request:Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def home(request:Request):
    return templates.TemplateResponse("register.html", {"request": request})




