from flask import Flask
from app.database import db
from app.controllers import init_routes, login_manager, create_default_admin
from app.config import LocalDevelopmentConfig

def create_app():
    app = Flask(__name__)
    
    app.config.from_object(LocalDevelopmentConfig)
  
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"
    
    init_routes(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully!")
            create_default_admin()
            print("Default admin created successfully!")
        except Exception as e:
            print(f"Error creating database: {e}")
    
    app.run(debug=True)