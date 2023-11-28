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


def create_src(file):
    """Adds src attribute to filecontent object representing html img src value to display image

    Accepts FileContent object and adds the src attribute which represents the src value of an html img tag.
    This allows the attribute to be directly plugged into an html template within an html tag src value

    Keyword Arguements:
    file -- FileContent object

    Return: None

    """
    file.src = f"data:image/{file.location};base64,{file.rendered_data}"        
        
def create_image(id):
    """Creates image_item object for a FileContent item

    Accepts integer representing FileContent id and creates an image_item object for it

    Keyword Arguements:
    id -- integer representing FileContent id 

    Return: image_item object

    """

    try:
        id = int(id)
    except: 
        return redirect('/404')
    image = FileContent.query.get_or_404(id)
    create_src(image)
    return image

def create_image_item(id):
    """Creates image_item object for an item based on item id

    Accepts integer representing PageObject id and creates an image_item object for that item's primary image

    Keyword Arguements:
    id -- integer representing PageObject id 

    Return: image_item object

    """
    
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
    create_src(image)
    return image

def create_image_item_2(item):
    """Creates image_item object for an item based on item object

    Accepts PageObject object and creates an image_item object for that item's primary image

    Keyword Arguements:
    item -- PageObject object 

    Return: image_item object

    """

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
    create_src(image)
    return image

def save_item(request):
        """Function to save a file in the local directory

        Accepts a post request in the form of an html form submission. It is important that the form has
        enctype="multipart/form-data" activated so that you can access the files attribute. There should be
        a file input with the name "file" which is what will be accessed
        
        Keyword Arguements:
        request -- http post request from an html form submission

        Return: string representing the name of the file

        """
        
        user_file = request.files["file"]
        if user_file.filename == '':
            return None
        if user_file:
            filename = secure_filename(user_file.filename)
            pic_name = str(uuid.uuid1()) + "_" + filename
            user_file.save(os.path.join(app.config["ITEM_FOLDER"], pic_name))
            return pic_name

def render_picture(data):
    """Converts byte data for image into a viewable format that is safe for browsers

    Accepts stream data of raw image and converts it into a byte stream that is able to be rendered via a browser
    
    Keyword Arguements:
    data -- stream with raw image data

    Return: base64 string with browser safe version of the image

    """

    render_pic = base64.b64encode(data).decode('ascii') 
    return render_pic

def uploadimage(request):
    """Function used to upload new image files to the database

    Accepts a post request in the form of an html form submission. It is important that the form has
    enctype="multipart/form-data" activated so that you can access the files attribute. There should be
    a file input with the name "file" which is what will be accessed
    
    Keyword Arguements:
    request -- http post request from an html form submission

    Return: int representing the image id from the FileContent table

    """
    
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