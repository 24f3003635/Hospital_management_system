from app.database import db
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("Patient", backref="user", uselist=False)
    doctor = db.relationship("Doctor", backref="user", uselist=False)


class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(20))
    age = db.Column(db.Integer)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(300))
    email = db.Column(db.String(200))

    appointments = db.relationship("Appointment", backref="patient", cascade="all, delete-orphan")
    records = db.relationship("MedicalRecord", backref="patient", cascade="all, delete-orphan")


class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    specialization = db.Column(db.String(200))
    availability = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(200))

    appointments = db.relationship("Appointment", backref="doctor", cascade="all, delete-orphan")
    records = db.relationship("MedicalRecord", backref="doctor", cascade="all, delete-orphan")


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)

    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    record = db.relationship("MedicalRecord", backref="appointment", uselist=False)


class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'

    id = db.Column(db.Integer, primary_key=True)

    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    diagnosis = db.Column(db.Text)
    treatment = db.Column(db.Text)
    prescription = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
