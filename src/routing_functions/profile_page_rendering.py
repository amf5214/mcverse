from flask import Flask, render_template, request, redirect, url_for, json, Response, jsonify, make_response, flash
import logging
from sqlalchemy.orm.exc import NoResultFound

from src.authentication import *
from src.image_handling import *
from src.logging_manager import create_logger
from src.models import AccountPermission, AuthAccount, UserAccount, PermissionsRequest, db

profile_logger = create_logger("profile_page")

Permission_values = ["Admin", "Edit_Pages", "Add_Pages"]

class Permission():
        def __init__(self, has, name):
            self.has=has
            self.name=name

class ProfilePageRendering():
    def signin():
        """View function that renders the signin/signup page

        Renders the page used to sign in and sign up for an account

        Return: Rendered view from signinup.html template with js and css code 
        """

        profile_logger.info('Sign in/Sign up page rendered')
        return render_template('signinup.html', useraccount=get_account(request))

    def failed_signin():
        """View function that renders the signin/signup page with error message due to a failed sign in

        Renders the page used to sign in and sign up for an account but adds the error message variable due to a failed sign in attempt

        Return: Rendered view from signinup.html template with js and css code 
        """

        profile_logger.info('Failed sign in occured')
        return render_template('signinup.html', message="Username/Password Invalid. Please try again.", useraccount=get_account(request))

    def profile():
        """View function that renders the profile page

        Renders the page used to view user profile. Checks to ensure that there is a user signed in and 
        redirects to sign in page if no user is signed in

        Return: Rendered view from profile.html template with js and css code 
        """

        profile_logger.info('Profile page rendered')
        account = get_account(request)
        profile_logger.info(f'Account {account} rendered')
        if account.full_name != "No Account":
            profile_logger.info(f'Account id={account.id} accessed')
            permissions = db.session.execute(db.select(AccountPermission).filter_by(account_id=account.id)).scalars()
            permissions_gen = []
            remaining_permissions = [z for z in Permission_values]
            for x in permissions:
                perm_type = x.permission_type
                permissions_gen.append(Permission(has=True, name=perm_type))
                remaining_permissions.remove(perm_type)
            for y in remaining_permissions:
                permissions_gen.append(Permission(has=False, name=y))
            return render_template("profile.html", useraccount=account, permissions=permissions_gen)
        else:
            return redirect('/signin/home')

# @app.route('/profile/introduction')
# def introduction():
#     return render_template("introduction.html", useraccount=get_account(request))


    def signinattempt():
        """View function that handles a sign in attempt

        Takes a post request in the form of an html form submission. If the signin works then user redirected to home path
        otherwise user will be redirected to failed sign in path.

        Return: Redirect object that moves the user to the correct page based off accuracy of the submitted form 
        """
        try:
            given_pass = request.form["logpass"]

            auth_account = db.session.execute(db.select(AuthAccount).filter_by(email_account=request.form["logemail"])).scalar_one()

            if(validate_password(given_pass, auth_account.hash_password)):
                token_data = encode_auth_token(request.form["logemail"])
                auth_account.auth_token = token_data[0]
                auth_account.token_key = token_data[1]
                db.session.commit()
                response = make_response(redirect("/"))
                response.set_cookie("token", auth_account.auth_token)
                return response
            else:
                return redirect("/signin/failed")
        except NoResultFound: 
            return redirect("/signin/failed")
    
    def sign_out():
        response = make_response(redirect("/"))
        response.set_cookie("token", "None")
        return response

    def create_new_account():
        if request.form["logname"]=="No Account":
            return render_template('signinup.html', signupmessage="Name entry is invalid", useraccount=get_account(request))

        password = create_password(request.form["logpass"])
        token_data = encode_auth_token(str(request.form["logusername"]))
        auth_account = AuthAccount(email_account=request.form["logemail"],hash_password=password, auth_token=token_data[0], token_key=token_data[1])

        db.session.add(auth_account)

        db.session.commit()

        authaccountrec = db.session.execute(db.select(AuthAccount).filter_by(email_account=request.form["logemail"])).scalar_one()
        try:   
            birthdatedata=birthdate=request.form["logbirthdate"].split("-")
            birthdate = date(int(birthdatedata[0]), int(birthdatedata[1]), int(birthdatedata[2]))
            account = UserAccount(username=request.form["logusername"],full_name=request.form["logname"],birthdate=birthdate,auth_account_id=authaccountrec.id)
        except ValueError:
                    account = UserAccount(username=request.form["logusername"],full_name=request.form["logname"],auth_account_id=authaccountrec.id)
        db.session.add(account)
        db.session.commit()
        return redirect('/signin/home')

    def create_permission_request(permission, accountid):
        account = UserAccount.query.get_or_404(accountid)
        request = PermissionsRequest(account_id=accountid, permission_type=permission, username=account.username, grant_date=date.today())
        db.session.add(request)
        db.session.commit()
        return redirect('/profile')

    def profileimageupdate():
        image_id = uploadimage(request)
        picture_account = UserAccount.query.get_or_404(request.form["user_id"])

        picture_account.account_image_link = str(image_id)
        db.session.commit()
        return redirect("/profile")
    
    def updateprofileattribute():
        request_data = request.get_json()
        account_id = request_data['accountId']
        fulfilled = False
        if verify_account_match(request, account_id):
            attribute = request_data['attribute']
            new_value = request_data['newValue']
            account = db.session.execute(db.select(UserAccount).filter_by(id=account_id)).scalar_one()
            if attribute == "name":
                account.full_name = new_value
                fulfilled = True
            elif attribute == "username":
                account.username = new_value
                fulfilled = True
            elif attribute == "birthdate":
                try:
                    new_value_2 = new_value.replace('-', '/')
                    birthdatedata = new_value_2.split('/')
                    birthdate = date(int(birthdatedata[2]), int(birthdatedata[1]), int(birthdatedata[0]))
                    account.birthdate = birthdate
                    fulfilled = True
                except Exception as e:
                    print(f"Error during birthdate update. Provided={new_value} \n {e}")
            elif attribute == "bio":
                account.bio = new_value
                fulfilled = True
            elif attribute == "experience":
                account.experience = new_value
                fulfilled = True
            db.session.commit()
    
        if fulfilled:
            body = {"fulfillable": True}
            response_obj = make_response(jsonify(body))
            response_obj.headers.set('content-type', 'text/plain')
            return response_obj
        else:
            body = {"fulfillable": False}
            response_obj = make_response(jsonify(body))
            response_obj.headers.set('content-type', 'text/plain')
            return response_obj
