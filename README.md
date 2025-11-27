Hospital Management System

A full-stack web application designed to streamline hospital operations, including patient management, doctor scheduling, appointments, medical history tracking, and administrative controls.
This project uses Python, Flask, SQLite, HTML/CSS, and Bootstrap to create a simple yet functional management system.

📁 Project Directory Structure

Hospital-Management-System/
│
├── app/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── config.py
│   ├── controllers.py
│   ├── database.py
│   └── model.py
│
├── database/
│   └── project_db.sqlite3
│
├── database_directory/
│   └── project_db.sqlite3
│
├── static/
│   ├── bootstrap/
│   └── images/
│       ├── hms-home.jpg
│       └── hospital-bg.jpg
│
├── templates/
│   ├── admin_dashboard.html
│   ├── Create_doc.html
│   ├── Department.html
│   ├── doctor_availability.html
│   ├── doctor_dashboard.html
│   ├── doctor_detail.html
│   ├── edit_doctor.html
│   ├── edit_my_profile.html
│   ├── edit_patient.html
│   ├── home.html
│   ├── login.html
│   ├── Manage_appointments.html
│   ├── Manage_doctor.html
│   ├── Manage_patient.html
│   ├── new_appointment.html
│   ├── patient_book_doctor.html
│   ├── patient_dashboard.html
│   ├── patient_history.html
│   ├── search.html
│   ├── sign_up.html
│   └── update_patient_history.html
│
├── venv/
│
├── main.py
├── requirements.txt
└── README.md


🚀 Features

👨‍⚕️ Doctor Module
Doctor login
Manage availability
View booked appointments
Manage patient history
update/add medical record

🧑‍🤝‍🧑 Patient Module
Patient registration and login
Book appointment with doctor
View own history & prescriptions
Manage profile

🛠️ Admin Module
Add/Edit/Delete Doctors
Add/Edit/Delete Patients
Manage Departments
Monitor Appointments
Dashboard with system statistics

📅 Appointment System
Patients can book appointments
Doctors can view & approve appointments
Updating appointment status

💾 Database
Lightweight SQLite database
Separate directory for production and development DB
Model classes with controller logic

🏗️ Tech Stack

Backend
Python (Flask Framework)
SQLite Database

Frontend
HTML5 / CSS3
Bootstrap
Jinja2 Templating

Tools
VS Code
Virtual Environment
Flask CLI

⚙️ Installation & Setup

1️⃣ Clone the Repository
git clone <your-repository-url>
cd Hospital-Management-System

2️⃣ Create & Activate Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate   # Linux / Mac

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run the Application
python main.py

5️⃣ Open in Browser
http://127.0.0.1:5000