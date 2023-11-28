from flask import Flask, render_template, request, redirect, url_for, json, Response, jsonify, make_response, flash
import logging
from src.authentication import get_account
from src.logging_manager import log_message

class AuxPageRendering():

    def aboutus():
        """View function that handles a request to access the about us page

        Function to render aboutus.html template

        Return: Rendered template with css and js included
        
        """

        return render_template('aboutus.html', useraccount=get_account(request))

    def contactus():
        """View function that handles a request to access the contact us page

        Function to render contactus.html template

        Return: Rendered template with css and js included
        
        """

        return render_template('contactus.html', useraccount=get_account(request))

    