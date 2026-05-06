# Qatar Foundation Admin Portal Backend

## Features

- Admin Signup
- Admin Login
- Remember Me Session
- Forgot Password Flow
- Create Opportunity
- Edit Opportunity
- Delete Opportunity
- View Opportunity Details
- SQLite Database
- Flask Login Authentication
- Session Management

---

## Project Structure

qatar_foundation_submission/
│
├── app.py
├── config.py
├── models.py
├── routes.py
├── requirements.txt
├── README.md
│
├── static/
├── templates/

---

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Environment

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Application

```bash
python app.py
```

Server:
```bash
http://127.0.0.1:5000
```

---

## API Routes

### Authentication

- POST /api/signup
- POST /api/login
- POST /api/logout
- POST /api/forgot-password

### Opportunities

- GET /api/opportunities
- POST /api/opportunities
- GET /api/opportunities/<id>
- PUT /api/opportunities/<id>
- DELETE /api/opportunities/<id>

---

## Notes

- No UI modifications required
- Connect provided frontend repository directly
- All opportunity data is stored in database
- Opportunities are isolated per admin account