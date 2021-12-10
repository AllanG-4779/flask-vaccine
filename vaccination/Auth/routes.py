from flask import Blueprint , render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user
from vaccination.Auth import forms as Forms
from vaccination import  bcrypt,db
from vaccination.Auth.utils import sendEmail
from vaccination.models import  User

auth = Blueprint('auth', __name__)




@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in", 'info')
        return redirect(url_for('general.home'))

    form = Forms.LoginForm()
    if form.validate_on_submit():
        # check if the user is in the db
        user = User.query.filter_by(id=form.id.data).first()
        # check that the user's password is verifiable
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('You have been successfully logged in', 'success')
            # check if the user has an updated profile
            if user.first_name == None and user.last_name == None and user.county == None:
                return redirect(url_for('regular.update_profile'))

            # Enable the page to redirect to the initially requested page
            next = request.args.get('next')
            if next:
                return redirect(next)
            return redirect(url_for('general.home'))

        else:
            form.id.errors.append("Wrong username or password")
            form.password.errors.append("")
            flash("User authentication failed! Invalid credentials", 'danger')
    return render_template("login.html", form=form, title="Go Home")


# Logout user


@auth.route("/logout")
def logout():
    logout_user()
    flash("Logout successful", 'success')
    return redirect(url_for('auth.login'))



@auth.route("/forgot-password/password/reset/request/", methods=['GET', 'POST'])
def request_pass_reset_token():
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    form = Forms.EmailReset()

    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            sendEmail(user)
        flash("If the email provided exist, you'll receive reset password instructions shortly", 'info')

    return render_template('email_password.html', form=form)


@auth.route("/password-reset/<token>/", methods=['GET', 'POST'])
def reset_pass(token):
    if current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    user = User.verify_token(token)
    if not user:
        flash("Something went wrong", 'danger')
        return redirect(url_for('auth.login'))

    form = Forms.ChangePassword()
    if form.validate_on_submit():
        new_pass = bcrypt.generate_password_hash(form.password.data)
        user.password = new_pass
        db.session.commit()
        flash("Your password changed successfully", "success")
        return redirect(url_for('auth.login'))




    return render_template("reset_pass_form.html", form=form)
