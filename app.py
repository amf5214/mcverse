from flask import Flask, render_template, request, redirect, url_for, json, Response, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from authentication import create_password, validate_password
from datetime import date
import sys
import jwt
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

with app.app_context():
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mcverse.sqlite"
    app.config["SECRET_KEY"] = "jgjdfk34benrgtgjfhbdnjmkf5784iejkdshjssefwr"
    app.config["UPLOAD_FOLDER"] = "static/uploads/"
    app.config["ITEM_FOLDER"] = "static/items/"
    db = SQLAlchemy(app)

    class FrequentlyAskedQuestion(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        author_user = db.Column(db.String, nullable=True)
        question = db.Column(db.String(200), nullable=True)
        answer = db.Column(db.String(200), default="")
        answer_author = db.Column(db.String(200), default="")

        def __repr__(self):
                return f"<FAQ {self.id}>"
        
        def to_string(self):
            return f"FAQ {self.id} by author {self.author_user}: {self.question}"
       
    class PageObject(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        item_title = db.Column(db.String(200), nullable=False)
        image_link = db.Column(db.String(200))
        item_description = db.Column(db.String(200), nullable=True)
        iframe_video_link = db.Column(db.String(500), nullable=True, default="www.google.com")
        crafting_image_links = db.Column(db.String(200))
        smelting_image_links = db.Column(db.String(200))
        source_mod = db.Column(db.String(50))
        stack_size = db.Column(db.Integer)
        item_rarity = db.Column(db.Enum("Common", "Uncommon", "Rare", "Impossible", "Creative Only", ""))
        dimension = db.Column(db.String(30))
        item_type = db.Column(db.String(20))
        minecraft_item_id = db.Column(db.String(1000))

        def __repr__(self):
            return f"<PageObj {self.id}>"

    class UserAccount(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(50))
        full_name = db.Column(db.String(100))
        auth_account_id = db.Column(db.Integer)
        birthdate = db.Column(db.Date)
        account_image_link = db.Column(db.String(100))
        bio = db.Column(db.Text)
        experience = db.Column(db.Text)

        def __repr__(self):
            return f"<UserAccount {self.id}>"
        
        def set_auth(self, auth_account):
            self.auth = auth_account
        
    class AccountPermission(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        permission_type = db.Column(db.String(50))
        account_id = db.Column(db.Integer)
        grant_date = db.Column(db.Date)

        def __repr__(self):
            return f"<AccountPermission {self.id}>"
        
    class PermissionsRequest(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(50))
        permission_type = db.Column(db.String(50))
        account_id = db.Column(db.Integer)
        grant_date = db.Column(db.Date)
        is_visible = db.Column(db.Integer, default=1)

        def __repr__(self):
            return f"<AccountPermission Request {self.id}>"
        
    class AuthAccount(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        email_account = db.Column(db.String(100), unique=True)
        hash_password = db.Column(db.String(1000))
        auth_token = db.Column(db.String(1000))

        def __repr__(self):
            return f"<AuthAccount {self.id}>"
        
    class Permission():
        def __init__(self, has, name):
            self.has=has
            self.name=name
        
    def get_account(request):
        token = request.cookies.get("token")
        try:
            auth_account = db.session.execute(db.select(AuthAccount).filter_by(auth_token=token)).scalar_one()
            account = db.session.execute(db.select(UserAccount).filter_by(auth_account_id=auth_account.id)).scalar_one()
            account.set_auth(auth_account)
            account.admin_flag = permission_validation("Admin", account.id)
            print(account.admin_flag)
            if account.account_image_link != None:
                account.image_resource_link = os.path.join(os.curdir, "/static/uploads", account.account_image_link)
                account.image_flag = True
            else:
                account.image_resource_link = os.path.join(os.curdir, "/static/uploads", "no_image.jpg")
                account.image_flag = False

            return account
        
        except NoResultFound:
            return UserAccount(full_name="No Account")
        
    def permission_validation(permission, accountid):
        user_perms = db.session.execute(db.select(AccountPermission).filter_by(account_id=accountid)).scalars()
        for permissionx in user_perms:
            print(f"{permissionx.permission_type}={permission}")
            if permissionx.permission_type == permission:
                return True
        
        return False
        
        
    def encode_auth_token(email_account):
            """
            Generates the Auth Token
            :return: string
            """
            try:
                payload = {
                    'exp': datetime.utcnow() + timedelta(days=1, seconds=0),
                    'iat': datetime.utcnow(),
                    'sub': email_account
                }
                return jwt.encode(
                    payload,
                    app.config.get('SECRET_KEY'),
                    algorithm='HS256'
                )
            except Exception as e:
                return e
            
    def save_item(request):
        user_file = request.files["file"]
        if user_file.filename == '':
            return None
        if user_file:
            filename = secure_filename(user_file.filename)
            pic_name = str(uuid.uuid1()) + "_" + filename
            print(pic_name)
            print(os.path.join(app.config["ITEM_FOLDER"], pic_name))
            user_file.save(os.path.join(app.config["ITEM_FOLDER"], pic_name))
            return pic_name

    db.create_all()

    Permission_values = ["Admin", "Edit_Pages", "Add_Pages"]


@app.route('/')
def go_home():
    frequently_asked_questions = FrequentlyAskedQuestion.query.order_by(FrequentlyAskedQuestion.id).all()
    objects = PageObject.query.order_by(PageObject.id).all()
    page_objects = map(lambda obj: f"{obj.id}:{obj.item_title},", objects)

    original_stdout = sys.stdout # Save a reference to the original standard output

    with open('static/searchbar.txt', 'w') as f:
        sys.stdout = f # Change the standard output to the file we created.
        for x in page_objects:
            print(x)
        sys.stdout = original_stdout
    
    return render_template('index.html', questions=frequently_asked_questions, useraccount=get_account(request))


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', useraccount=get_account(request))

@app.route('/contactus')
def contactus():
    return render_template('contactus.html', useraccount=get_account(request))

@app.route('/newquestion', methods=['POST'])
def new_question():
    new_question = FrequentlyAskedQuestion(author_user=str(request.form["username"]), question=str(request.form["question"]))
    print(new_question.to_string())
    
    db.session.add(new_question)
    db.session.commit()
    return redirect('/')

@app.route('/item/<itemid>', defaults={"editable":"false"})
@app.route('/item/<itemid>/<editable>')
def item_report(itemid, editable):
    page_object = PageObject.query.get_or_404(itemid)
    image_url = f"/static/items/{page_object.image_link}" 
    if page_object.crafting_image_links != "":
        crafting_links = page_object.crafting_image_links.split(" ")
        for i, link in enumerate(crafting_links):
            crafting_links[i] = f"/static/items/{link}"
    else:
        crafting_links = ""

    if page_object.smelting_image_links != "":
        smelting_links = page_object.smelting_image_links.split(" ")
        for i, link in enumerate(smelting_links):
            smelting_links[i] = f"/static/items/{link}"
    else:
        smelting_links = ""

    account = get_account(request)

    print("editable=" + editable)
    if editable == "true":
        editable_permisssion = permission_validation("Edit_Pages", account.id)
        print("editable_permission=" + str(editable_permisssion))
        if editable_permisssion:
            return render_template('item.html', page_object=page_object, image_url=image_url, crafting_links=crafting_links, smelting_links=smelting_links, editable=editable_permisssion, useraccount=get_account(request))
        else:
            return redirect(f"/item/{itemid}/false")
    else:
        return render_template('item.html', page_object=page_object, image_url=image_url, crafting_links=crafting_links, smelting_links=smelting_links, editable=False, useraccount=get_account(request))

@app.route('/item/admin')
def item_admin():
    items = PageObject.query.order_by(PageObject.id).all()
    template = {
        "id": "ID", 
        "item_title": "Title", 
        "description": "Description",
        "iframe_video_link": "Youtube video", 
        "crafting_image_links": "Crafting Image Links", 
        "smelting_image_links": "Smelting Image Links", 
        "source_mod": "Source Mod", 
        "stack_size": "Stack Size", 
        "item_rarity": "Rarity", 
        "dimension": "Dimension",
        "minecraft_item_id": "Minecraft Item ID",
        "item_type": "Item Type"
        }
    return render_template('item_admin.html', admin_token=True, items=items, template=template, useraccount=get_account(request))

@app.route('/newitem', methods=['POST'])
def new_item():
    rarity = request.form["item_rarity"] if request.form["item_rarity"] != "" else "Common"
    path = save_item(request)
    if path == None:
        path=""

    new_item = PageObject(
        item_title = request.form["item_title"],
        image_link = path,
        item_description = request.form["description"],
        iframe_video_link = request.form["iframe_video_link"],
        crafting_image_links = request.form["crafting_image_links"],
        smelting_image_links = request.form["smelting_image_links"],
        source_mod = request.form["source_mod"],
        stack_size = request.form["stack_size"],
        item_rarity = rarity,
        dimension = request.form["dimension"],
        item_type = request.form["item_type"],
        minecraft_item_id = request.form["minecraft_item_id"]
    )
    db.session.add(new_item)
    db.session.commit()
    return redirect('/item/home')

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
            print(f"{item.id} updated")
            return redirect(f"/item/{itemid}")
        
        except:
            print(f"There was an error when updating the chosen item {itemid}")

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
            print(perm_type)
            permissions_gen.append(Permission(has=True, name=perm_type))
            remaining_permissions.remove(perm_type)
        for y in remaining_permissions:
            permissions_gen.append(Permission(has=False, name=y))
        print(remaining_permissions)
        print(permissions_gen)
        return render_template("profile.html", useraccount=account, permissions=permissions_gen)
    else:
        return redirect('/signin')

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
    except NoResultFound: 
        return redirect("/signin/failed")
    
@app.route('/signout')
def sign_out():
    response = make_response(redirect("/"))
    response.set_cookie("token", "None")
    return response

@app.route('/newaccount', methods=["POST"])
def create_new_account():

    password = create_password(request.form["logpass"])
    print(request.form["logusername"])
    token = encode_auth_token(str(request.form["logusername"]))
    print(token)
    auth_account = AuthAccount(email_account=request.form["logemail"],hash_password=password, auth_token=token)

    db.session.add(auth_account)

    db.session.commit()

    authaccountrec = db.session.execute(db.select(AuthAccount).filter_by(email_account=request.form["logemail"])).scalar_one()
    birthdatedata=birthdate=request.form["logbirthdate"].split("-")
    print(birthdatedata)
    birthdate = date(int(birthdatedata[0]), int(birthdatedata[1]), int(birthdatedata[2]))

    account = UserAccount(username=request.form["logusername"],full_name=request.form["logname"],birthdate=birthdate,auth_account_id=authaccountrec.id)
    db.session.add(account)
    db.session.commit()
    return redirect('/signin/home')

@app.route('/permissions/requests/admin')
def permissions_requests_admin():
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
    permission_request = PermissionsRequest.query.get_or_404(requestid)
    permission_request.is_visible = False
    db.session.commit()
    return redirect('/permissions/requests/admin')

@app.route('/prequestapprove/<requestid>')
def approve_request(requestid):
    permission_request = PermissionsRequest.query.get_or_404(requestid)
    permission_request.is_visible = False
    db.session.add(AccountPermission(permission_type=permission_request.permission_type, account_id=permission_request.account_id))
    db.session.commit()
    return redirect('/permissions/requests/admin')

@app.route('/profileimageupdate', methods=['POST'])
def updateprofileimage():
    picture_account = UserAccount.query.get_or_404(request.form["user_id"])
    print(picture_account)
    user_file = request.files["imageupload"]
    if user_file.filename == '':
        return redirect("/profile")
    if user_file:
        filename = secure_filename(user_file.filename)
        pic_name = str(uuid.uuid1()) + "_" + filename
        print(pic_name)
        print(os.path.join(app.config["UPLOAD_FOLDER"], pic_name))
        user_file.save(os.path.join(app.config["UPLOAD_FOLDER"], pic_name))
        picture_account.account_image_link = pic_name
        db.session.commit()
        return redirect("/profile")
    
@app.route('/item/home')
def item_home():
    items = db.session.execute(db.select(PageObject).filter_by(item_type="Item")).scalars()
    item_list = []
    for x in items:
        x.image_link = "/static/items/" + x.image_link
        item_list.append(x)
    
    template = {
        "id": "ID", 
        "item_title": "Title", 
        "image_link": "Image Link",
        "description": "Description",
        "iframe_video_link": "Youtube video", 
        "crafting_image_links": "Crafting Image Links", 
        "smelting_image_links": "Smelting Image Links", 
        "source_mod": "Source Mod", 
        "stack_size": "Stack Size", 
        "item_rarity": "Rarity", 
        "dimension": "Dimension",
        "minecraft_item_id": "Minecraft Item ID",
        "item_type": "Item Type"
        }
    return render_template('itemhome.html', items=item_list, pagename="Item", template=template, useraccount=get_account(request))

@app.route('/tool/home')
def tool_home():
    items = db.session.execute(db.select(PageObject).filter_by(item_type="Tool")).scalars()
    item_list = []
    for x in items:
        x.image_link = "/static/items/" + x.image_link
        item_list.append(x)
    
    template = {
        "id": "ID", 
        "item_title": "Title", 
        "image_link": "Image Link",
        "description": "Description",
        "iframe_video_link": "Youtube video", 
        "crafting_image_links": "Crafting Image Links", 
        "smelting_image_links": "Smelting Image Links", 
        "source_mod": "Source Mod", 
        "stack_size": "Stack Size", 
        "item_rarity": "Rarity", 
        "dimension": "Dimension",
        "minecraft_item_id": "Minecraft Item ID",
        "item_type": "Item Type"
        }
    return render_template('itemhome.html', pagename="Tool", items=item_list, template=template, useraccount=get_account(request))

@app.route('/weapon/home')
def weapon_home():
    items = db.session.execute(db.select(PageObject).filter_by(item_type="Weapon")).scalars()
    item_list = []
    for x in items:
        x.image_link = "/static/items/" + x.image_link
        item_list.append(x)
    
    template = {
        "id": "ID", 
        "item_title": "Title", 
        "image_link": "Image Link",
        "description": "Description",
        "iframe_video_link": "Youtube video", 
        "crafting_image_links": "Crafting Image Links", 
        "smelting_image_links": "Smelting Image Links", 
        "source_mod": "Source Mod", 
        "stack_size": "Stack Size", 
        "item_rarity": "Rarity", 
        "dimension": "Dimension",
        "minecraft_item_id": "Minecraft Item ID",
        "item_type": "Item Type"
        }
    return render_template('itemhome.html', pagename="Weapon", items=item_list, template=template, useraccount=get_account(request))

if __name__ == '__main__':
    app.run(debug=True, port=54913)
   