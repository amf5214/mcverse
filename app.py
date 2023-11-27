from flask import Flask, render_template, request
from sqlalchemy.exc import OperationalError
import sys
import os
import pymysql
import configparser
import secrets

from src.models import *
from src.image_handling import *
from src.authentication import *
from src.logging_manager import get_root_logger, create_logger
from src.routing_manager import configure_routing


app = Flask(__name__)

logger = get_root_logger("main")
db_logger = create_logger('database_configuration')

logger.info("--------------------------Application Server Starting------------------------------")
    
with app.app_context():
    db_config_file = 'auth/database_config.ini'
    if os.path.isfile(db_config_file):
        config = configparser.ConfigParser()
        config.read(db_config_file)
        app.config["SQLALCHEMY_DATABASE_URI"] = config['MariaDB_Config']['connection_string']
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = 'mariadb+pymysql://db:pasword@mariadb.cloudclusters.net:1000/prod?charset=utf8mb4'
        
    app.config["SECRET_KEY"] = secrets.token_hex(30)

    db_logger.info('DB Connection Beginning')
    db_logger.info(f'DB Connection location = {app.config["SQLALCHEMY_DATABASE_URI"]}')
    db.init_app(app)
    db_logger.info('DB Connection Completed')
    
    db_logger.info('DB create_all Running')
    try:
        db.create_all()
        db_logger.info('DB create_all Completed')
        
    except OperationalError as e:
        db_logger.info(f'DB create_all Error. Error = {e}')

    configure_routing(app)

app.run(debug=True, port=54913)
