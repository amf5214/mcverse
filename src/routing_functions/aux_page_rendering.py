from flask import Flask, render_template, request, redirect, url_for, json, Response, jsonify, make_response, flash
import logging
from src.authentication import get_account
from src.logging_manager import create_logger

logger = create_logger("aux_page")

class AuxPageRendering():

    def __init__(self):
        pass

    def aboutus():
        return render_template('aboutus.html', useraccount=get_account(request))

    def contactus():
        return render_template('contactus.html', useraccount=get_account(request))

    