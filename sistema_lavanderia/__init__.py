from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'grupopatito'

    with app.app_context():
        from .routes import routes
        app.register_blueprint(routes)
        return app