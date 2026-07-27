# Leave Management System

A web-based **Leave Management System** developed using **Flask** and **SQLite** to streamline the leave application and approval process within an educational institution. The system enables faculty members to apply for leave online while allowing the Head of Department (HOD) to review, approve, or reject requests through a dedicated dashboard.

---

## Features

### Faculty Module
- Secure faculty login
- Apply for leave with reason and leave duration
- View leave application history
- Track leave request status (Pending, Approved, Rejected)

### HOD Module
- Secure HOD login
- View all leave requests
- Approve or reject leave applications
- Dashboard for monitoring leave records

### General Features
- User authentication
- Role-based access control
- Responsive user interface
- SQLite database integration
- Clean and simple dashboard

---

## Tech Stack

### Frontend
- HTML5
- CSS3
- Bootstrap
- JavaScript

### Backend
- Python
- Flask

### Database
- SQLite
- SQLAlchemy ORM

---

## Project Structure

```text
Leave_Management_System/
│
├── instance/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── faculty/
│   ├── hod/
│   ├── login.html
│   └── ...
│
├── __pycache__/
├── app.py
├── models.py
├── requirements.txt
├── README.md
└── .gitattributes
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/lalithkumar-07/Leave_Management_System.git
cd Leave_Management_System
```

### 2. Create a Virtual Environment

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

The application will be available at:

```
http://127.0.0.1:5000
```

---

## Database

The application uses **SQLite** as the backend database.

If running for the first time, the database will be created automatically (depending on your Flask configuration).

---

## Workflow

1. Faculty logs into the system.
2. Faculty submits a leave application.
3. Leave request is stored in the database.
4. HOD reviews pending applications.
5. HOD approves or rejects the request.
6. Faculty can monitor the application status from their dashboard.

---

## Screenshots

You can add screenshots of:

- Login Page
- Faculty Dashboard
- Leave Application Form
- HOD Dashboard
- Leave Approval Page

Example:

```
screenshots/
    login.png
    faculty_dashboard.png
    hod_dashboard.png
```

---

## Future Enhancements

- Email notifications
- Leave balance calculation
- Admin panel
- Multiple departments
- Calendar integration
- PDF leave reports
- Role management
- Analytics dashboard
- Export leave records to Excel/PDF

---

## Learning Outcomes

This project helped in understanding:

- Flask web development
- MVC architecture
- SQLAlchemy ORM
- Authentication and authorization
- CRUD operations
- Database design
- Session management
- Responsive web design

---

## Author

**Nanam Lalith Kumar Goud**

GitHub: https://github.com/lalithkumar-07

LinkedIn: *(Add your LinkedIn profile link here)*

---

## License

This project is developed for educational purposes.
