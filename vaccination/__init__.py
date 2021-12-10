import os.path as path

from flask import Flask
from flask.helpers import url_for
from flask.scaffold import F
from flask_sqlalchemy import  SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
app = Flask(__name__)
app.config['SECRET_KEY'] = "myAp838ancdoolk3r3o4038433jflfsdfjdfd844"
app.config['SQLALCHEMY_DATABASE_URI'] ="mysql://root:cnd80751xh@localhost:3306/vaccination_registry"
app.config['UPLOAD_FOLDER'] = path.join(path.dirname(path.realpath(__file__)),'static/imgs')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# set the email
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_USERNAME'] = 'allang4779@gmail.com'
app.config['MAIL_PASSWORD'] = 'UgLgHQyE01.COM'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

# set the application to use the bcrypt algorithm to hash passwords
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
# To enable the flask know where to redirect if login is not fullfilled do the following
login_manager.login_view = "login"
login_manager.login_message = "You are not logged in"
login_manager.login_message_category = 'info'

# Make sure the routes are imported after the app is initialized because it is required in the routes file
# Therfore to avoid the circular imports, use the format specified

from vaccination import routes

