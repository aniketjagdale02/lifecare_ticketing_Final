import os
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from database import SessionLocal, init_db, Ticket

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# ⏬ Use correct relative path for templates and static folders
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "app", "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "app", "static")), name="static")

# 🔄 Initialize database
init_db()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Login page
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

# ✅ Handle login form POST
@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "admin":
        request.session["user"] = username
        return RedirectResponse("/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

# ✅ Dashboard page
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db=Depends(get_db)):
    if not request.session.get("user"):
        return RedirectResponse("/", status_code=302)
    tickets = db.query(Ticket).all()
    return app/templates.TemplateResponse("dashboard_ticket.html", {"request": request, "tickets": tickets})

# ✅ Create Ticket
@app.get("/create", response_class=HTMLResponse)
def create_ticket_form(request: Request):
    if not request.session.get("user"):
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("create_ticket.html", {"request": request})

@app.post("/create")
def create_ticket(request: Request, title: str = Form(...), description: str = Form(...), db=Depends(get_db)):
    if not request.session.get("user"):
        return RedirectResponse("/", status_code=302)
    new_ticket = Ticket(title=title, description=description)
    db.add(new_ticket)
    db.commit()
    return RedirectResponse("/dashboard", status_code=302)

# ✅ Edit Ticket
@app.get("/edit/{ticket_id}", response_class=HTMLResponse)
def edit_ticket_form(request: Request, ticket_id: int, db=Depends(get_db)):
    if not request.session.get("user"):
        return RedirectResponse("/", status_code=302)
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    return templates.TemplateResponse("edit_ticket.html", {"request": request, "ticket": ticket})

@app.post("/edit/{ticket_id}")
def edit_ticket(request: Request, ticket_id: int, title: str = Form(...), description: str = Form(...), db=Depends(get_db)):
    if not request.session.get("user"):
        return RedirectResponse("/", status_code=302)
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    ticket.title = title
    ticket.description = description
    db.commit()
    return RedirectResponse("/dashboard", status_code=302)

# ✅ Delete Ticket
@app.get("/delete/{ticket_id}")
def delete_ticket(request: Request, ticket_id: int, db=Depends(get_db)):
    if not request.session.get("user"):
        return RedirectResponse("/", status_code=302)
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    db.delete(ticket)
    db.commit()
    return RedirectResponse("/dashboard", status_code=302)

# ✅ Logout
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)
