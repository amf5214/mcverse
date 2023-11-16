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

from src.models import FileContent, PageObject, db

class image_item():
        def __init__(self, location, rendered_data, id):
            self.location = location
            self.rendered_data = rendered_data
            self.id = id
            self.src = self.create_src()

        def create_src(self):
            return f"data:image/{self.location};base64,{self.rendered_data}"
        
def create_image(id):
    try:
        id = int(id)
    except: 
        return redirect('/404')
    image = FileContent.query.get_or_404(id)
    return image_item(image.location, image.rendered_data, image.id)

def create_image_item(id):
    item = PageObject.query.get_or_404(id)
    if item.image_link != None:
        image_id = item.image_link
        try:
            int(image_id)
        except:
            image_id = 7
    else:
        image_id = 7
    image = FileContent.query.get_or_404(image_id)
    return image_item(image.location, image.rendered_data, image.id)

def create_image_item_2(item):
    image_id = item.image_link
    if item.image_link != None:
        image_id = item.image_link
        try:
            int(image_id)
        except:
            image_id = 7
    else:
        image_id = 7
    image = FileContent.query.get_or_404(image_id)
    return image_item(image.location, image.rendered_data, image.id)

def save_item(request):
        user_file = request.files["file"]
        if user_file.filename == '':
            return None
        if user_file:
            filename = secure_filename(user_file.filename)
            pic_name = str(uuid.uuid1()) + "_" + filename
            user_file.save(os.path.join(app.config["ITEM_FOLDER"], pic_name))
            return pic_name

def render_picture(data):
    render_pic = base64.b64encode(data).decode('ascii') 
    return render_pic

def uploadimage(request):
    file = request.files['file']
    if file.filename == '':
        return None
    if file:
        data = file.read()
        render_file = render_picture(data)
        filename = secure_filename(file.filename)
        pic_name = str(uuid.uuid1()) + "_" + filename
        location = file.filename.split(".")[1]

        newFile = FileContent(name=file.filename, rendered_data=render_file, text=pic_name, location=location)
        db.session.add(newFile)
        db.session.commit() 
        return newFile.id