from flask import Flask
from config import Config
from controllers import flight_controller

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

   
    app.register_blueprint(flight_controller.bp)

    return app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
