from flask import Flask
from flask_mysqldb import MySQL

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    
    app.config['MYSQL_HOST'] = 'mysql-sofuer-porto-car-wash.g.aivencloud.com'
    app.config['MYSQL_USER'] = 'avnadmin'
    app.config['MYSQL_PASSWORD'] = 'AVNS_USU_gdEw2HXwwO8UhFQ'
    app.config['MYSQL_DB'] = 'defaultdb'
    app.config['MYSQL_PORT'] = 19682
    app.config['MYSQL_SSL_MODE'] = 'REQUIRED'
    
    app.secret_key = 'grupopatito'
    
    # Inicializar MySQL
    mysql.init_app(app)
    
    with app.app_context():
        from .routes import routes
        app.register_blueprint(routes)
        return app
