import os
from flask import Flask, session
from app import config
from app.config import LocalDevelopmentConfig
from app.database import db
from app.controllers import login_manager, create_default_admin, init_routes


app = None


def create_app():
    app = Flask(__name__, template_folder="templates")
    if os.getenv('ENV', "development") == "production":
      raise Exception("Currently no production config is setup.")
    else:
      print("Staring Local Development")
      app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    login_manager.init_app(app)
    with app.app_context():
        db.create_all()
        create_default_admin()

    init_routes(app)
    
    return app

app= create_app()



if __name__ == '__main__':
  
  app.run(host='0.0.0.0',port=8080)
