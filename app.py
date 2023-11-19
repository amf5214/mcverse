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
from io import BytesIO #Converts data from Database into bytes
from sqlalchemy import create_engine
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

app = Flask(__name__)

logging.basicConfig(filename='record.log', level=logging.DEBUG, filemode="w")

with app.app_context():
    app.config["SQLALCHEMY_DATABASE_URI"] = "mariadb+pymysql://prod_main:Alhamley3/@mariadb-152364-0.cloudclusters.net:19546/mcverse_prod?charset=utf8mb4"
    app.config["SECRET_KEY"] = "jgjdfk34benrgtgjfhbdnjmkf5784iejkdshjssefwr"
    app.config["UPLOAD_FOLDER"] = "static/uploads/"
    app.config["ITEM_FOLDER"] = "static/items/"

    db.init_app(app)
    
    logging.info("Database configured")

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
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    def get_item_classes():
        item_classes = ItemClass.query.order_by(ItemClass.id).all()
        return item_classes

    def process_carousel_element(element):
        if element.element_type == "image-carousel":
            if element.text == "" or element.text == "NULL":
                return False
            image_links = element.text.split("-")
            element.images = []
            for x in image_links:
                image = create_image(x)
                element.images.append(image)
            return True
        else: return False

    def process_nested_div(element):
        element_ids = element.text.split("-")
        print(f"element_ids_nested={element_ids}")
        if element.text == "" or element.text == "NULL":
                return False
        element.nested_elements = []
        for x in element_ids:
            try:
                nested_element_id = int(x)
                nested_element = db.session.execute(db.select(PageElement).filter_by(id=nested_element_id)).scalar_one()
                print(nested_element)
                if nested_element.element_type == "img":
                    nested_element.text = (create_image(int(nested_element.text))).src
                element.nested_elements.append(nested_element)
            except Exception as e:
                print(f"Error found at {x}. Error: {e}")
        return True

    def convert_image_to_json(image_obj):
        json_obj = {}
        json_obj["id"] = image_obj.id
        json_obj["rendered_data"] = image_obj.rendered_data
        json_obj["location"] = image_obj.location
        json_obj["src"] = image_obj.src
        return json_obj

    def get_carousel_items(element_id):
        try:
            element_id = int(element_id)
            carousel = db.session.execute(db.select(PageElement).filter_by(id=element_id)).scalar_one()
        except Exception as e:
            print(e)

        images = carousel.text.split("-")
        image_objects = []
        for x in images:
            image_objects.append(create_image(x))
        
        json_data = []
        for y in image_objects:
            json_data.append(convert_image_to_json(y))
        
        return {"jdata": json_data}

    def get_item_json():
        objects = PageObject.query.order_by(PageObject.id).all()
        json_data = []
        for x in objects:
            json_data.append([x.item_title, x.id])
        return {"jdata": json_data}

    db.create_all()

    Permission_values = ["Admin", "Edit_Pages", "Add_Pages"]

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
app.add_url_rule('/item/<itemid>', defaults={"editable":"false"}, view_func=ItemPageRendering.item_report)
app.add_url_rule('/item/<itemid>/<editable>', view_func=ItemPageRendering.item_report)
app.add_url_rule('/newitem', methods=['POST'], view_func=ItemPageRendering.new_item)
app.add_url_rule('/deleteitem/<itemid>', view_func=ItemPageRendering.delete_item)
app.add_url_rule('/updateitem/<itemid>', methods=["POST"], view_func=ItemPageRendering.update_item)

# Routing for question pages

# Routing for admin pages
app.add_url_rule('/item/admin', view_func=AdminPageRendering.item_admin)
app.add_url_rule('/permissions/requests/admin', view_func=AdminPageRendering.permissions_requests_admin)
app.add_url_rule('/prequestdeny/<requestid>', view_func=AdminPageRendering.deny_request)
app.add_url_rule('/prequestapprove/<requestid>', view_func=AdminPageRendering.approve_request)
app.add_url_rule('/uploadimagedb', methods=["POST"], view_func=AdminPageRendering.uploadnewimage)
app.add_url_rule('/createwebpage', methods=['POST'], view_func=AdminPageRendering.createwebpage)
app.add_url_rule('/deletewebpage/<pageid>', view_func=AdminPageRendering.deletewebpage)

# Routing for profile pages
app.add_url_rule('/signin/home', view_func=ProfilePageRendering.signin)
app.add_url_rule('/signin/failed', view_func=ProfilePageRendering.failed_signin)
app.add_url_rule('/profile', view_func=ProfilePageRendering.profile)
app.add_url_rule('/attemptedsignin', methods=["POST"], view_func=ProfilePageRendering.signinattempt)
app.add_url_rule('/signout', view_func=ProfilePageRendering.sign_out)
app.add_url_rule('/newaccount', methods=["POST"], view_func=ProfilePageRendering.create_new_account)
app.add_url_rule('/requestpermission/<permission>/<accountid>', view_func=ProfilePageRendering.create_permission_request)

# Routing for learning pages
app.add_url_rule('/learn/<pagepath>', defaults={"editable":"false"}, view_func=LearningPageRendering.learningpages)
app.add_url_rule('/learn/<pagepath>/<editable>', view_func=LearningPageRendering.learningpages)

# Routing for learning page helper functions
app.add_url_rule('/learningpage/admin/newdiv/<path>/<int:page_id>/<int:placement_order>', view_func=LearningPageHelperFunctions.create_learning_page_object)
app.add_url_rule('/learningpage/admin/newimage/<path>/<int:page_id>/<int:placement_order>', view_func=LearningPageHelperFunctions.create_learning_page_image)
app.add_url_rule('/learningpage/admin/newpara/<path>/<int:page_id>/<int:placement_order>', view_func=LearningPageHelperFunctions.create_learning_page_paragraph)
app.add_url_rule('/learningpage/admin/newvideo/<path>/<int:page_id>/<int:placement_order>', view_func=LearningPageHelperFunctions.create_learning_page_video)
app.add_url_rule('/learningpage/admin/newcarousel/<path>/<int:page_id>/<int:placement_order>', view_func=LearningPageHelperFunctions.create_learning_page_carousel)
app.add_url_rule('/learningpage/admin/newsection/<path>/<int:page_id>/<int:placement_order>', view_func=LearningPageHelperFunctions.create_learning_page_section)
app.add_url_rule('/updatelearningitem', methods=['POST'], view_func=LearningPageHelperFunctions.update_learning_item)
app.add_url_rule('/movelearningelement/<page_path>/<int:element_id>/<direction>', view_func=LearningPageHelperFunctions.move_learning_element)
app.add_url_rule('/movelearningdiv/<page_path>/<int:div_id>/<direction>', view_func=LearningPageHelperFunctions.move_learning_div)
app.add_url_rule('/unlinkpageitem/<page_path>/<container_type>/<item_id>', view_func=LearningPageHelperFunctions.unlink_page_item)
app.add_url_rule('/pageelementimageupdate', methods=['POST'], view_func=LearningPageHelperFunctions.update_page_element_image)
app.add_url_rule('/admingetcarousel/<int:element_id>', view_func=LearningPageHelperFunctions.carousel_items)
app.add_url_rule('/removecarouselimage', methods=['POST'], view_func=LearningPageHelperFunctions.remove_carousel_image)
app.add_url_rule('/adminaddcarouselimage', methods=["POST"], view_func=LearningPageHelperFunctions.add_carousel_image)

@app.route('/newquestion', methods=['POST'])
def new_question():
    new_question = FrequentlyAskedQuestion(author_user=str(request.form["username"]), question=str(request.form["question"]))
    
    db.session.add(new_question)
    db.session.commit()
    return redirect('/')

@app.route('/admin/items')
def all_items():
    return jsonify(get_item_json())

@app.route('/profileimageupdate', methods=['POST'])
def profileimageupdate():
    image_id = uploadimage(request)
    picture_account = UserAccount.query.get_or_404(request.form["user_id"])

    picture_account.account_image_link = str(image_id)
    db.session.commit()
    return redirect("/profile")

@app.route('/itemimageupdate', methods=['POST'])
def itemimageupdate():
    if not check_if_editor(request):
        return redirect('/')
    image_id = uploadimage(request)
    picture_item = PageObject.query.get_or_404(request.form["item_id"])

    picture_item.image_link = str(image_id)
    db.session.commit()
    return redirect(f"/item/{request.form['item_id']}/false")
  
@app.route('/item/home/<type>')
def item_home(type):
    if type in ["item", "weapon", "tool"]:
        items = db.session.execute(db.select(PageObject).filter_by(item_type=type)).scalars()
        item_list = []
        image_dict = {}
        for x in items:
            image_dict[x.id] = create_image_item_2(x)
            item_list.append(x)
        
        template = {
            "id": "ID", 
            "item_title": "Title", 
            "description": "Description",
            "iframe_video_link": "Youtube video", 
            "source_mod": "Source Mod", 
            "stack_size": "Stack Size", 
            "item_rarity": "Rarity", 
            "dimension": "Dimension",
            "minecraft_item_id": "Minecraft Item ID",
            "item_type": "Item Type"
            }
        return render_template('itemhome.html', pagename=type.upper(), image_dict=image_dict, items=item_list, template=template, useraccount=get_account(request))
    else:
        return redirect("/")
    
@app.route('/admin/uploadimage', methods=["GET"])
def adminuploadimage():
    if not check_if_admin(request):
        return redirect('/')
    useraccount = get_account(request)
    test = permission_validation("Admin", useraccount.id)
    if test:
        return render_template('uploadimage.html', useraccount=useraccount, baseimage=create_image_item(2))
    else:
        return redirect('/')

@app.route('/createcraftingimage', methods=['POST'])
def create_crafting_image():
    if not check_if_editor(request):
        return redirect('/')
    itemid = request.form["item_id"]
    pobject = PageObject.query.get_or_404(itemid)
    image_id = uploadimage(request)
    image_links = pobject.crafting_image_links.strip().split(" ")
    image_links.append(str(image_id))
    new_str = ""
    for i, x in enumerate(image_links):
        if i == 0:
            new_str = str(x)
        else:
            new_str = new_str + " " + str(x)
    pobject.crafting_image_links = new_str
    db.session.commit()    
    return redirect(f'item/{itemid}/true')


@app.route('/createsmeltingimage', methods=['POST'])
def create_smelting_image():
    if not check_if_editor(request):
        return redirect('/')
    itemid = request.form["item_id"]
    pobject = PageObject.query.get_or_404(itemid)
    image_id = uploadimage(request)
    image_links = pobject.smelting_image_links.strip().split(" ")
    image_links.append(str(image_id))
    new_str = ""
    for i, x in enumerate(image_links):
        if i == 0:
            new_str = str(x)
        else:
            new_str = new_str + " " + str(x)
    pobject.smelting_image_links = new_str
    db.session.commit()    
    return redirect(f'item/{itemid}/true')

@app.route('/unlinkcraftingimage/<page_object>/<image>')
def unlinkcraftingimage(page_object, image):
    if not check_if_editor(request):
        return redirect('/')
    image_id = str(image)
    pobject = PageObject.query.get_or_404(page_object)
    image_links = pobject.crafting_image_links.strip().split(" ")
    image_links.remove(image_id)
    new_str = ""
    for i, x in enumerate(image_links):
        if i == 0:
            new_str = str(x)
        else:
            new_str = new_str + " " + str(x)
    pobject.crafting_image_links = new_str
    db.session.commit()   
    return redirect(f'/item/{page_object}/true')

@app.route('/unlinksmeltingimage/<page_object>/<image>')
def unlinksmeltingimage(page_object, image):
    if not check_if_editor(request):
        return redirect('/')
    image_id = str(image)
    pobject = PageObject.query.get_or_404(page_object)
    image_links = pobject.smelting_image_links.strip().split(" ")
    image_links.remove(image_id)
    new_str = ""
    for i, x in enumerate(image_links):
        if i == 0:
            new_str = str(x)
        else:
            new_str = new_str + " " + str(x)
    pobject.smelting_image_links = new_str
    db.session.commit()   
    return redirect(f'/item/{page_object}/true')

@app.route('/itemclasshome')
def itemclasshome():
    if not check_if_admin(request):
        return redirect('/')
    return render_template('itemclasshome.html', pagename="Item Class", admin_token=True, useraccount=get_account(request), itemclasses=get_item_classes())

@app.route('/newitemclass', methods=['POST'])
def newitemclass():
    if not check_if_admin(request):
            return redirect('/')
    
    item_class = ItemClass(name=request.form['class-name'])
    db.session.add(item_class)
    db.session.commit()
    return redirect('/itemclasshome')

@app.route('/deleteitemclass/<classid>')
def deleteitemclass(classid):
    if not check_if_admin(request):
        return redirect('/')
    itemclass = ItemClass.query.get_or_404(classid)
    db.session.delete(itemclass)
    db.session.commit()
    return redirect('/itemclasshome')

app.run(debug=True, port=54913)
