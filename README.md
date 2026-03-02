# School Management System

A comprehensive **School Management System** built with Django, PostgreSQL, and modern web templates. Supports Role-Based Access Control (RBAC), JWT authentication, and a rich feature set for managing school operations.

---

## ✨ Features

### 👥 Student Management
- Add, Edit, Delete, and View students
- Bulk CSV upload & export
- ID Card generation (Front + Back) with barcode
- Class Promotion with history log
- Per-student sub-pages: Remarks, Documents, Contacts, Fee, Results

### 🏫 Academic
- Class & Section management
- Subject management (per class)
- Exam creation and subject-wise mark entry (marksheet grid)
- Class Academic Report (ranked) with Print support
- Individual Student Report Card
- Attendance Sessions, Mark Attendance, Attendance Analytics (Chart.js)
- Class Teacher Assignment & Dashboard
- Homework creation, student submission, and evaluation

### 💰 Finance
- Fee Types (CRUD)
- Payment Records
- Per-Student Fee summary
- Printable Fee Invoices & Receipts

### 📡 Online MCQ Exam
- Question Bank (with difficulty levels)
- Exam creation and question assignment
- Student exam-taking with countdown timer & auto-submit
- Result with answer review

### 📅 Routines & Calendar
- Class Routine (weekly timetable)
- Exam Routine (schedule)
- Year Calendar (FullCalendar.js, holiday/event management)

### 📩 SMS Notifications
- Log-only SMS system (ready for gateway integration)
- SMS History

### 📊 Analytics & Notifications
- Student Analytics Dashboard (Chart.js)
- Attendance Analytics Dashboard
- Bulk Notifications to class/status groups
- Real-time In-App Notifications (navbar dropdown)

### 👥 HR & Staff Management
- Teacher & Staff Profiles
- Leave Request Workflows (Apply & Approve)
- Payroll Generation & Printable Payslips

### ⚙️ School Settings
- Logo, Signature, Contact, Social Links, Leadership info

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Backend | Django 6.0 |
| API | Django REST Framework + SimpleJWT |
| Database | PostgreSQL |
| Frontend | HTML5, Bootstrap 5, Tabler Icons |
| Charts | Chart.js |
| Calendar | FullCalendar.js |
| Auth | JWT (SimpleJWT) + RBAC |
| Env | django-environ |
| Media | Pillow |

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- pip & virtualenv

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd schoolLanding Page
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux / macOS
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=school
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=127.0.0.1,localhost
```

### 5. Database Setup
```bash
# Create PostgreSQL database
createdb school  # or use pgAdmin

python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

---

## 🐳 Docker Setup

```bash
# Build and run with Docker Compose
docker compose up --build

# Run migrations inside container
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Visit: **http://localhost:8000**

---

## 📁 Project Structure

```
school/
├── core/               # Project settings, urls, wsgi
├── accounts/           # Custom User model, auth, RBAC
├── students/           # Students, Attendance, Fee, Exam, Results
├── online_exam/        # MCQ exam system
├── routines/           # Class & Exam routines, Year Calendar
├── sms/                # SMS notification log
├── templates/          # All HTML templates (per-app folders)
├── media/              # Uploaded files (logo, documents, etc.)
├── static/             # CSS, JS, images
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env
```

---

## 📄 License

MIT License. Free to use and modify.
