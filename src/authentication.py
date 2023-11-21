from passlib.hash import sha256_crypt
from datetime import datetime, timedelta
import jwt
from sqlalchemy.orm.exc import NoResultFound
from flask import Flask, render_template, request, redirect, url_for, json, Response, jsonify, make_response, flash
import sys
import os
from datetime import datetime, timedelta, date, timezone
from werkzeug.utils import secure_filename
import uuid
import logging
from base64 import b64encode
import base64
from io import BytesIO #Converts data from Database into bytes
from sqlalchemy import create_engine
import pymysql
import secrets

from src.models import AuthAccount, UserAccount, FileContent, AccountPermission, db

logging.basicConfig(filename='record.log', level=logging.DEBUG, filemode="w")

secret_key = secrets.token_hex(30)

def create_password(password_string):
    return sha256_crypt.encrypt(password_string)

def validate_password(given_pass, real_pass):
    return sha256_crypt.verify(given_pass, real_pass)

def get_account(request):
        token = request.cookies.get("token")
        logging.info(f"auth_token={token}")
        if token != None:
            try:
                auth_account = db.session.execute(db.select(AuthAccount).filter_by(auth_token=token)).scalar_one()
                if auth_account != None:
                    logging.info(f"auth_account_id={auth_account.id}")
                    account = db.session.execute(db.select(UserAccount).filter_by(auth_account_id=auth_account.id)).scalar_one()
                    if account != None:
                        logging.info(f"account_id={account.id}")
                        account.set_auth(auth_account)
                        account.admin_flag = permission_validation("Admin", account.id)
                        logging.info(f"admin_flag={account.admin_flag}")
                        if account.account_image_link != None:
                            image_id = account.account_image_link
                            account.image_flag = True
                            try:
                                int(image_id)
                            except:
                                image_id = 8
                        else:
                            image_id = 8
                            account.image_flag = False
                        image_obj = FileContent.query.get_or_404(image_id)
                        account.profile_img_loc = image_obj.location
                        logging.info(f"account_image_loc={account.profile_img_loc}")
                        account.profile_img_data = image_obj.rendered_data
                    else:
                        return UserAccount(full_name="No Account")
                else:
                    return UserAccount(full_name="No Account")
                
                return account
            
            except NoResultFound:
                return UserAccount(full_name="No Account")
        else:
            return UserAccount(full_name="No Account")

def permission_validation(permission, accountid):
    user_perms = db.session.execute(db.select(AccountPermission).filter_by(account_id=accountid)).scalars()
    for permissionx in user_perms:
        if permissionx.permission_type == permission:
            return True
    
    return False

def check_if_admin(request):
    account = get_account(request)
    if account.full_name != "No Account":
        return permission_validation("Admin", account.id)
    
def check_if_editor(request):
    account = get_account(request)
    if account.full_name != "No Account":
        return permission_validation("Edit_Pages", account.id)
    
def check_if_canadd(request):
    account = get_account(request)
    if account.full_name != "No Account":
        return permission_validation("Add_Pages", account.id)
    
def encode_auth_token(email_account):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.now(timezone.utc) + timedelta(days=1, seconds=0),
                'iat': datetime.now(timezone.utc),
                'sub': email_account
            }
            return jwt.encode(
                payload,
                secret_key,
                algorithm='HS256'
            )
        except Exception as e:
            return e
        
def verify_account_match(request, accountId):
    """Verifies if the user making request is the same as the one matching the provided account id

    Takes in an http request and uses it to access the user account information so that it can compare 
    that account id with the provided account id and compare them

    Keyword Arguements:
    request -- http request containing a cookie named token which contains an authentication token
    accountId -- account id that the user is trying to access

    Return: boolean
    """

    account = get_account(request)
    return account.id == accountId
