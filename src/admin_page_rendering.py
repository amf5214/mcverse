from flask import render_template, request
from src.models import db, PageObject, ItemClass
from src.authentication import check_if_admin, get_account

def get_item_classes():
        item_classes = ItemClass.query.order_by(ItemClass.id).all()
        return item_classes

class AdminPageRendering():
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
