#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import ValidationError, StopValidation, DataRequired
from flask import flash, Flask

#--------------------------------OUR DEPENDENCIES--------------------------------#
from userManager import UserManager


class ForgotPwdForm(FlaskForm, UserManager):
    """Generates a forgot password form to authenticate and change password"""
    #-----------------------------------Form Fields-----------------------------------#
    username = StringField('Username', validators=[DataRequired()])
    new_password = PasswordField('New Password',  validators=[DataRequired()])
    submit = SubmitField('Reset Password')

    def __init__(self, flaskApp: Flask, user_manager: UserManager, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.user_manager = user_manager
        cls = self.__class__ # get reference to cls
        cls.username = StringField('Username', validators=[DataRequired(), self.checkUsername])
        cls.new_password = PasswordField('New Password',  validators=[DataRequired()])

    def checkUsername(self, form, field)->bool():
        """
            \n@Returns True = Exists
        """
        # check that username is not already taken
        if not self.user_manager.does_username_exist(form.username.data):
            errMsg = "Invalid username or password"
            # flash(errMsg, "is-danger")
            raise StopValidation(message=errMsg) # prints under box
        else:
            return True
