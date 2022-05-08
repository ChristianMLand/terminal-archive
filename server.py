from flask_app import app
from flask_app.controllers import availability_controller, user_controller, api_controller

if __name__ == "__main__":
    from flask_app.config.mysqlconnection import create_db
    create_db()
    app.run()