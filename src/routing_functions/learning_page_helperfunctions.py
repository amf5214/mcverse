from flask import Flask, render_template, request, redirect, url_for, json, Response, jsonify, make_response, flash
import logging
from src.models import WebPage, DivContainer, PageElement
from src.image_handling import *
from src.authentication import *

logging.basicConfig(filename='record.log', level=logging.DEBUG, filemode="w")

class LearningPageHelperFunctions():
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

    def update_page_element_image():
        if not check_if_editor(request):
            return redirect('/')
        image_id = uploadimage(request)
        page_element = PageElement.query.get_or_404(request.form["element_id"])

        page_element.text = str(image_id)
        print(f"element_id={page_element.id}. image_id={image_id}")
        db.session.commit()
        return redirect(f"/learn/{request.form['page_path']}/true")
    
    def carousel_items(element_id):
        if not check_if_editor(request):
            return redirect('/')
        return jsonify(get_carousel_items(element_id))

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