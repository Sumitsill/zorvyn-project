# Finance Dashboard & Access Control Backend 🚀

A full-stack financial data processing application featuring a robust, secure REST API, Role-Based Access Control (RBAC), and analytics functionalities. Built with **Python, FastAPI, and SQLite**.

## 📖 Table of Contents
- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Project Structure & Architecture](#-project-structure--architecture)
- [API Documentation & Testing](#-api-documentation--testing)
- [Test Credentials](#-test-credentials)

---

## 🌟 Project Overview
This project is built to demonstrate production-ready API design principles. It provides highly secure authentication using JWTs, strictly enforces data relationships via SQLAlchemy ORM, and separates administrative data processing from standard viewing privileges through advanced Role-Based Access Control limits.

## ✨ Key Features
- **Stateless JWT Authentication:** Secure login mechanism utilizing bcrypt for password hashing.
- **Role-Based Access Control (RBAC):** Three distinct roles (`admin`, `analyst`, and `viewer`) restricting access across API endpoints.
- **Financial Record Operations:** Full CRUD operations on transaction logs, categorized implicitly for analytics.
- **Dashboard Analytics:** High-level APIs for dashboard summaries (Total Revenue, Total Expenses) along with historical trends analysis over specified date ranges.
- **Seamless Static File Serving:** Serves frontend HTML directly through FastAPI, keeping the architecture unified for simple deployments without CORS complexity.

## 🛠 Tech Stack

**Backend (Python)**
- **Framework:** FastAPI (Python 3.10+)
- **Database / ORM:** SQLite / SQLAlchemy
- **Data Validation:** Pydantic
- **Security & Auth:** `passlib` (bcrypt password hashing), `python-jose` (Stateless JSON Web Tokens)
- **Deployment Server:** Uvicorn

**Frontend (UI/UX)**
- **Architecture:** Single Page Application (SPA), dynamically served by FastAPI.
- **Styling:** Vanilla CSS with modern Glassmorphism aesthetics (Backdrop filters, CSS custom properties).
- **Interactivity:** Vanilla JavaScript (ES6+), Fetch API for async secure JSON consumption.

---

## 🚀 Getting Started

Follow these steps to set up and run the application locally on your machine.

### Prerequisites
- **Python 3.10+**
- Git

### 1. Clone & Setup
Clone the repository, verify you are in the project folder, and then install the required dependencies:
```bash
# Strongly recommended to create a virtual environment first:
python -m venv venv
# Activate the virtual env:
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
```

### 2. Database Initialization & Seeding
Instead of manual testing, a robust seed script is provided. It configures the SQLite database and populates it with users, roles, and dummy financial records.
```bash
python seed.py
```

### 3. Start the Development Server
Launch the API using Uvicorn:
```bash
uvicorn main:app --reload
```
The server will start running at: `http://localhost:8000`

---

## 📄 API Documentation & Testing (Live URL)

FastAPI automatically generates interactive OpenAPI documentation. You can test all endpoints, authenticate, and analyze responses straight from your browser.

**👉 Open the Interactive API Docs (Swagger UI):**
[http://localhost:8000/docs](http://localhost:8000/docs)

*(Note: To test endpoints requiring authorization, use the `Authorize` button at the top right of the Swagger UI with one of the test credentials below.)*

---

## 🔑 Test Credentials

The database script (`seed.py`) automatically generates the following user roles for testing out the RBAC functionality:

| Role Type      | Email                 | Password     | Capabilities                               |
|----------------|-----------------------|--------------|--------------------------------------------|
| **Admin**      | `admin@example.com`   | `admin123`   | Full CRUD setup, all financial tools       |
| **Analyst**    | `analyst@example.com` | `analyst123` | View records, analyze aggregated summaries |
| **Viewer**     | `viewer@example.com`  | `viewer123`  | Limited read-only access                   |

---

## 🧠 Design Decisions & Trade-offs
1. **Architecture Model:** Tightly segregated REST API ensuring that the frontend can be scaled out via any modern Javascript framework decoupled from the server logic.
2. **Database:** Chosen SQLite for initial rapid-prototyping and zero-friction reviewing for recruiters. Changing to a robust database like PostgreSQL for production environment takes merely updating the `SQLALCHEMY_DATABASE_URL`.
3. **Pydantic Validation:** Models handle strict input and output type-enforcement before logic touches the SQLite tables, mitigating internal server errors and SQL injections gracefully. 
