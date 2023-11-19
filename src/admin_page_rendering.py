from flask import render_template, request, redirect
from src.models import db, PageObject, ItemClass, PermissionsRequest
from src.authentication import check_if_admin, get_account
from src.image_handling import create_image

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
