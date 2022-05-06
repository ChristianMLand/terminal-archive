from flask_app import app
from flask_app.controllers import availability_controller, user_controller, api_controller

if __name__ == "__main__":
    app.run(debug=True)