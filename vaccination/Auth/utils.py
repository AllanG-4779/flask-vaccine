from flask_mail import Message
from flask import  url_for
from vaccination import  mail
def sendEmail(user):
    if user:
        token = user.request_token()
        msg = Message(subject="Password Reset Request", recipients=[user.email], sender='noreply@gmail.com')
        msg.body = f'Hey {user.first_name}, If you requested to change your password then click on this link to reset your password {url_for("auth.reset_pass", token=token, _external=True)}'
        mail.send((msg))

