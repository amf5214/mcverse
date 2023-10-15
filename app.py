from flask import Flask, render_template, request, redirect, url_for, json, Response, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from authentication import create_password, validate_password
from datetime import date
import sys
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)

with app.app_context():
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mcverse.sqlite"
    app.config["SECRET_KEY"] = "jgjdfk34benrgtgjfhbdnjmkf5784iejkdshjssefwr"
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
        
    class AuthAccount(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        email_account = db.Column(db.String(100), unique=True)
        hash_password = db.Column(db.String(1000))
        auth_token = db.Column(db.String(1000))

        def __repr__(self):
            return f"<AuthAccount {self.id}>"
        
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
        
    def get_account(request):
        token = request.cookies.get("token")
        try:
            auth_account = db.session.execute(db.select(AuthAccount).filter_by(auth_token=token)).scalar_one()
            account = db.session.execute(db.select(UserAccount).filter_by(auth_account_id=auth_account.id)).scalar_one()
            account.set_auth(auth_account)

            return account
        
        except NoResultFound:
            return UserAccount(full_name="No Account")


    db.create_all()


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
    image_url = f"/static/{page_object.image_link}" 
    if page_object.crafting_image_links != "":
        crafting_links = page_object.crafting_image_links.split(" ")
        for i, link in enumerate(crafting_links):
            crafting_links[i] = f"/static/{link}"
    else:
        crafting_links = ""

    if page_object.smelting_image_links != "":
        smelting_links = page_object.smelting_image_links.split(" ")
        for i, link in enumerate(smelting_links):
            smelting_links[i] = f"/static/{link}"
    else:
        smelting_links = ""

    return render_template('item.html', page_object=page_object, image_url=image_url, crafting_links=crafting_links, smelting_links=smelting_links, editable=editable, useraccount=get_account(request))

@app.route('/item/admin')
def item_admin():
    items = PageObject.query.order_by(PageObject.id).all()
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
    return render_template('item_admin.html', admin_token=True, items=items, template=template, useraccount=get_account(request))

@app.route('/newitem', methods=['POST'])
def new_item():
    rarity = request.form["item_rarity"] if request.form["item_rarity"] != "" else "Common"
    new_item = PageObject(
        item_title = request.form["item_title"],
        image_link = request.form["image_link"],
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
    return redirect('/item/admin', useraccount=get_account(request))

@app.route('/deleteitem/<itemid>')
def delete_item(itemid):
    db.session.delete(PageObject.query.get_or_404(itemid))
    db.session.commit()
    return redirect('/item/admin', useraccount=get_account(request))

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
        return render_template("profile.html", useraccount=account)
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
    return redirect('signin')

@app.route('/deleteaccount/<accountid>')
def delete_account(accountid):
    # db.session.delete(AuthAccount.query.get_or_404(accountid))
    # db.session.delete(UserAccount.query.get_or_404(accountid))
    # db.session.commit()
    # return redirect('/')
    pass

if __name__ == '__main__':
    app.run(debug=True, port=54913)
   