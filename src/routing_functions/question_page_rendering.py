from flask import Flask, render_template, request, redirect, url_for, json, Response, jsonify, make_response, flash
import logging
from src.models import FrequentlyAskedQuestion
from src.image_handling import *
from src.authentication import *
from src.logging_manager import create_logger

logger = create_logger("question_page")

class FAQPageRendering():
    def new_question():
        """View function that handles a request to add a new question to the FrequentlyAskedQuestion table

        Accepts a post request in the form of an html form submission and uses it to create a new question
        in the FrequentlyAskedQuestion table

        Return: Redirect object that sends the user to the home path
        
        """

        new_question = FrequentlyAskedQuestion(author_user=str(request.form["username"]), question=str(request.form["question"]))
        
        db.session.add(new_question)
        db.session.commit()
        return redirect('/')