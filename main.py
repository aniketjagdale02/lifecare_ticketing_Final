import os
from fastapi import FastAPI, Form, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.database import SessionLocal, init_db, Ticket

# Set base path to current directory (app/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


# Initialize database
init_db()

# Simple credentials (you can change this later)
VALID_USERNAME = "admin"
VALID_PASSWORD = "admin123"

@app.get("/")
async def root():
    return RedirectResponse(url="/login")

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == VALID_USERNAME and password == VALID_PASSWORD:
        request.session["user"] = username
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/dashboard")
def dashboard(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@app.post("/create_ticket")
def create_ticket(title: str = Form(...), description: str = Form(...), db: SessionLocal = Depends(lambda: SessionLocal())):
    ticket = Ticket(title=title, description=description)
    db.add(ticket)
    db.commit()
    return {"message": "Ticket created"}
