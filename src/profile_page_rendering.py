from flask import Flask, render_template, request, redirect, url_for, json, Response, jsonify, make_response, flash

from src.authentication import get_account
from src.models import AccountPermission, AuthAccount, UserAccount

class Permission():
        def __init__(self, has, name):
            self.has=has
            self.name=name

class ProfilePageRendering():
    def signin():
        return render_template('signinup.html', useraccount=get_account(request))

    def failed_signin():
        return render_template('signinup.html', message="Username/Password Invalid. Please try again.", useraccount=get_account(request))

    def profile():
        account = get_account(request)
        if account.full_name != "No Account":
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
        try:
            given_pass = request.form["logpass"]

            auth_account = db.session.execute(db.select(AuthAccount).filter_by(email_account=request.form["logemail"])).scalar_one()

            if(validate_password(given_pass, auth_account.hash_password)):
                auth_account.auth_token = encode_auth_token(request.form["logemail"])
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
        token = encode_auth_token(str(request.form["logusername"]))
        auth_account = AuthAccount(email_account=request.form["logemail"],hash_password=password, auth_token=token)

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