from flask import Flask, render_template, request, redirect, url_for, json, Response, jsonify, make_response, flash
import logging 
from src.models import WebPage, DivContainer, PageElement
from src.image_handling import *
from src.authentication import *

logging.basicConfig(filename='record.log', level=logging.DEBUG, filemode="w")

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

class LearningPageRendering():
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
            