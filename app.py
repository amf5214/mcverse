from flask import Flask
from sqlalchemy.exc import OperationalError
import os
import configparser
import secrets

from src.models import *
from src.image_handling import *
from src.authentication import *
from src.logging_manager import log_message
from src.routing_manager import configure_routing


app = Flask(__name__)

log_message("--------------------------Application Server Starting------------------------------", main=True)
    
with app.app_context():
    db_config_file = 'auth/database_config.ini'
    if os.path.isfile(db_config_file):
        config = configparser.ConfigParser()
        config.read(db_config_file)
        app.config["SQLALCHEMY_DATABASE_URI"] = config['MariaDB_Config']['connection_string']
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = 'mariadb+pymysql://db:pasword@mariadb.cloudclusters.net:1000/prod?charset=utf8mb4'
        
    app.config["SECRET_KEY"] = secrets.token_hex(30)

    log_message('DB Connection Beginning')
    log_message(f'DB Connection location = {app.config["SQLALCHEMY_DATABASE_URI"]}')

    db.init_app(app)

    log_message('DB Connection Completed')
    log_message('DB create_all Running')

    try:
        db.create_all()
        log_message('DB create_all Completed')
        
    except OperationalError as e:
        log_message(f'DB create_all Error. Error = {e}')

    configure_routing(app)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
