from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Ticket
import uuid

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Create DB tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Home page - Dashboard
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    tickets = db.query(Ticket).order_by(Ticket.id.desc()).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "tickets": tickets})

# Create ticket page
@app.get("/create", response_class=HTMLResponse)
def create_ticket_form(request: Request):
    return templates.TemplateResponse("create_ticket.html", {"request": request})

# Save new ticket
@app.post("/create")
def create_ticket(
    request: Request,
    customer_name: str = Form(...),
    email: str = Form(...),
    contact_name: str = Form(...),
    issue_title: str = Form(...),
    description: str = Form(...),
    status: str = Form(...),
    assigned_to: str = Form(...),
    priority: str = Form(...),
    category: str = Form(...),
    db: Session = Depends(get_db)
):
    ticket_id = str(uuid.uuid4())[:8]
    new_ticket = Ticket(
        ticket_id=ticket_id,
        customer_name=customer_name,
        email=email,
        contact_name=contact_name,
        issue_title=issue_title,
        description=description,
        status=status,
        assigned_to=assigned_to,
        priority=priority,
        category=category
    )
    db.add(new_ticket)
    db.commit()
    return RedirectResponse("/", status_code=303)

# Edit ticket form
@app.get("/edit/{ticket_id}", response_class=HTMLResponse)
def edit_ticket_form(ticket_id: str, request: Request, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    return templates.TemplateResponse("edit_ticket.html", {"request": request, "ticket": ticket})

# Save edited ticket
@app.post("/edit/{ticket_id}")
def edit_ticket(
    ticket_id: str,
    customer_name: str = Form(...),
    email: str = Form(...),
    contact_name: str = Form(...),
    issue_title: str = Form(...),
    description: str = Form(...),
    status: str = Form(...),
    assigned_to: str = Form(...),
    priority: str = Form(...),
    category: str = Form(...),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    ticket.customer_name = customer_name
    ticket.email = email
    ticket.contact_name = contact_name
    ticket.issue_title = issue_title
    ticket.description = description
    ticket.status = status
    ticket.assigned_to = assigned_to
    ticket.priority = priority
    ticket.category = category
    db.commit()
    return RedirectResponse("/", status_code=303)

# Delete ticket
@app.get("/delete/{ticket_id}")
def delete_ticket(ticket_id: str, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    db.delete(ticket)
    db.commit()
    return RedirectResponse("/", status_code=303)
