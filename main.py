from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import os

# App setup
app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Database setup
conn = sqlite3.connect("tickets.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    email TEXT,
    contact TEXT,
    issue_title TEXT,
    description TEXT,
    status TEXT,
    assigned_to TEXT,
    priority TEXT,
    category TEXT
)
''')
conn.commit()

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    cursor.execute("SELECT * FROM tickets")
    tickets = cursor.fetchall()
    return templates.TemplateResponse("dashboard.html", {"request": request, "tickets": tickets})

@app.get("/create", response_class=HTMLResponse)
def create_ticket(request: Request):
    return templates.TemplateResponse("create_ticket.html", {"request": request})

@app.post("/create", response_class=HTMLResponse)
async def create_ticket_post(
    request: Request,
    customer_name: str = Form(...),
    email: str = Form(...),
    contact: str = Form(...),
    issue_title: str = Form(...),
    description: str = Form(...),
    status: str = Form(...),
    assigned_to: str = Form(...),
    priority: str = Form(...),
    category: str = Form(...)
):
    cursor.execute('''
        INSERT INTO tickets (customer_name, email, contact, issue_title, description, status, assigned_to, priority, category)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (customer_name, email, contact, issue_title, description, status, assigned_to, priority, category))
    conn.commit()
    return RedirectResponse("/", status_code=302)

@app.get("/edit/{ticket_id}", response_class=HTMLResponse)
def edit_ticket(request: Request, ticket_id: int):
    cursor.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,))
    ticket = cursor.fetchone()
    return templates.TemplateResponse("edit_ticket.html", {"request": request, "ticket": ticket})

@app.post("/edit/{ticket_id}", response_class=HTMLResponse)
async def edit_ticket_post(
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
    category: str = Form(...)
):
    cursor.execute('''
        UPDATE tickets
        SET customer_name=?, email=?, contact=?, issue_title=?, description=?, status=?, assigned_to=?, priority=?, category=?
        WHERE id=?
    ''', (customer_name, email, contact, issue_title, description, status, assigned_to, priority, category, ticket_id))
    conn.commit()
    return RedirectResponse("/", status_code=302)

@app.get("/delete/{ticket_id}", response_class=HTMLResponse)
def delete_ticket(request: Request, ticket_id: int):
    cursor.execute("DELETE FROM tickets WHERE id=?", (ticket_id,))
    conn.commit()
    return RedirectResponse("/", status_code=302)
