## Setup Instructions

### 1. Clone the repository

git clone https://github.com/rambodai04-ux/hit237-assessment2-group14.git
cd hit237-assessment2-group14

### 2. Create and activate virtual environment

python -m venv venv
source venv/bin/activate

### 3. Install dependencies

pip install -r requirements.txt

### 4. Run migrations

python manage.py migrate

### 5. Create superuser

python manage.py createsuperuser

### 6. Run the server

python manage.py runserver

### 7. Visit the app

- Frontend: http://127.0.0.1:8000/programs/
- Admin: http://127.0.0.1:8000/admin/

---

## Django Design Philosophies Applied

- DRY — Template inheritance via base.html
- Fat Models, Skinny Views — Business logic in model methods
- Loose Coupling — App-level URL configuration
- Explicit is better than implicit — Named URLs, clear model methods
- Batteries included — Django ORM, Admin, CSRF protection

---

## AI Tool Usage

This project used Claude (Anthropic) as an AI coding assistant. All generated code was reviewed and understood by the team. Chat history is available as evidence of responsible AI usage per CDU guidelines.

## REVIEW CONFIRMATION

Code and requirements reviewed by Manjil Bolakhe.
Tests Performed. Worked without any issues.