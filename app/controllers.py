from flask import render_template, request, url_for, redirect
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import db
from app.model import User, Patient, Doctor, Appointment, MedicalRecord 


login_manager = LoginManager()
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_default_admin():
    admin_username = "admin"
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


def init_routes(app):

    @app.route("/")
    def home():
        return render_template("home.html")


    @app.route('/register', methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            role = request.form.get("role", "patient")

            if User.query.filter_by(username=username).first():
                return render_template("sign_up.html", error="Username already taken!")
            
            hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
            new_user = User(username=username, password=hashed_password, role=role)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))
        return render_template("sign_up.html")


    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password, password):
                login_user(user)
                if user.role == "admin":
                    return redirect(url_for("admin_dashboard"))
                elif user.role == "doctor":
                    return redirect(url_for("doctor_dashboard"))
                else:
                    return redirect(url_for("patient_dashboard"))
            else:
                return render_template("login.html", error="Invalid username or password")
        return render_template("login.html")


    @app.route("/patient_dashboard")
    @login_required
    def patient_dashboard():
        if current_user.role != 'patient':
            return redirect(url_for('home'))
        return render_template("patient_dashboard.html", username=current_user.username)

   
    @app.route("/doctor_dashboard")
    @login_required
    def doctor_dashboard():
        if current_user.role != 'doctor':
            return redirect(url_for('home'))
        return render_template("doctor_dashboard.html", username=current_user.username)

  
    @app.route("/admin_dashboard")
    @login_required
    def admin_dashboard():
        if current_user.role != 'admin':
            return redirect(url_for('home'))
        return render_template("admin_dashboard.html", username=current_user.username)

   
    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("home"))