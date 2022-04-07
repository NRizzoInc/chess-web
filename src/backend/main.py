#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------STANDARD DEPENDENCIES-----------------------------#
import os
import sys
import webbrowser # allows opening of new tab on start
import argparse # cli paths
import logging # used to disable printing of each POST/GET request
import pathlib
from pathlib import Path
import secrets
import getpass
from datetime import  datetime
from typing import TypedDict, List, Tuple

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
import flask
from flask import Flask, session, render_template, request, redirect, flash, url_for, jsonify
import werkzeug.serving # needed to make production worthy app that's secure

# decorate app.route with "@login_required" to make sure user is logged in before doing anything
from flask_login import login_user, current_user, login_required, logout_user


#--------------------------------Project Includes--------------------------------#
from user import User
from userManager import UserManager
from flask_helpers import FlaskHelper, flash_print, is_json, is_form, is_static_req, clear_flashes
from registrationForm import RegistrationForm
from loginForm import LoginForm
from forgotPasswordForm import ForgotPwdForm

class ChessWeb(UserManager):
    def __init__(self, port: int, is_debug: bool, user: str, pwd: str, db: str, db_host: str):
        self._app = Flask("Chess Server App")
        self._app.config["TEMPLATES_AUTO_RELOAD"] = True # refreshes flask if html files change
        self._app.config['SECRET_KEY'] = secrets.token_urlsafe(16)

        UserManager.__init__(self, self._app, user, pwd, db, db_host)
        self.flask_helper = FlaskHelper(self._app, port)

        # get the paths relative to this file
        backend_dir = Path(__file__).parent.resolve()
        src_dir = backend_dir.parent
        frontend_dir = src_dir / 'frontend'
        template_dir = frontend_dir / 'templates'
        static_dir = frontend_dir / "static"
        self._app.static_folder = str(static_dir)
        self._app.template_folder = str(template_dir)

        # logging
        self._logger = logging.getLogger("werkzeug")

        self._is_debug = is_debug
        self._host = '0.0.0.0'
        self._port = port
        logLevel = logging.INFO if self._is_debug == True else logging.ERROR
        self._logger.setLevel(logLevel)

        # create routes (and print routes)
        self.generateRoutes()
        self.flask_helper.print_routes()


        is_threaded = True

        # start blocking main web server loop (nothing after this is run)
        if self._is_debug:
            self._app.run(host=self._host, port=self._port, debug=self._is_debug, threaded=is_threaded)
        else:
            # FOR PRODUCTION
            werkzeug.serving.run_simple(
                hostname=self._host,
                port=self._port,
                application=self._app,
                use_debugger=self._is_debug,
                threaded=is_threaded
            )

    def generateRoutes(self):
        """Wrapper for all the url route generation"""
        self.createUserPages()

    def createUserPages(self):
        """These are all the GET'able / rendered pages for the user"""

        @self._app.route("/", methods=["GET"])
        @self._app.route("/index", methods=["GET"])
        def index():
            return render_template("index.html")


        # https://flask-login.readthedocs.io/en/latest/#login-example
        @self._app.route("/user/login", methods=["GET", "POST"], defaults={'username': None, 'password': None, 'rememberMe': None})
        def login(username: str, password: str, rememberMe: bool):
            # dont login if already logged in
            if current_user.is_authenticated: return redirect(url_for('index'))

            form = LoginForm(self._app, self)

            def login_fail(msg=""):
                flash_print(f'Invalid Username or Password!', "is-danger")
                # print(msg)
                return redirect(url_for('login'))

            username = None
            password = None
            rememberMe = None
            if request.method == "GET":
                return render_template("login.html", title="ChessWeb Login", form=form)
            elif request.method == "POST":
                # print("Login Form Params: username = {0}, password = {1}, rememberMe={2}".format(
                #     form.username.data, form.password.data, form.rememberMe.data
                # ))

                if form.validate_on_submit():

                    # username & pwd must be right at this point, so login
                    # https://flask-login.readthedocs.io/en/latest/#flask_login.LoginManager.user_loader
                    # call loadUser() / @user_loader in userManager.py
                    user_id = self.get_user_id(form.username.data)
                    user = User(user_id)
                    login_user(user, remember=form.rememberMe.data)

                    # flash messages for login
                    flash_print("Login Successful!", "is-success")
                    flash_print(f"user id: {user_id}", "is-info") # format str safe bc not user input

                    # route to original destination
                    next = flask.request.args.get('next')
                    isNextUrlBad = next == None or not is_safe_url(next, self._urls)
                    if isNextUrlBad:
                        return redirect(url_for('index'))
                    else:
                        return redirect(next)

            # on error, keep trying to login until correct
            return redirect(url_for("login"))



        @self._app.route("/user/signup", methods=["GET", "POST"])
        def signup(fname:str, lname:str, username:str, password:str, password2: str):
            if current_user.is_authenticated: return redirect(url_for('index'))

            form = RegistrationForm(self._app, user_manager=self)

            def signup_fail(msg=""):
                flash_print(f'Signup Failed! {msg}', "is-danger")
                # try again
                return redirect(url_for("signup"))
            def signup_succ(username, msg=""):
                # since validated, always return to login
                flash_print(f"Signup successful for {username}! {msg}", "is-success")
                return redirect(url_for("login"))

            if request.method == "POST":
                if is_form and form.validate_on_submit():
                    fname = form.fname.data
                    lname = form.lname.data
                    username = form.username.data
                    pwd = form.password.data
                elif is_form:
                    return signup_fail()

                add_res = self.add_user(fname, lname, username, pwd)
                if(add_res != -1):
                    return signup_succ(username)
                else:
                    return signup_fail(msg="failed to add user to db")

            elif request.method == "POST":
                print("Signup Validation Failed")

            # on GET or failure, reload
            return render_template('signup.html', title="ChessWeb Signup", form=form)


        @self._app.route("/user/forgot_password", methods=["GET", "POST"])
        def forgotPassword(uname: str, new_pwd: str):
            form = ForgotPwdForm(self._app, user_manager=self)
            update_res = True

            if request.method == "POST":
                if is_form and form.validate_on_submit():
                    uname = form.username.data
                    new_pwd = form.new_password.data
                elif is_form:
                    # flash_print(f"Password Reset Fail! Bad form", "is-warning")
                    uname = new_pwd = None

                if uname != None and new_pwd != None:
                    update_res = self.update_pwd(uname, new_pwd)

                    if update_res == 1:
                        flash_print("Password Reset Successful", "is-success")
                        return redirect(url_for('index'))
                print(f"Password Reset Failed: {uname} w/ {new_pwd}")
                flash("Password Reset Failed", "is-danger")

            # on GET or failure, reload
            return render_template("forgot_password.html", title="ChessWeb Reset Password", form=form)

        @self._app.route("/user/logout", methods=["GET", "POST"])
        @login_required
        def logout():
            logout_user()
            flash("Successfully logged out!", "is-success")
            return redirect(url_for("login"))




if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Start up a web app GUI for the ChessWeb DB App")
    parser.add_argument(
        "-p", "--port",
        type=int,
        required=False,
        help="The port to run the web app from",
        default=10225
    )

    # defaults debugMode to false (only true if flag exists)
    parser.add_argument(
        "--debugModeOn",
        action="store_true",
        dest="debugMode",
        required=False,
        help="Use debug mode for development environments",
        default=False
    )
    parser.add_argument(
        "--debugModeOff",
        action="store_false",
        dest="debugMode",
        required=False,
        help="Dont use debug mode for production environments",
        default=True
    )

    parser.add_argument(
        "-db_u", "--db_username",
        required=False,
        # sometimes this is also root
        default="capstone",
        dest="db_user",
        help="The username for the Database"
    )

    parser.add_argument(
        "-pwd", "--password",
        required=False, # but if not provided asks for input
        default=None,
        dest="pwd",
        help="The password for the Database"
    )
    parser.add_argument(
        "-d", "--db",
        required=False,
        default="ChessWeb",
        dest="db",
        help="The name of the database to connect to"
    )

    parser.add_argument(
        "-dbh", "--database_host",
        required=False,
        default="localhost",
        dest="db_host",
        help="Set the host ip address of the database (can be localhost)"
    )

    # Actually Parse Flags (turn into dictionary)
    args = vars(parser.parse_args())

    # ask for input if password not given
    # if args["pwd"] == None:
    #     pass_msg = "Enter the password for user '"
    #     pass_msg += str(args["db_user"])
    #     pass_msg += "' for the database '"
    #     pass_msg += str(args["db"])
    #     pass_msg += "': "
    #     args["pwd"] = getpass.getpass(pass_msg)

    # start app
    app = ChessWeb(args["port"], args["debugMode"], args["db_user"], args["pwd"], args["db"], args["db_host"])
