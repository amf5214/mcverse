from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date, timezone
from src.logging_manager import create_logger

logger = create_logger("database_configuration")

db = SQLAlchemy()

class FrequentlyAskedQuestion(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        author_user = db.Column(db.String(200), nullable=True)
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
    item_description = db.Column(db.Text, nullable=True)
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

class FileContent(db.Model):

    id = db.Column(db.Integer,  primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    rendered_data = db.Column(db.Text(max), nullable=False) #Data to render the pic in browser
    text = db.Column(db.Text)
    location = db.Column(db.String(64))
    pic_date = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))

    def __repr__(self):
        return f"<FileContent {self.id}>"

class ItemClass(db.Model):

    id = db.Column(db.Integer,  primary_key=True)
    name = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f"<ItemClass {self.id}>"
    
class WebPage(db.Model):

    id = db.Column(db.Integer,  primary_key=True)
    text = db.Column(db.Text)
    div_title = db.Column(db.String(255))
    path = db.Column(db.String(255))
    directory = db.Column(db.String(255))

    def __repr__(self):
        return f"<WebPage {self.id}>"
    
class DivContainer(db.Model):

    id = db.Column(db.Integer,  primary_key=True)
    text = db.Column(db.Text)
    div_title = db.Column(db.String(255))
    display_type = db.Column(db.String(255))
    flex_direction = db.Column(db.String(255))
    page_id = db.Column(db.Integer)
    placement_order = db.Column(db.Integer)

    def __repr__(self):
        return f"<DivContainer {self.id}>"
    
class PageElement(db.Model):

    id = db.Column(db.Integer,  primary_key=True)
    element_type = db.Column(db.String(255))
    div_id = db.Column(db.Integer)
    text = db.Column(db.Text)
    div_title = db.Column(db.String(255))
    page_id = db.Column(db.Integer)
    placement_order = db.Column(db.Integer)

    def __repr__(self):
        return f"<PageElement {self.id}>"
        