from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, URL
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


from wtforms import TextAreaField, SelectField
from wtforms.validators import Length
from flask_wtf.file import FileField, FileAllowed

class LinkForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired(), URL(message='Please enter a valid URL.')])
    submit = SubmitField('Add Link')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    bio = TextAreaField('About me', validators=[Length(min=0, max=140)])
    payment_link = StringField('Payment Link (e.g., Paystack, Flutterwave)')
    theme = SelectField('Theme', choices=[
        ('default.css', 'Default'),
        ('dark.css', 'Dark (Premium)'),
        ('light.css', 'Light (Premium)'),
        ('neon_glow.css', 'Neon Glow (Premium)'),
        ('minimalist_monochrome.css', 'Minimalist Monochrome (Premium)'),
        ('gradient_bliss.css', 'Gradient Bliss (Premium)'),
        ('retro_pixel.css', 'Retro Pixel (Premium)'),
        ('eco_natural.css', 'Eco Natural (Premium)')
    ])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
