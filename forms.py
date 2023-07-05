from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email



class GroupForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    description = StringField('description')


class SignupForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired(), Length(min=5, max=25)])
    email = EmailField(label="Email", validators=[DataRequired(), Email()])
    password = PasswordField(label="Password", validators=[DataRequired(), Length(min=4, max=12), EqualTo("confirm_password")])
    confirm_password = PasswordField(label="Confirm Password", validators=[DataRequired(),  Length(min=4, max=12),  EqualTo("password")])
    submit=SubmitField(label='Sign Up')


class LoginForm(FlaskForm):
    email = EmailField(label="Email", validators=[DataRequired(), Email()])
    password = PasswordField(label="Password", validators=[DataRequired(), Length(min=4, max=12)])
    submit = SubmitField(label='Login')


class ResetRequestForm(FlaskForm):
    email = EmailField(label="Email", validators=[DataRequired(), Email()])
    submit = SubmitField(label='Reset Password' , validators=[DataRequired()])


class ResetPasswordForm(FlaskForm):
    password = PasswordField(label="Password", validators=[DataRequired(), Length(min=4, max=12)])
    confirm_password = PasswordField(label=" Confirm Password", validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField(label='Change Password',validators=[DataRequired()])
