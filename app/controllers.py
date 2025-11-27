from flask import render_template, request, url_for, redirect, flash,jsonify
from sqlalchemy import or_, distinct
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import db
from sqlalchemy import select
from app.model import User, Patient, Doctor, Appointment, MedicalRecord 
from datetime import datetime, date,timedelta
import sys

login_manager = LoginManager()
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_default_admin():
    try:
        admin_username = "admin@gmail.com"
        admin_password = "admin_123"

        admin_user = User.query.filter_by(username=admin_username).first()

        if not admin_user:
            hashed_password = generate_password_hash(admin_password, method="pbkdf2:sha256")
            
            new_admin = User(username=admin_username, password=hashed_password, role="admin")
            db.session.add(new_admin)
            db.session.commit()
            print(f"Default admin user '{admin_username}' created.")
        else:
            print(f"Admin user '{admin_username}' already exists.")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        print(f"Error type: {type(e)}")

def init_routes(app):
    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route('/register', methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            try:
                print("Registration form submitted!") 
                print(f"Form data: {request.form}") 
                
                username = request.form.get("username")
                password = request.form.get("password")
                name = request.form.get("name")
                gender = request.form.get("gender")
                age = request.form.get("age")
                phone = request.form.get("phone")
                address = request.form.get("address")
                email = request.form.get("email")

                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    flash('Username already taken!', 'danger')
                    return render_template("sign_up.html")

                existing_email = Patient.query.filter_by(email=email).first()
                if existing_email:
                    flash('Email already registered!', 'danger')
                    return render_template("sign_up.html")

                hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
                new_user = User(username=username, password=hashed_password, role="patient")
                db.session.add(new_user)
                db.session.flush() 
                print(f"New user created with ID: {new_user.id}") 

                new_patient = Patient(
                    user_id=new_user.id,
                    name=name,
                    gender=gender,
                    age=age,
                    phone=phone,
                    address=address,
                    email=email
                )
                db.session.add(new_patient)
                db.session.commit()
                
                print("Registration successful!") 
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for("login"))
            
            except Exception as e:
                db.session.rollback()
                print(f"Registration error: {e}") 
                flash(f'Registration failed: {str(e)}', 'danger')
                return render_template("sign_up.html")
    
        return render_template("sign_up.html")

   
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
        
            print(f"Login attempt - Username: {username}, Password: {password}") 
        
            user = User.query.filter_by(username=username).first()

            if user:
                print(f"User found - ID: {user.id}, Role: {user.role}")
            
                if check_password_hash(user.password, password):
                    print("✓ Password matches!") 
                    login_user(user)
                    if user.role == "admin":
                        print("Redirecting to admin dashboard") 
                        return redirect(url_for("admin_dashboard"))
                    elif user.role == "doctor":
                        return redirect(url_for("doctor_dashboard"))
                    else:
                        return redirect(url_for("patient_dashboard"))
                else:
                    print("✗ Password does not match!") 
                    flash("Invalid username or password", "danger")
            else:
                print(f"✗ No user found with username: {username}") 
                flash("Invalid username or password", "danger")
            
            return render_template("login.html")
    
        return render_template("login.html")

    @app.route("/patient_dashboard")
    @login_required
    def patient_dashboard():
        if current_user.role != 'patient':
            return redirect(url_for('home'))

        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            flash('Patient profile not found!', 'danger')
            return redirect(url_for('home'))
   
        dept_tuples = db.session.query(distinct(Doctor.specialization)).all()
        departments = [dept[0] for dept in dept_tuples]  
    

        appointments = db.session.query(
            Appointment.id,
            Doctor.name.label('doctor_name'),
            Doctor.specialization.label('department'),
            Appointment.date,
            Appointment.time,
            Appointment.status
        ).join(Doctor).filter(Appointment.patient_id == patient.id).all()

        current_date = date.today().isoformat()
    
        return render_template("patient_dashboard.html", 
                         username=current_user.username, 
                         id=patient.id,
                         departments=departments,
                         appointments=appointments,
                         current_date=current_date)
    
 
    @app.route("/doctor_dashboard")
    @login_required
    def doctor_dashboard():
        if current_user.role != 'doctor':
            return redirect(url_for('home'))
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if not doctor:
            return redirect(url_for('home'))
        appointments = db.session.query(
            Appointment.id,
            Patient.name,
            Appointment.patient_id,
            Doctor.name, 
            Doctor.specialization,
            Appointment.date,
            Appointment.time,
            Appointment.status,
            ).join(Patient).join(Doctor).filter(Doctor.id == doctor.id).all()
        print(appointments)

        return render_template("doctor_dashboard.html", appointments=appointments, id=doctor.id)


    @app.route("/admin_dashboard")
    @login_required
    def admin_dashboard():
        if current_user.role != 'admin':
            return redirect(url_for('home'))
        doctor_count = Doctor.query.count()
        patient_count = Patient.query.count()
        appointment_count = Appointment.query.count()
        return render_template("admin_dashboard.html", username=current_user.username, dc=doctor_count,pc=patient_count,ac=appointment_count )

    
    @app.route("/manage_doctor")
    @login_required
    def manage_doctor():
        doctors = db.session.execute(select(Doctor.id, Doctor.name, Doctor.specialization)).all()
        return render_template("Manage_doctor.html", doctors=doctors)
    
    @app.route("/create_doc", methods=["GET", "POST"])
    @login_required
    def create_doc():
        if request.method == "POST":
            try:
                print("Registration form submitted!") 
                print(f"Form data: {request.form}") 
                
                username = request.form.get("username")
                password = request.form.get("password")
                name = request.form.get("name")
                specialization = request.form.get("specialization")
                experience = request.form.get("experience")
                email = request.form.get("email")

                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    flash('Username already taken!', 'danger')
                    return render_template("Create_doc.html")

                existing_email = Doctor.query.filter_by(email=email).first()
                if existing_email:
                    flash('Email already registered!', 'danger')
                    return render_template("Create_doc.html")

                hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
                new_user = User(username=username, password=hashed_password, role="doctor")
                db.session.add(new_user)
                db.session.flush() 
                print(f"New user created with ID: {new_user.id}") 

                new_doctor = Doctor(
                    user_id=new_user.id,
                    name=name,
                    specialization=specialization,
                    experience=experience,
                    email=email
                )
                db.session.add(new_doctor)
                db.session.commit()
                
                print("Registration successful!") 
                flash('Registration successful! ', 'success')
                return redirect(url_for("admin_dashboard"))
            
            except Exception as e:
                db.session.rollback()
                print(f"Registration error: {e}") 
                flash(f'Registration failed: {str(e)}', 'danger')
                return render_template("Create_doc.html")
    
        return render_template("Create_doc.html")

    @app.route("/edit_doctor/<int:id>", methods=["GET", "POST"])
    @login_required
    def edit_doctor(id):
        doctor = Doctor.query.get_or_404(id)
    
        if request.method == "POST":
            try:
             
                username = request.form.get("username")
                password = request.form.get("password")
                name = request.form.get("name")
                specialization = request.form.get("specialization")
                experience = request.form.get("experience")
                email = request.form.get("email")
                availability = request.form.get("availability")
            
                if not all([name, specialization, experience, email]):
                    flash('All required fields must be filled!', 'danger')
                    return render_template("edit_doctor.html", doctor=doctor)
            

                existing_email = Doctor.query.filter(Doctor.email == email, Doctor.id != id).first()
                if existing_email:
                    flash('Email already registered to another doctor!', 'danger')
                    return render_template("edit_doctor.html", doctor=doctor)
            

                doctor.name = name
                doctor.specialization = specialization
                doctor.experience = int(experience)
                doctor.email = email
                doctor.availability = availability
            
               
                if doctor.user:
                    existing_username = User.query.filter(User.username == username, User.id != doctor.user.id).first()
                    if existing_username:
                        flash('Username already taken!', 'danger')
                        return render_template("edit_doctor.html", doctor=doctor)
                
                    doctor.user.username = username
                

                    if password:
                        doctor.user.password = generate_password_hash(password, method="pbkdf2:sha256")
            
                db.session.commit()
                flash('Doctor information updated successfully!', 'success')
                return redirect(url_for("manage_doctor"))
        
            except Exception as e:
                db.session.rollback()
                print(f"Update error: {e}")
                flash(f'Update failed: {str(e)}', 'danger')
                return render_template("edit_doctor.html", doctor=doctor)
    
        return render_template("edit_doctor.html", doctor=doctor)
    
    
    @app.route("/delete_doctor/<int:id>",methods=["GET", "POST"])
    @login_required
    def delete_doctor(id):
        if current_user.role != 'admin':
            flash('You are not authorized to delete doctors!', 'danger')
            return redirect(url_for('manage_doctor'))
    
        try:
            doctor = Doctor.query.get_or_404(id)
                
            user_id = doctor.user_id
            db.session.delete(doctor)

            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
        
            db.session.commit()
            flash('Doctor deleted successfully!', 'success')
        
        except Exception as e:
            db.session.rollback()
            print(f"Delete error: {e}")
            flash(f'Delete failed: {str(e)}', 'danger')
    
        return redirect(url_for('manage_doctor'))

    @app.route("/manage_patient")
    @login_required
    def manage_patient():
        patients = db.session.execute(select(Patient.id, Patient.name, Patient.gender)).all()
        return render_template("Manage_patient.html", patients=patients)
    
    @app.route("/edit_patient/<int:id>", methods=["GET", "POST"])
    @login_required
    def edit_patient(id):
        patient = Patient.query.get_or_404(id)
    
        if request.method == "POST":
            try:
             
                username = request.form.get("username")
                password = request.form.get("password")
                name = request.form.get("name")
                phone = request.form.get("phone")
                age = request.form.get("age")
                email = request.form.get("email")
                gender = request.form.get("gender")
                address = request.form.get("address")
            
                if not all([name, phone, age, email,gender,address]):
                    flash('All required fields must be filled!', 'danger')
                    return render_template("edit_patient.html", patient=patient)
            

                existing_email = Patient.query.filter(Patient.email == email, Patient.id != id).first()
                if existing_email:
                    flash('Email already registered to another patient!', 'danger')
                    return render_template("edit_patient.html", patient=patient)
            

                patient.name = name
                patient.phone = phone
                patient.age = int(age)
                patient.email = email
                patient.gender = gender
                patient.address=address
            
               
                if patient.user:
                    existing_username = User.query.filter(User.username == username, User.id != patient.user.id).first()
                    if existing_username:
                        flash('Username already taken!', 'danger')
                        return render_template("edit_patient.html", patient=patient)
                
                    patient.user.username = username
                

                    if password:
                        patient.user.password = generate_password_hash(password, method="pbkdf2:sha256")
            
                db.session.commit()
                flash('Patient information updated successfully!', 'success')
                return redirect(url_for("manage_patient"))
        
            except Exception as e:
                db.session.rollback()
                print(f"Update error: {e}")
                flash(f'Update failed: {str(e)}', 'danger')
                return render_template("edit_patient.html", patient=patient)
    
        return render_template("edit_patient.html", patient=patient)
    
    @app.route("/delete_patient/<int:id>",methods=["GET", "POST"])
    @login_required
    def delete_patient(id):
        if current_user.role != 'admin':
            flash('You are not authorized to delete patients!', 'danger')
            return redirect(url_for('manage_patient'))
    
        try:
            patient = Patient.query.get_or_404(id)
                
            user_id = patient.user_id
            db.session.delete(patient)

            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
        
            db.session.commit()
            flash('Patient deleted successfully!', 'success')
        
        except Exception as e:
            db.session.rollback()
            print(f"Delete error: {e}")
            flash(f'Delete failed: {str(e)}', 'danger')
    
        return redirect(url_for('manage_patient'))

    

    @app.route("/manage_appointment")
    @login_required
    def manage_appointment():
        appointments = db.session.query(
            Appointment.id,
            Patient.name,
            Appointment.patient_id,
            Doctor.name, 
            Doctor.specialization,
            Appointment.date,
            Appointment.time,
            Appointment.status
            ).join(Patient).join(Doctor).all()
        
        current_date = date.today().isoformat()
        return render_template("Manage_appointments.html", appointments=appointments, current_date=current_date )
    
    @app.route("/search",methods=["GET", "POST"])
    @login_required
    def search():
        query = request.args.get("query", "").strip()

        if not query:
            flash("Please enter a search term.", "warning")
            return redirect(request.referrer or url_for("home"))
    
        search_terms = query.split()
    
        base_query = Doctor.query
        conditions = []
        for term in search_terms:
            term_condition = or_(Doctor.name.ilike(f"%{term}%"),Doctor.specialization.ilike(f"%{term}%"))
            conditions.append(term_condition)
    
        if conditions:
            base_query = base_query.filter(*conditions)
        results = base_query.all()
    
        if not results:
            flash(f"No doctors found for '{query}'. Try different keywords.", "info")
    
        return render_template("search.html", query=query, results=results)

    
    @app.route("/patient_history/<int:id>", methods=["GET", "POST"])
    @login_required
    def patient_history(id):
        medical_history = db.session.query(
        MedicalRecord.appointment_id,
        MedicalRecord.diagnosis,
        MedicalRecord.treatment,
        MedicalRecord.prescription,
        MedicalRecord.notes,
        Patient.name,
        Doctor.name,
        Doctor.specialization,
        ).join(Doctor).join(Patient).filter(MedicalRecord.patient_id == id).all()


        return render_template("patient_history.html", medical_history=medical_history)
    
    @app.route("/doctor/<int:id>")
    @login_required
    def doctor_detail(id):
        doctor = Doctor.query.get_or_404(id)
        return render_template("doctor_detail.html", doctor=doctor)

    @app.route("/doctor_action/<string:action>/<int:id>",methods=["GET", "POST"])
    @login_required
    def doctor_action(action,id):
        appointment = Appointment.query.get(id)
        if not appointment:
            return redirect(url_for('doctor_dashboard'))
        if action =='completed':
            appointment.status='completed'
        elif action =='cancel':
            appointment.status='cancel'
        db.session.commit()
        return redirect(url_for('doctor_dashboard'))
        

    @app.route("/update_patient_history/<int:appointment_id>", methods=["GET", "POST"])
    @login_required
    def update_patient_history(appointment_id):
    
        appointment = Appointment.query.get_or_404(appointment_id)
        patient = Patient.query.get(appointment.patient_id)
        doctor = Doctor.query.get(appointment.doctor_id)
    
   
        medical_record = MedicalRecord.query.filter_by(appointment_id=appointment_id).first()
    
        if request.method == "POST":
            if not medical_record:

                medical_record = MedicalRecord(
                    appointment_id=appointment_id,
                    patient_id=appointment.patient_id,
                    doctor_id=appointment.doctor_id,
                    diagnosis=request.form.get('diagnosis'),
                    treatment=request.form.get('treatment'),
                    prescription=request.form.get('prescription'),
                    notes=request.form.get('notes')
                    )
                db.session.add(medical_record)
            else:

                medical_record.diagnosis = request.form.get('diagnosis')
                medical_record.treatment = request.form.get('treatment')
                medical_record.prescription = request.form.get('prescription')
                medical_record.notes = request.form.get('notes')
        
            db.session.commit()
            flash('Patient history updated successfully!', 'success')
            return redirect(url_for('doctor_dashboard'))
    
        return render_template("update_patient_history.html",
                         appointment=appointment,
                         patient=patient,
                         doctor=doctor,
                         medical_record=medical_record)
    
  
    @app.route("/doctor/<int:id>/availability")
    def doctor_availability(id):
        doctor = Doctor.query.get_or_404(id)
    
  
        today = datetime.now().date()
        next_7_days = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    
        availability_data = slicing_availability_string(doctor.availability)
    
 
        current_availability = {}
        for date_str, slots in availability_data.items():
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_obj >= today:
                current_availability[date_str] = slots

        doctor.availability = create_availability_string(current_availability)
        db.session.commit()
    
        return render_template("doctor_availability.html", doctor=doctor, dates=next_7_days,availability_data=current_availability)

    @app.route("/update_slot", methods=["POST"])
    def update_slot():
        doctor_id = request.form.get("doctor_id")
        date = request.form.get("date")
        slot = request.form.get("slot")
        status = request.form.get("status")
    
        doctor = Doctor.query.get_or_404(doctor_id)
    

        availability_data = slicing_availability_string(doctor.availability)
    

        if date not in availability_data:
            availability_data[date] = []
    

        if status == "available" and slot not in availability_data[date]:
            availability_data[date].append(slot)
        elif status == "booked" and slot in availability_data[date]:
            availability_data[date].remove(slot)
    

        doctor.availability = create_availability_string(availability_data)
        db.session.commit()
    
        return jsonify({"success": True})

    def slicing_availability_string(availability_str):
        """Parse availability string into dictionary {date: [slots]}"""
        if not availability_str:
            return {}
    
        availability_data = {}
        try:
            entries = availability_str.split(';')
            for entry in entries:
                if ':' in entry:
                    date_part, slots_part = entry.split(':', 1)
                    slots = [s.strip() for s in slots_part.split(',')] if slots_part else []
                    availability_data[date_part.strip()] = slots
        except Exception as e:
            print(f"Error parsing availability string: {e}")
            return {}
    
        return availability_data

    def create_availability_string(availability_data):
        """Create availability string from dictionary {date: [slots]}"""
        if not availability_data:
            return ""
    
        entries = []
        for date, slots in sorted(availability_data.items()):
            if slots:  
                slots_str = ','.join(sorted(slots))
                entries.append(f"{date}:{slots_str}")
    
        return ';'.join(entries)

    
    @app.route("/departments/<string:dept_name>")
    @login_required
    def departments(dept_name):

        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            flash('Patient profile not found!', 'danger')
            return redirect(url_for('home'))
    
        doctors = db.session.query(Doctor.id, Doctor.name).filter(Doctor.specialization == dept_name).all()
    
        return render_template("Department.html", 
                         doctors=doctors, 
                         dept_name=dept_name, 
                         id=patient.id) 

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("home"))
    
    @app.route("/edit_my_profile", methods=["GET", "POST"])
    @login_required
    def edit_my_profile():
        if current_user.role != 'patient':
            flash('Access denied!', 'danger')
            return redirect(url_for('home'))
    
  
        patient = Patient.query.filter_by(user_id=current_user.id).first()
    
        if not patient:
            flash('Patient profile not found!', 'danger')
            return redirect(url_for('patient_dashboard'))
    
        if request.method == "POST":
            try:
         
                name = request.form.get("name")
                phone = request.form.get("phone")
                age = request.form.get("age")
                email = request.form.get("email")
                gender = request.form.get("gender")
                address = request.form.get("address")
            
  
                patient.name = name
                patient.phone = phone
                patient.age = int(age)
                patient.email = email
                patient.gender = gender
                patient.address = address
            
                db.session.commit()
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('patient_dashboard'))
            
            except Exception as e:
                db.session.rollback()
                flash(f'Update failed: {str(e)}', 'danger')
    
        return render_template("edit_my_profile.html", patient=patient)
    
    @app.route("/doctor/<int:doctor_id>/book")
    @login_required
    def book_doctor(doctor_id):
        if current_user.role != 'patient':
            return redirect(url_for('home'))

        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            flash('Patient profile not found!', 'danger')
            return redirect(url_for('home'))

        doctor = Doctor.query.get_or_404(doctor_id)
    

        today= datetime.now().date()
        next_7_days = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

        availability_data = slicing_availability_string(doctor.availability)

        current_availability = {}
        for date_str in next_7_days:
            current_availability[date_str] = availability_data.get(date_str, [])
    

        existing_appointment = Appointment.query.filter_by(
            patient_id=patient.id, 
            doctor_id=doctor_id,
            status='scheduled'
        ).first()
    
        has_existing_appointment = existing_appointment is not None
    
        return render_template("patient_book_doctor.html", 
                         doctor=doctor, 
                         patient=patient,
                         dates=next_7_days,
                         availability_data=current_availability,
                         has_existing_appointment=has_existing_appointment,
                         existing_appointment=existing_appointment)

    @app.route("/book_appointment", methods=["POST"])
    @login_required
    def book_appointment():
        if current_user.role != 'patient':
            return jsonify({"success": False, "error": "Unauthorized"})

        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            return jsonify({"success": False, "error": "Patient not found"})

        doctor_id = request.form.get("doctor_id")
        date = request.form.get("date")
        slot = request.form.get("slot")

        if not all([doctor_id, date, slot]):
            return jsonify({"success": False, "error": "Missing required fields"})


        existing_appointment = Appointment.query.filter_by(
            patient_id=patient.id,
            doctor_id=doctor_id,
            status='scheduled'
        ).first()

        if existing_appointment:
            return jsonify({
                "success": False, 
                "error": f"You already have a scheduled appointment with this doctor on {existing_appointment.date}"
            })

        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({"success": False, "error": "Doctor not found"})

        availability_data = slicing_availability_string(doctor.availability)
        available_slots = availability_data.get(date, [])
    
        if slot not in available_slots:
            return jsonify({"success": False, "error": "This time slot is no longer available"})


        existing_slot_booking = Appointment.query.filter_by(
            doctor_id=doctor_id,
            date=date,
            time=slot,
            status='scheduled'
        ).first()

        if existing_slot_booking:
            return jsonify({"success": False, "error": "This time slot has just been booked by another patient"})

        try:

            appointment = Appointment(
                patient_id=patient.id,
                doctor_id=doctor_id,
                date=date,
                time=slot,
                status='scheduled'
            )
        

            availability_data[date].remove(slot)
            doctor.availability = create_availability_string(availability_data)
        
            db.session.add(appointment)
            db.session.commit()
        
            return jsonify({"success": True, "message": "Appointment booked successfully!"})
        
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)})

    @app.route("/cancel_appointment/<int:appointment_id>", methods=["GET","POST"])
    @login_required
    def cancel_appointment(appointment_id):
        if current_user.role != 'patient':
                flash('Unauthorized!', 'danger')
                return redirect(url_for('patient_dashboard'))

        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
            flash('Patient profile not found!', 'danger')
            return redirect(url_for('patient_dashboard'))
        appointment = Appointment.query.filter_by(
            id=appointment_id,
            patient_id=patient.id
            ).first_or_404()

        try:
 
            appointment.status = 'cancelled'
            db.session.commit()
            flash('Appointment cancelled successfully!', 'success')
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error cancelling appointment: {str(e)}', 'danger')
        return redirect(url_for('patient_dashboard'))