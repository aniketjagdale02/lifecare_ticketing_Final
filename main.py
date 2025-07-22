from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import asc
from database import SessionLocal, engine
from models import Base, Ticket
import uuid

app = FastAPI()

# Mount static directory and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Create database tables
Base.metadata.create_all(bind=engine)


# Home/dashboard
@app.get("/", response_class=HTMLResponse)
def read_tickets(request: Request):
    db: Session = SessionLocal()
    tickets = db.query(Ticket).order_by(asc(Ticket.id)).all()
    db.close()
    return templates.TemplateResponse("dashboard.html", {"request": request, "tickets": tickets})


# Show create form
@app.get("/create", response_class=HTMLResponse)
def create_ticket_form(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


# Create ticket
@app.post("/create")
async def create_ticket(
    request: Request,
    customer_name: str = Form(...),
    email_id: str = Form(...),
    contact_name: str = Form(...),
    issue_title: str = Form(...),
    description: str = Form(...),
    status: str = Form(...),
    assigned_to: str = Form(...),
    priority: str = Form(...),
    category: str = Form(...)
):
    db: Session = SessionLocal()
    ticket = Ticket(
        ticket_id=str(uuid.uuid4())[:8],
        customer_name=customer_name,
        email_id=email_id,
        contact_name=contact_name,
        title=issue_title,
        description=description,
        status=status,
        assigned_to=assigned_to,
        priority=priority,
        category=category
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    db.close()
    return RedirectResponse("/", status_code=302)


# Edit ticket form
@app.get("/edit/{ticket_id}", response_class=HTMLResponse)
def edit_ticket_form(request: Request, ticket_id: str):
    db: Session = SessionLocal()
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    db.close()
    return templates.TemplateResponse("edit.html", {"request": request, "ticket": ticket})


# Update ticket
@app.post("/edit/{ticket_id}")
async def update_ticket(
    request: Request,
    ticket_id: str,
    customer_name: str = Form(...),
    email_id: str = Form(...),
    contact_name: str = Form(...),
    issue_title: str = Form(...),
    description: str = Form(...),
    status: str = Form(...),
    assigned_to: str = Form(...),
    priority: str = Form(...),
    category: str = Form(...)
):
    db: Session = SessionLocal()
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if ticket:
        ticket.customer_name = customer_name
        ticket.email_id = email_id
        ticket.contact_name = contact_name
        ticket.title = issue_title
        ticket.description = description
        ticket.status = status
        ticket.assigned_to = assigned_to
        ticket.priority = priority
        ticket.category = category
        db.commit()
        db.refresh(ticket)
    db.close()
    return RedirectResponse("/", status_code=302)


# Delete ticket
@app.get("/delete/{ticket_id}")
def delete_ticket(ticket_id: str):
    db: Session = SessionLocal()
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if ticket:
        db.delete(ticket)
        db.commit()
    db.close()
    return RedirectResponse("/", status_code=302)
