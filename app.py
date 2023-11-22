from flask import Flask, render_template, request, redirect, url_for, json, Response, jsonify, make_response, flash
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import OperationalError
import sys
import jwt
import os
from datetime import datetime, timedelta, date, timezone
from werkzeug.utils import secure_filename
import uuid
import logging
from base64 import b64encode
import base64
import pymysql
import configparser

from src.models import *
from src.image_handling import *
from src.authentication import *
from src.logging_manager import get_root_logger
from src.routing_functions.aux_page_rendering import AuxPageRendering
from src.routing_functions.admin_page_rendering import AdminPageRendering
from src.routing_functions.item_page_rendering import ItemPageRendering
from src.routing_functions.profile_page_rendering import ProfilePageRendering
from src.routing_functions.learning_page_rendering import LearningPageRendering
from src.routing_functions.learning_page_helperfunctions import LearningPageHelperFunctions
from src.routing_functions.question_page_rendering import FAQPageRendering
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
        
    app.config["SECRET_KEY"] = "jgjdfk34benrgtgjfhbdnjmkf5784iejkdshjssefwr"

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
