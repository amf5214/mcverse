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
from src.aux_page_rendering import AuxPageRendering

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

    class Permission():
        def __init__(self, has, name):
            self.has=has
            self.name=name

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

app.add_url_rule('/aboutus', view_func=AuxPageRendering.aboutus)
app.add_url_rule('/contactus', view_func=AuxPageRendering.contactus)


@app.route('/newquestion', methods=['POST'])
def new_question():
    new_question = FrequentlyAskedQuestion(author_user=str(request.form["username"]), question=str(request.form["question"]))
    
    db.session.add(new_question)
    db.session.commit()
    return redirect('/')

@app.route('/item/<itemid>', defaults={"editable":"false"})
@app.route('/item/<itemid>/<editable>')
def item_report(itemid, editable):
    page_object = PageObject.query.get_or_404(itemid)
    item_image = create_image_item(itemid) 
    craftingdefault = create_image(10) 
    smeltingdefault = create_image(9) 

    if page_object.crafting_image_links != "":
        crafting_links = page_object.crafting_image_links.strip().split(" ")
        for i, link in enumerate(crafting_links):
            crafting_links[i] = create_image(link)
    else:
        crafting_links = ""

    if page_object.smelting_image_links != "":
        smelting_links = page_object.smelting_image_links.strip().split(" ")
        for i, link in enumerate(smelting_links):
            smelting_links[i] = create_image(int(link))
    else:
        smelting_links = ""

    if editable == "true":
        editable_permisssion = check_if_editor(request)
        if editable_permisssion:
            return render_template('item.html', page_object=page_object, item_image=item_image, crafting_links=crafting_links, smelting_links=smelting_links, editable=editable_permisssion, useraccount=get_account(request), smeltingdefault=smeltingdefault, craftingdefault=craftingdefault, itemclasses=get_item_classes(), videoimage=create_image(int(59)))
        else:
            return redirect(f"/item/{itemid}/false")
    else:
        return render_template('item.html', page_object=page_object, item_image=item_image, crafting_links=crafting_links, smelting_links=smelting_links, editable=False, useraccount=get_account(request))

@app.route('/item/admin')
def item_admin():
    if not check_if_admin(request):
        return redirect('/')
    items = PageObject.query.order_by(PageObject.id).all()
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
    return render_template('item_admin.html', admin_token=True, items=items, template=template, useraccount=get_account(request), itemclasses=get_item_classes())

@app.route('/newitem', methods=['POST'])
def new_item():
    if not check_if_editor(request):
        return redirect('/item/home/item')
    rarity = request.form["item_rarity"] if request.form["item_rarity"] != "" else "Common"
    path = uploadimage(request)
    if path == None:
        path=1

    try:
        stack_size  = int(request.form["stack_size"])

    except: 
        stack_size = 0
    

    new_item = PageObject(
        item_title = request.form["item_title"],
        image_link = path,
        item_description = request.form["description"],
        iframe_video_link = request.form["iframe_video_link"],
        source_mod = request.form["source_mod"],
        stack_size = stack_size,
        item_rarity = rarity,
        dimension = request.form["dimension"],
        item_type = request.form["item_type"],
        minecraft_item_id = request.form["minecraft_item_id"],
        crafting_image_links = "",
        smelting_image_links = ""
    )
    db.session.add(new_item)
    db.session.commit()
    return redirect('/item/home/item')

@app.route('/deleteitem/<itemid>')
def delete_item(itemid):
    db.session.delete(PageObject.query.get_or_404(itemid))
    db.session.commit()
    return redirect('/item/admin')

def get_item_json():
    objects = PageObject.query.order_by(PageObject.id).all()
    json_data = []
    for x in objects:
        json_data.append([x.item_title, x.id])
    return {"jdata": json_data}

@app.route('/updateitem/<itemid>', methods=["POST"])
def update_item(itemid):
    if not check_if_editor(request):
        return redirect(f"/item/{itemid}/false")
    if request.method == "POST":
        item = PageObject.query.get_or_404(itemid)

        if request.form["attribute"] == "item_title":
            item.item_title = request.form["newValue"]
        elif request.form["attribute"] == "item_description":
            item.item_description = request.form["newValue"]
        elif request.form["attribute"] == "source_mod":
            item.source_mod = request.form["newValue"]
        elif request.form["attribute"] == "stack_size":
            item.stack_size = int(request.form["newValue"])
        elif request.form["attribute"] == "item_rarity":
            item.item_rarity = request.form["newValue"]
        elif request.form["attribute"] == "dimension":
            item.dimension = request.form["newValue"]
        elif request.form["attribute"] == "item_type":
            item.item_type = request.form["newValue"]
        elif request.form["attribute"] == "smelting_image_links":
            item.smelting_image_links = request.form["newValue"]
        elif request.form["attribute"] == "crafting_image_links":
            item.crafting_image_links = request.form["newValue"]
        elif request.form["attribute"] == "iframe_video_link":
            item.iframe_video_link = request.form["newValue"]
        elif request.form["attribute"] == "image_link":
            item.image_link = request.form["newValue"]
        elif request.form["attribute"] == "minecraft_item_id":
            item.minecraft_item_id = request.form["newValue"]
        
        try:
            db.session.commit()
            return redirect(f"/item/{itemid}/true")
        
        except:
            pass

@app.route('/admin/items')
def all_items():
    return jsonify(get_item_json())


@app.route('/signin/home')
def signin():
    return render_template('signinup.html', useraccount=get_account(request))

@app.route('/signin/failed')
def failed_signin():
    return render_template('signinup.html', message="Username/Password Invalid. Please try again.", useraccount=get_account(request))

@app.route('/profile')
def profile():
    account = get_account(request)
    if account.full_name != "No Account":
        permissions = db.session.execute(db.select(AccountPermission).filter_by(account_id=account.id)).scalars()
        permissions_gen = []
        remaining_permissions = [z for z in Permission_values]
        for x in permissions:
            perm_type = x.permission_type
            permissions_gen.append(Permission(has=True, name=perm_type))
            remaining_permissions.remove(perm_type)
        for y in remaining_permissions:
            permissions_gen.append(Permission(has=False, name=y))
        return render_template("profile.html", useraccount=account, permissions=permissions_gen)
    else:
        return redirect('/signin/home')

# @app.route('/profile/introduction')
# def introduction():
#     return render_template("introduction.html", useraccount=get_account(request))


@app.route('/attemptedsignin', methods=["POST"])
def signinattempt():
    try:
        given_pass = request.form["logpass"]

        auth_account = db.session.execute(db.select(AuthAccount).filter_by(email_account=request.form["logemail"])).scalar_one()

        if(validate_password(given_pass, auth_account.hash_password)):
            auth_account.auth_token = encode_auth_token(request.form["logemail"])
            db.session.commit()
            response = make_response(redirect("/"))
            response.set_cookie("token", auth_account.auth_token)
            return response
        else:
            return redirect("/signin/failed")
    except NoResultFound: 
        return redirect("/signin/failed")
    
@app.route('/signout')
def sign_out():
    response = make_response(redirect("/"))
    response.set_cookie("token", "None")
    return response

@app.route('/newaccount', methods=["POST"])
def create_new_account():

    if request.form["logname"]=="No Account":
        return render_template('signinup.html', signupmessage="Name entry is invalid", useraccount=get_account(request))

    password = create_password(request.form["logpass"])
    token = encode_auth_token(str(request.form["logusername"]))
    auth_account = AuthAccount(email_account=request.form["logemail"],hash_password=password, auth_token=token)

    db.session.add(auth_account)

    db.session.commit()

    authaccountrec = db.session.execute(db.select(AuthAccount).filter_by(email_account=request.form["logemail"])).scalar_one()
    try:   
        birthdatedata=birthdate=request.form["logbirthdate"].split("-")
        birthdate = date(int(birthdatedata[0]), int(birthdatedata[1]), int(birthdatedata[2]))
        account = UserAccount(username=request.form["logusername"],full_name=request.form["logname"],birthdate=birthdate,auth_account_id=authaccountrec.id)
    except ValueError:
                account = UserAccount(username=request.form["logusername"],full_name=request.form["logname"],auth_account_id=authaccountrec.id)
    db.session.add(account)
    db.session.commit()
    return redirect('/signin/home')

@app.route('/permissions/requests/admin')
def permissions_requests_admin():
    if not check_if_admin(request):
        return redirect('/')
    requests = PermissionsRequest.query.filter_by(is_visible=True).order_by(PermissionsRequest.id).all()
    return render_template("permissions_request_admin.html", admin_token=True, prequests=requests, useraccount=get_account(request))

@app.route('/requestpermission/<permission>/<accountid>')
def create_permission_request(permission, accountid):
    account = UserAccount.query.get_or_404(accountid)
    request = PermissionsRequest(account_id=accountid, permission_type=permission, username=account.username, grant_date=date.today())
    db.session.add(request)
    db.session.commit()
    return redirect('/profile')

@app.route('/prequestdeny/<requestid>')
def deny_request(requestid):
    if not check_if_admin(request):
        return redirect('/')
    permission_request = PermissionsRequest.query.get_or_404(requestid)
    permission_request.is_visible = False
    db.session.commit()
    return redirect('/permissions/requests/admin')

@app.route('/prequestapprove/<requestid>')
def approve_request(requestid):
    if not check_if_admin(request):
        return redirect('/')
    permission_request = PermissionsRequest.query.get_or_404(requestid)
    permission_request.is_visible = False
    db.session.add(AccountPermission(permission_type=permission_request.permission_type, account_id=permission_request.account_id))
    db.session.commit()
    return redirect('/permissions/requests/admin')

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

@app.route('/uploadimagedb', methods=["POST"])
def uploadnewimage():
    if not check_if_admin(request):
        return redirect('/')
    image_id = uploadimage(request)
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

@app.route('/managewebpages')
def managewebpages():
    if not check_if_admin(request):
        return redirect('/')
    pages = WebPage.query.order_by(WebPage.id).all()
    return render_template('webpagehome.html', pages=pages, useraccount=get_account(request))


@app.route('/createwebpage', methods=['POST'])
def createwebpage():
    if not check_if_admin(request):
        return redirect('/')
    new_page = WebPage(text=request.form["text"], div_title=request.form["div_title"], path=request.form["path"].lower(), directory=request.form["directory"].lower())
    db.session.add(new_page)
    db.session.commit()
    return redirect('/managewebpages')

@app.route('/deletewebpage/<pageid>')
def deletewebpage(pageid):
    if not check_if_admin(request):
        return redirect('/')

    page = db.session.execute(db.select(WebPage).filter_by(id=pageid)).scalar_one()
    db.session.delete(page)
    db.session.commit()
    return redirect('/managewebpages')

@app.route('/learn/<pagepath>', defaults={"editable":"false"})
@app.route('/learn/<pagepath>/<editable>')
def learningpages(pagepath, editable):
    try:
        page = db.session.execute(db.select(WebPage).filter_by(path=pagepath)).scalar_one()
    except NoResultFound:
        return redirect('/404')
    divs = db.session.execute(db.select(DivContainer).filter_by(page_id=page.id).order_by(DivContainer.placement_order)).scalars()
    elements = db.session.execute(db.select(PageElement).filter_by(page_id=page.id).filter(PageElement.div_id!=0).order_by(PageElement.div_id, PageElement.placement_order)).scalars()
    div_elements = {}
    max_placement_order = 0

    for element in elements:
        if element.element_type == "img":
            element.text = (create_image(int(element.text))).src
        elif element.element_type == "image-carousel":
            element_updated = process_carousel_element(element)
            if not element_updated:
                element.images = [create_image(8)]
        elif element.element_type == "div":
            elements_found = process_nested_div(element)
        if f"div_{element.div_id}" in div_elements.keys():
            div_elements[f"div_{element.div_id}"].append(element)
        else:
              div_elements[f"div_{element.div_id}"] = [element]
              
    div_lst = []
    for div in divs:
        if f"div_{div.id}" in div_elements.keys():
            div.elements = div_elements[f"div_{div.id}"]
            div.element_count = len(div.elements)
        else:
            div.elements = []
            div.element_count = len(div.elements)
        div_lst.append(div)
        if div.placement_order > max_placement_order:
            max_placement_order = div.placement_order
            
    if editable == "true":
        if check_if_editor(request):
            return render_template("learnpage.html", divs=div_lst, page=page, useraccount=get_account(request), editable=True, max_placement=max_placement_order, images=[create_image(25)]) 
        else:
            return redirect(f"/learn/{page.path}/false")
    else:
        return render_template("learnpage.html", divs=div_lst, page=page, useraccount=get_account(request), editable=False) 
        
@app.route('/learningpage/admin/newdiv/<path>/<int:page_id>/<int:placement_order>')
def create_learning_page_object(path, page_id, placement_order):
    logging.info(f"Learning Page Div Creator Running ({path}, {page_id}, {placement_order})")
    if check_if_editor(request):
        try:
            page_num = int(page_id)
            placement_order = int(placement_order)
            print(f"page_num={page_num}; placement_order={placement_order}")
            new_div = DivContainer(text="Empty div", div_title="Empty Div", page_id=page_num, placement_order=placement_order)
            db.session.add(new_div)
            db.session.commit()
            return redirect(f'/learn/{path}/true')
        except:
            return redirect('/')
    else:
        return redirect('/')

@app.route('/learningpage/admin/newimage/<path>/<int:page_id>/<int:placement_order>/<int:div_id>')
def create_learning_page_image(path, page_id, placement_order, div_id):
    logging.info(f"Learning Page Image Creator Running ({path}, {page_id}, {placement_order}, {div_id})")
    if check_if_editor(request):
        try:
            page_num = int(page_id)
            placement_order = int(placement_order)
            print(f"page_num={page_num}; placement_order={placement_order}")
            new_image = PageElement(element_type="img", div_id=div_id, text="8", page_id=page_num, placement_order=placement_order)
            db.session.add(new_image)
            db.session.commit()
            return redirect(f'/learn/{path}/true')
        except:
            return redirect('/')
    else:
        return redirect('/')

@app.route('/learningpage/admin/newpara/<path>/<int:page_id>/<int:placement_order>/<int:div_id>')
def create_learning_page_paragraph(path, page_id, placement_order, div_id):
    logging.info(f"Learning Page Image Creator Running ({path}, {page_id}, {placement_order}, {div_id})")
    if check_if_editor(request):
        try:
            page_num = int(page_id)
            placement_order = int(placement_order)
            print(f"page_num={page_num}; placement_order={placement_order}")
            new_div = PageElement(element_type="p", div_id=div_id, text="Empty paragraph", page_id=page_num, placement_order=placement_order)
            db.session.add(new_div)
            db.session.commit()
            return redirect(f'/learn/{path}/true')
        except:
            return redirect('/')
    else:
        return redirect('/')

@app.route('/learningpage/admin/newvideo/<path>/<int:page_id>/<int:placement_order>/<int:div_id>')
def create_learning_page_video(path, page_id, placement_order, div_id):
    logging.info(f"Learning Page Image Creator Running ({path}, {page_id}, {placement_order}, {div_id})")
    if check_if_editor(request):
        try:
            page_num = int(page_id)
            placement_order = int(placement_order)
            print(f"page_num={page_num}; placement_order={placement_order}")
            new_div = PageElement(element_type="video", div_id=div_id, text="https://www.youtube.com/embed/xopvkx6CpNs?si=xMM2Uq-gklaNK4_g", page_id=page_num, placement_order=placement_order)
            db.session.add(new_div)
            db.session.commit()
            return redirect(f'/learn/{path}/true')
        except:
            return redirect('/')
    else:
        return redirect('/')

@app.route('/updatelearningitem', methods=['POST'])
def update_learning_item():
    logging.info("Item updating")
    if not check_if_editor(request):
        return redirect(f'/learn/{request.form["page_path"]}/false')
    container_type = request.form["container"]
    element_type = request.form["attribute"]
    item_id = request.form["item"]
    new_value = request.form["newValue"]
    if container_type == "page":
        page = db.session.execute(db.select(WebPage).filter_by(id=item_id)).scalar_one()
        if element_type == "title":
            page.div_title = new_value
            db.session.commit()
        else:
            page.text = new_value
            db.session.commit()
    elif container_type == "div":
        div = db.session.execute(db.select(DivContainer).filter_by(id=item_id)).scalar_one()
        if element_type == "title":
            div.div_title = new_value
            db.session.commit()
        else:
            div.text = new_value
            db.session.commit()
    elif container_type == "element":
        element = db.session.execute(db.select(PageElement).filter_by(id=item_id)).scalar_one()
        if element_type == "title":
            element.div_title = new_value
            db.session.commit()
        else:
            element.text = new_value
            db.session.commit()
    
    return redirect(f'/learn/{request.form["page_path"]}/true')

@app.route('/movelearningelement/<page_path>/<int:element_id>/<direction>')
def move_learning_element(page_path, element_id, direction):
    logging.info("Moving page element")
    if not check_if_editor(request):
        return redirect(f'/learn/{request.form["page_path"]}/false')
    try:
        page = db.session.execute(db.select(WebPage).filter_by(path=page_path)).scalar_one()
        logging.info(f"learning page located. web_page_id={page.id}")
        current_element = db.session.execute(db.select(PageElement).filter_by(id=element_id)).scalar_one()
        logging.info(f"Current element located. element_id={current_element.id}")
        order = current_element.placement_order
        original_order = int(order)
        if direction == "up":
            order -= 1
            if order > 0:
                logging.info(f"original_order={original_order}, new_order={order}")
                other_element = db.session.execute(db.select(PageElement).filter_by(page_id=page.id, div_id=current_element.div_id, placement_order=order)).scalar_one()
                logging.info(f"Other element located. element_id={other_element.id}")
                other_element.placement_order = original_order
                current_element.placement_order = order
                db.session.commit()
        elif direction == "down":
            order += 1
            other_element = db.session.execute(db.select(PageElement).filter_by(page_id=page.id, div_id=current_element.div_id, placement_order=order)).scalar_one()
            logging.info(f"Other element located. element_id={other_element.id}")
            logging.info(f"original_order={original_order}, new_order={order}")
            other_element.placement_order = original_order
            current_element.placement_order = order
            db.session.commit()
        return redirect(f"/learn/{page_path}/true")
    except Exception as e:
        print(e)
        return redirect('/')
        
@app.route('/movelearningdiv/<page_path>/<int:div_id>/<direction>')
def move_learning_div(page_path, div_id, direction):
    logging.info("Moving page div")
    if not check_if_editor(request):
        return redirect(f'/learn/{request.form["page_path"]}/false')
    try:
        page = db.session.execute(db.select(WebPage).filter_by(path=page_path)).scalar_one()
        logging.info(f"learning page located. web_page_id={page.id}")
        current_div = db.session.execute(db.select(DivContainer).filter_by(id=div_id)).scalar_one()
        logging.info(f"Current div located. div_id={current_div.id}")
        order = current_div.placement_order
        original_order = int(order)
        if direction == "up":
            order -= 1
            if order > 0:
                logging.info(f"original_order={original_order}, new_order={order}")
                other_div = db.session.execute(db.select(DivContainer).filter_by(page_id=page.id, placement_order=order)).scalar_one()
                logging.info(f"Other div located. div_id={other_div.id}")
                other_div.placement_order = original_order
                current_div.placement_order = order
                db.session.commit()
        elif direction == "down":
            order += 1
            other_div = db.session.execute(db.select(DivContainer).filter_by(page_id=page.id, placement_order=order)).scalar_one()
            logging.info(f"Other element located. element_id={other_div.id}")
            logging.info(f"original_order={original_order}, new_order={order}")
            other_div.placement_order = original_order
            current_div.placement_order = order
            db.session.commit()
        return redirect(f"/learn/{page_path}/true")
    except Exception as e:
        print(e)
        return redirect('/')

@app.route('/unlinkpageitem/<page_path>/<container_type>/<item_id>')
def unlink_page_item(page_path, container_type, item_id):
    print(f"page_path={page_path}, container={container_type}, item={item_id}")
    if not check_if_editor(request):
        return redirect(f'/learn/{request.form["page_path"]}/false')
    if container_type == "div":
        div = db.session.execute(db.select(DivContainer).filter_by(id=item_id)).scalar_one()
        div.page_id = -1
        db.session.commit()

    elif container_type == "element":
        element = db.session.execute(db.select(PageElement).filter_by(id=item_id)).scalar_one()
        element.page_id = -1
        db.session.commit()

    return redirect(f'/learn/{page_path}/true')

@app.route('/learningpage/admin/newcarousel/<path>/<int:page_id>/<int:placement_order>/<int:div_id>')
def create_learning_page_carousel(path, page_id, placement_order, div_id):
    logging.info(f"Learning Page Image Carousel Creator Running ({path}, {page_id}, {placement_order}, {div_id})")
    if check_if_editor(request):
        try:
            page_num = int(page_id)
            placement_order = int(placement_order)
            print(f"page_num={page_num}; placement_order={placement_order}")
            new_image = PageElement(element_type="image-carousel", div_id=div_id, text="25", page_id=page_num, placement_order=placement_order)
            db.session.add(new_image)
            db.session.commit()
            return redirect(f'/learn/{path}/true')
        except:
            return redirect('/')
    else:
        return redirect('/')

@app.route('/learningpage/admin/newsection/<path>/<int:page_id>/<int:placement_order>/<int:div_id>')
def create_learning_page_section(path, page_id, placement_order, div_id):
    logging.info(f"Learning Page Image Carousel Creator Running ({path}, {page_id}, {placement_order}, {div_id})")
    if check_if_editor(request):
        try:
            page_num = int(page_id)
            placement_order = int(placement_order)
            print(f"page_num={page_num}; placement_order={placement_order}")
            new_section_part1 = PageElement(element_type="img", div_id=0, text="25", page_id=page_num, placement_order=0)
            new_section_part2 = PageElement(element_type="p", div_id=0, text="Empty paragraph", page_id=page_num, placement_order=0)
            db.session.add(new_section_part1)
            db.session.add(new_section_part2)

            db.session.commit()

            new_section = PageElement(element_type="div", div_id=div_id, text=f"{new_section_part1.id}-{new_section_part2.id}", page_id=page_num, placement_order=placement_order)
            db.session.add(new_section)

            db.session.commit()
            return redirect(f'/learn/{path}/true')
        except:
            return redirect('/')
    else:
        return redirect('/')
        
@app.route('/pageelementimageupdate', methods=['POST'])
def update_page_element_image():
    if not check_if_editor(request):
        return redirect('/')
    image_id = uploadimage(request)
    page_element = PageElement.query.get_or_404(request.form["element_id"])

    page_element.text = str(image_id)
    print(f"element_id={page_element.id}. image_id={image_id}")
    db.session.commit()
    return redirect(f"/learn/{request.form['page_path']}/true")

@app.route('/admingetcarousel/<int:element_id>')
def carousel_items(element_id):
    if not check_if_editor(request):
        return redirect('/')
    return jsonify(get_carousel_items(element_id))

@app.route('/removecarouselimage', methods=['POST'])
def remove_carousel_image():
    if not check_if_editor(request):
        return redirect('/')
    request_data = request.get_json()
    carousel_id = request_data['carousel_id']
    image_id = request_data['image_id']
    page_path = request_data['page_path']
    try:
        carousel = db.session.execute(db.select(PageElement).filter_by(id=carousel_id)).scalar_one()
        text = carousel.text
        images = text.split("-")
        print(f"images={images}; image_id={str(image_id)}")
        images.remove(str(image_id))
        return_string = ""
        for i, x in enumerate(images):
            if i == 0:
                return_string += str(x)
            else:
                return_string += "-"
                return_string += str(x)
        carousel.text = return_string
        db.session.commit()
        print(f"newpath=/learn/{page_path}/true")
        body = {"redirect": f"/learn/{page_path}/true"}
        response_obj = make_response(jsonify(body))
        response_obj.headers.set('content-type', 'text/plain')
        return response_obj
    except Exception as e:
        print(e)
        response_obj = make_response("/")
        response_obj.headers.set('content-type', 'text/plain')
        return response_obj

@app.route('/adminaddcarouselimage', methods=["POST"])
def add_carousel_image():
    if not check_if_editor(request):
        return redirect('/')
    image_id = uploadimage(request)
    try:
        carousel_id = request.form["carousel-id"]
        page_path = request.form["page-path"]
        carousel_id = int(carousel_id)
        carousel = db.session.execute(db.select(PageElement).filter_by(id=carousel_id)).scalar_one()
        images = carousel.text.split("-")
        images.append(image_id)
        return_string = ""
        for i, x in enumerate(images):
            if i == 0:
                return_string += str(x)
            else:
                return_string += "-"
                return_string += str(x)
        carousel.text = return_string
        
        db.session.commit()

        return redirect(f"/learn/{page_path}/true")
    
    except Exception as e:
        print(e)
        return redirect("/")

app.run(debug=True, port=54913)
