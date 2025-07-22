from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Ticket
import models

# App & Template setup
app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Initialize DB
models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = next(get_db())):
    tickets = db.query(Ticket).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "tickets": tickets})

@app.get("/create", response_class=HTMLResponse)
def create_ticket(request: Request):
    return templates.TemplateResponse("create_ticket.html", {"request": request})

@app.post("/create", response_class=HTMLResponse)
def create_ticket_post(
    request: Request,
    customer_name: str = Form(...),
    email: str = Form(...),
    contact: str = Form(...),
    issue_title: str = Form(...),
    description: str = Form(...),
    status: str = Form(...),
    assigned_to: str = Form(...),
    priority: str = Form(...),
    category: str = Form(...),
    db: Session = next(get_db())
):
    ticket = Ticket(
        customer_name=customer_name,
        email=email,
        contact=contact,
        issue_title=issue_title,
        description=description,
        status=status,
        assigned_to=assigned_to,
        priority=priority,
        category=category
    )
    db.add(ticket)
    db.commit()
    return RedirectResponse("/", status_code=302)

@app.get("/edit/{ticket_id}", response_class=HTMLResponse)
def edit_ticket(request: Request, ticket_id: int, db: Session = next(get_db())):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    return templates.TemplateResponse("edit_ticket.html", {"request": request, "ticket": ticket})

@app.post("/edit/{ticket_id}", response_class=HTMLResponse)
def edit_ticket_post(
    request: Request,
    ticket_id: int,
    customer_name: str = Form(...),
    email: str = Form(...),
    contact: str = Form(...),
    issue_title: str = Form(...),
    description: str = Form(...),
    status: str = Form(...),
    assigned_to: str = Form(...),
    priority: str = Form(...),
    category: str = Form(...),
    db: Session = next(get_db())
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket:
        ticket.customer_name = customer_name
        ticket.email = email
        ticket.contact = contact
        ticket.issue_title = issue_title
        ticket.description = description
        ticket.status = status
        ticket.assigned_to = assigned_to
        ticket.priority = priority
        ticket.category = category
        db.commit()
    return RedirectResponse("/", status_code=302)

@app.get("/delete/{ticket_id}", response_class=HTMLResponse)
def delete_ticket(request: Request, ticket_id: int, db: Session = next(get_db())):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket:
        db.delete(ticket)
        db.commit()
    return RedirectResponse("/", status_code=302)
