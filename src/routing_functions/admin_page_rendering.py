from flask import Flask, render_template, request, redirect, url_for, json, Response, jsonify, make_response, flash
import logging

from src.models import *
from src.authentication import *
from src.image_handling import *

logging.basicConfig(filename='record.log', level=logging.DEBUG, filemode="w")

def get_item_classes():
        item_classes = ItemClass.query.order_by(ItemClass.id).all()
        return item_classes

def get_item_json():
        objects = PageObject.query.order_by(PageObject.id).all()
        json_data = []
        for x in objects:
            json_data.append([x.item_title, x.id])
        return {"jdata": json_data}

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
    
    def permissions_requests_admin():
        if not check_if_admin(request):
            return redirect('/')
        requests = PermissionsRequest.query.filter_by(is_visible=True).order_by(PermissionsRequest.id).all()
        return render_template("permissions_request_admin.html", admin_token=True, prequests=requests, useraccount=get_account(request))

    def deny_request(requestid):
        if not check_if_admin(request):
            return redirect('/')
        permission_request = PermissionsRequest.query.get_or_404(requestid)
        permission_request.is_visible = False
        db.session.commit()
        return redirect('/permissions/requests/admin')

    def approve_request(requestid):
        if not check_if_admin(request):
            return redirect('/')
        permission_request = PermissionsRequest.query.get_or_404(requestid)
        permission_request.is_visible = False
        db.session.add(AccountPermission(permission_type=permission_request.permission_type, account_id=permission_request.account_id))
        db.session.commit()
        return redirect('/permissions/requests/admin')

    def uploadnewimage():
        if not check_if_admin(request):
            return redirect('/')
        image_id = uploadimage(request)
        return redirect('/')

    def createwebpage():
        if not check_if_admin(request):
            return redirect('/')
        new_page = WebPage(text=request.form["text"], div_title=request.form["div_title"], path=request.form["path"].lower(), directory=request.form["directory"].lower())
        db.session.add(new_page)
        db.session.commit()
        return redirect('/managewebpages')

    def deletewebpage(pageid):
        if not check_if_admin(request):
            return redirect('/')

        page = db.session.execute(db.select(WebPage).filter_by(id=pageid)).scalar_one()
        db.session.delete(page)
        db.session.commit()
        return redirect('/managewebpages')

    def managewebpages():
        if not check_if_admin(request):
            return redirect('/')
        pages = WebPage.query.order_by(WebPage.id).all()
        return render_template('webpagehome.html', pages=pages, useraccount=get_account(request))

    def adminuploadimage():
        if not check_if_admin(request):
            return redirect('/')
        useraccount = get_account(request)
        test = permission_validation("Admin", useraccount.id)
        if test:
            return render_template('uploadimage.html', useraccount=useraccount, baseimage=create_image_item(2))
        else:
            return redirect('/')

    def all_items():
        return jsonify(get_item_json())

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

    def itemclasshome():
        if not check_if_admin(request):
            return redirect('/')
        return render_template('itemclasshome.html', pagename="Item Class", admin_token=True, useraccount=get_account(request), itemclasses=get_item_classes())

    def newitemclass():
        if not check_if_admin(request):
                return redirect('/')
        
        item_class = ItemClass(name=request.form['class-name'])
        db.session.add(item_class)
        db.session.commit()
        return redirect('/itemclasshome')

    def deleteitemclass(classid):
        if not check_if_admin(request):
            return redirect('/')
        itemclass = ItemClass.query.get_or_404(classid)
        db.session.delete(itemclass)
        db.session.commit()
        return redirect('/itemclasshome')