# Yaba Capital

## First-time setup

1. Create and activate a virtual environment:
   python3 -m venv venv
   source venv/bin/activate   (Mac/Linux)
   venv\Scripts\activate      (Windows)

2. Install dependencies:
   pip install -r requirements.txt

3. Copy .env.example to .env and fill in a real SECRET_KEY:
   cp .env.example .env
   (generate one with: python -c "import secrets; print(secrets.token_urlsafe(50))")

4. Run migrations:
   python manage.py migrate

5. Create an admin account (for the review dashboard at /admin/):
   python manage.py createsuperuser

6. Run the dev server:
   python manage.py runserver

7. Visit http://127.0.0.1:8000/
