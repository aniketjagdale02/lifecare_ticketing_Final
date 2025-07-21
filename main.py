from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uuid import uuid4

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# In-memory ticket store (can be replaced with database)
TICKETS = {}

@app.get("/")
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "tickets": list(TICKETS.values())})

@app.get("/create")
def create_ticket_form(request: Request):
    return templates.TemplateResponse("create_ticket.html", {"request": request})

@app.post("/create")
def create_ticket(
    request: Request,
    customer_name: str = Form(...),
    email_id: str = Form(...),
    contact_number: str = Form(...),
    issue_title: str = Form(...),
    description: str = Form(...),
    status: str = Form(...),
    assigned_to: str = Form(...),
    priority: str = Form(...),
    category: str = Form(...)
):
    ticket_id = str(uuid4())[:8]
    TICKETS[ticket_id] = {
        "ticket_id": ticket_id,
        "customer_name": customer_name,
        "email_id": email_id,
        "contact_number": contact_number,
        "issue_title": issue_title,
        "description": description,
        "status": status,
        "assigned_to": assigned_to,
        "priority": priority,
        "category": category
    }
    return RedirectResponse("/", status_code=303)

@app.get("/edit/{ticket_id}")
def edit_ticket_form(request: Request, ticket_id: str):
    ticket = TICKETS.get(ticket_id)
    return templates.TemplateResponse("edit_ticket.html", {"request": request, "ticket": ticket})

@app.post("/edit/{ticket_id}")
def edit_ticket(
    request: Request,
    ticket_id: str,
    customer_name: str = Form(...),
    email_id: str = Form(...),
    contact_number: str = Form(...),
    issue_title: str = Form(...),
    description: str = Form(...),
    status: str = Form(...),
    assigned_to: str = Form(...),
    priority: str = Form(...),
    category: str = Form(...)
):
    if ticket_id in TICKETS:
        TICKETS[ticket_id] = {
            "ticket_id": ticket_id,
            "customer_name": customer_name,
            "email_id": email_id,
            "contact_number": contact_number,
            "issue_title": issue_title,
            "description": description,
            "status": status,
            "assigned_to": assigned_to,
            "priority": priority,
            "category": category
        }
    return RedirectResponse("/", status_code=303)

@app.get("/delete/{ticket_id}")
def delete_ticket(ticket_id: str):
    TICKETS.pop(ticket_id, None)
    return RedirectResponse("/", status_code=303)
