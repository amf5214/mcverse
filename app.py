from flask import Flask, render_template, request, redirect, url_for, json, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
import sys

app = Flask(__name__)

with app.app_context():
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mcverse.sqlite"
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
        item_rarity = db.Column(db.Enum("Common", "Uncommon", "Rare", "Impossible", "Creative Only"))
        dimension = db.Column(db.String(30))
        item_type = db.Column(db.String(20))
        minecraft_item_id = db.Column(db.String(1000))

        def __repr__(self):
            return f"<Page Obj {self.id}>"


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

    return render_template('index.html', questions=frequently_asked_questions)


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/contactus')
def contactus():
    return render_template('contactus.html')

@app.route('/newquestion', methods=['POST'])
def new_question():
    new_question = FrequentlyAskedQuestion(author_user=str(request.form["username"]), question=str(request.form["question"]))
    print(new_question.to_string())
    
    db.session.add(new_question)
    db.session.commit()
    return redirect('/')

@app.route('/item/<itemid>')
def item_report(itemid):
    page_object = PageObject.query.get_or_404(itemid)
    image_url = f"/static/{page_object.image_link}" 
    crafting_links = page_object.crafting_image_links.split(" ")
    for i, link in enumerate(crafting_links):
        crafting_links[i] = f"/static/{link}"
    smelting_links = page_object.smelting_image_links.split(" ")
    for i, link in enumerate(smelting_links):
        smelting_links[i] = f"/static/{link}"

    return render_template('item.html', page_object=page_object, image_url=image_url, crafting_links=crafting_links, smelting_links=smelting_links)

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
    return render_template('item_admin.html', admin_token=True, items=items, template=template)

@app.route('/newitem', methods=['POST'])
def new_item():
    new_item = PageObject(
        item_title = request.form["item_title"],
        image_link = request.form["image"],
        item_description = request.form["description"],
        iframe_video_link = request.form["iframe_video_link"],
        crafting_image_links = request.form["crafting_image_links"],
        smelting_image_links = request.form["smelting_image_links"],
        source_mod = request.form["source_mod"],
        stack_size = request.form["stack_size"],
        item_rarity = request.form["item_rarity"],
        dimension = request.form["dimension"],
        item_type = request.form["item_type"],
        minecraft_item_id = request.form["minecraft_item_id"]
    )

    db.session.add(new_item)
    db.session.commit()
    return redirect('/item/admin')

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

@app.route('/admin/items')
def all_items():
    return jsonify(get_item_json())

if __name__ == '__main__':
    app.run(debug=True, port=54913)
   