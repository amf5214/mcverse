from flask import render_template, redirect, request
import logging

from src.models import PageObject
from src.image_handling import *
from src.authentication import *

logging.basicConfig(filename='record.log', level=logging.DEBUG, filemode="w")

def get_item_classes():
        item_classes = ItemClass.query.order_by(ItemClass.id).all()
        return item_classes

class ItemPageRendering():
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

    def delete_item(itemid):
        db.session.delete(PageObject.query.get_or_404(itemid))
        db.session.commit()
        return redirect('/item/admin')

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

    def itemimageupdate():
        if not check_if_editor(request):
            return redirect('/')
        image_id = uploadimage(request)
        picture_item = PageObject.query.get_or_404(request.form["item_id"])

        picture_item.image_link = str(image_id)
        db.session.commit()
        return redirect(f"/item/{request.form['item_id']}/false")

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