from flask import Blueprint,request,redirect,flash, render_template, url_for
from flask_login import login_required,current_user


general = Blueprint('general', __name__)


@general.route('/')
@general.route('/home')
@login_required
def home():
    users = {"name": "Allan Onyang0", 'age': 43, }
    if current_user.first_name == None:
        flash("Please complete your profile first", 'warning')
        return redirect(url_for('regular.update_profile'))
    return render_template('home.html', users=users)

@general.route('/about')
def homepage():
    return render_template("about.html")
