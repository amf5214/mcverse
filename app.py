from flask import Flask, render_template, request, redirect, url_for, json, Response, jsonify, make_response, flash
from sqlalchemy.orm.exc import NoResultFound
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

from src.models import *
from src.image_handling import *
from src.authentication import *
from src.routing_functions.aux_page_rendering import AuxPageRendering
from src.routing_functions.admin_page_rendering import AdminPageRendering
from src.routing_functions.item_page_rendering import ItemPageRendering
from src.routing_functions.profile_page_rendering import ProfilePageRendering
from src.routing_functions.learning_page_rendering import LearningPageRendering
from src.routing_functions.learning_page_helperfunctions import LearningPageHelperFunctions
from src.routing_functions.question_page_rendering import FAQPageRendering

app = Flask(__name__)

logging.basicConfig(filename='record.log', level=logging.DEBUG, filemode="w")

with app.app_context():
    app.config["SQLALCHEMY_DATABASE_URI"] = "mariadb+pymysql://prod_main:Alhamley3/@mariadb-152364-0.cloudclusters.net:19546/mcverse_prod?charset=utf8mb4"
    app.config["SECRET_KEY"] = "jgjdfk34benrgtgjfhbdnjmkf5784iejkdshjssefwr"
    app.config["UPLOAD_FOLDER"] = "static/uploads/"
    app.config["ITEM_FOLDER"] = "static/items/"

    db.init_app(app)
    
    logging.info("Database configured")

    db.create_all()

    logging.info("Backend functions built")

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('comingsoon.html', useraccount=get_account(request)), 404

@app.route('/404')
def error_404():
    return render_template('comingsoon.html', useraccount=get_account(request)), 404

@app.route('/')
def go_home():
    frequently_asked_questions = FrequentlyAskedQuestion.query.order_by(FrequentlyAskedQuestion.id).all()
    return render_template('index.html', questions=frequently_asked_questions, useraccount=get_account(request))

# Routing for aux pages
app.add_url_rule('/aboutus', view_func=AuxPageRendering.aboutus)
app.add_url_rule('/contactus', view_func=AuxPageRendering.contactus)

# Routing for item pages
app.add_url_rule('/item/<itemid>', defaults={'editable':'false'}, view_func=ItemPageRendering.item_report)
app.add_url_rule('/item/<itemid>/<editable>', view_func=ItemPageRendering.item_report)
app.add_url_rule('/newitem', methods=['POST'], view_func=ItemPageRendering.new_item)
app.add_url_rule('/deleteitem/<itemid>', view_func=ItemPageRendering.delete_item)
app.add_url_rule('/updateitem/<itemid>', methods=['POST'], view_func=ItemPageRendering.update_item)
app.add_url_rule('/itemimageupdate', methods=['POST'], view_func=ItemPageRendering.itemimageupdate)
app.add_url_rule('/createcraftingimage', methods=['POST'], view_func=ItemPageRendering.create_crafting_image)
app.add_url_rule('/createsmeltingimage', methods=['POST'], view_func=ItemPageRendering.create_smelting_image)
app.add_url_rule('/unlinkcraftingimage/<page_object>/<image>', view_func=ItemPageRendering.unlinkcraftingimage)
app.add_url_rule('/unlinksmeltingimage/<page_object>/<image>', view_func=ItemPageRendering.unlinksmeltingimage)

# Routing for question pages
app.add_url_rule('/newquestion', methods=['POST'], view_func=FAQPageRendering.new_question)

# Routing for admin pages
app.add_url_rule('/item/admin', view_func=AdminPageRendering.item_admin)
app.add_url_rule('/permissions/requests/admin', view_func=AdminPageRendering.permissions_requests_admin)
app.add_url_rule('/prequestdeny/<requestid>', view_func=AdminPageRendering.deny_request)
app.add_url_rule('/prequestapprove/<requestid>', view_func=AdminPageRendering.approve_request)
app.add_url_rule('/uploadimagedb', methods=["POST"], view_func=AdminPageRendering.uploadnewimage)
app.add_url_rule('/managewebpages', view_func=AdminPageRendering.managewebpages)
app.add_url_rule('/createwebpage', methods=['POST'], view_func=AdminPageRendering.createwebpage)
app.add_url_rule('/deletewebpage/<pageid>', view_func=AdminPageRendering.deletewebpage)
app.add_url_rule('/admin/uploadimage', methods=['GET'], view_func=AdminPageRendering.adminuploadimage)
app.add_url_rule('/admin/items', view_func=AdminPageRendering.all_items)
app.add_url_rule('/item/home/<type>', view_func=AdminPageRendering.item_home)
app.add_url_rule('/itemclasshome', view_func=AdminPageRendering.itemclasshome)
app.add_url_rule('/newitemclass', methods=['POST'], view_func=AdminPageRendering.newitemclass)
app.add_url_rule('/deleteitemclass/<classid>', view_func=AdminPageRendering.deleteitemclass)

# Routing for profile pages
app.add_url_rule('/signin/home', view_func=ProfilePageRendering.signin)
app.add_url_rule('/signin/failed', view_func=ProfilePageRendering.failed_signin)
app.add_url_rule('/profile', view_func=ProfilePageRendering.profile)
app.add_url_rule('/attemptedsignin', methods=['POST'], view_func=ProfilePageRendering.signinattempt)
app.add_url_rule('/signout', view_func=ProfilePageRendering.sign_out)
app.add_url_rule('/newaccount', methods=['POST'], view_func=ProfilePageRendering.create_new_account)
app.add_url_rule('/requestpermission/<permission>/<accountid>', view_func=ProfilePageRendering.create_permission_request)
app.add_url_rule('/profileimageupdate', methods=['POST'], view_func=ProfilePageRendering.profileimageupdate)
app.add_url_rule('/updateprofileattribute', methods=['POST'], view_func=ProfilePageRendering.updateprofileattribute)

# Routing for learning pages
app.add_url_rule('/learn/<pagepath>', defaults={'editable':'false'}, view_func=LearningPageRendering.learningpages)
app.add_url_rule('/learn/<pagepath>/<editable>', view_func=LearningPageRendering.learningpages)

# Routing for learning page helper functions
app.add_url_rule('/learningpage/admin/newdiv/<path>/<int:page_id>/<int:placement_order>', view_func=LearningPageHelperFunctions.create_learning_page_object)
app.add_url_rule('/learningpage/admin/newimage/<path>/<int:page_id>/<int:placement_order>/<int:div_id>', view_func=LearningPageHelperFunctions.create_learning_page_image)
app.add_url_rule('/learningpage/admin/newpara/<path>/<int:page_id>/<int:placement_order>/<int:div_id>', view_func=LearningPageHelperFunctions.create_learning_page_paragraph)
app.add_url_rule('/learningpage/admin/newvideo/<path>/<int:page_id>/<int:placement_order>/<int:div_id>', view_func=LearningPageHelperFunctions.create_learning_page_video)
app.add_url_rule('/learningpage/admin/newcarousel/<path>/<int:page_id>/<int:placement_order>/<int:div_id>', view_func=LearningPageHelperFunctions.create_learning_page_carousel)
app.add_url_rule('/learningpage/admin/newsection/<path>/<int:page_id>/<int:placement_order>/<int:div_id>', view_func=LearningPageHelperFunctions.create_learning_page_section)
app.add_url_rule('/updatelearningitem', methods=['POST'], view_func=LearningPageHelperFunctions.update_learning_item)
app.add_url_rule('/movelearningelement/<page_path>/<int:element_id>/<direction>', view_func=LearningPageHelperFunctions.move_learning_element)
app.add_url_rule('/movelearningdiv/<page_path>/<int:div_id>/<direction>', view_func=LearningPageHelperFunctions.move_learning_div)
app.add_url_rule('/unlinkpageitem/<page_path>/<container_type>/<item_id>', view_func=LearningPageHelperFunctions.unlink_page_item)
app.add_url_rule('/pageelementimageupdate', methods=['POST'], view_func=LearningPageHelperFunctions.update_page_element_image)
app.add_url_rule('/admingetcarousel/<int:element_id>', view_func=LearningPageHelperFunctions.carousel_items)
app.add_url_rule('/removecarouselimage', methods=['POST'], view_func=LearningPageHelperFunctions.remove_carousel_image)
app.add_url_rule('/adminaddcarouselimage', methods=['POST'], view_func=LearningPageHelperFunctions.add_carousel_image)

app.run(debug=True, port=54913)
