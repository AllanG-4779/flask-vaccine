import os
import secrets

from flask import render_template, flash, redirect, url_for, request
from flask_mail import Message
from vaccination import mail
from werkzeug.utils import secure_filename
# for image resizing
from PIL import Image

from vaccination import app, bcrypt, db
from vaccination.models import User, Vaccination_Detail, Vaccine
from flask_login import login_user, current_user, login_required, logout_user
from vaccination import forms as Forms
from datetime import date, datetime
from datetime import timedelta

ALLOWED_EXTENSIONS = {'JPEG', 'JPG', 'PNG'}


@app.route('/')
@app.route('/home')
@login_required
def home():
    users = {"name": "Allan Onyang0", 'age': 43, }
    if current_user.first_name == None:
        flash("Please complete your profile first", 'warning')
        return redirect(url_for('update_profile'))
    return render_template('home.html', users=users)


@app.route('/about')
def homepage():
    return render_template("about.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash("You are already logged in, please logout to register a new account", 'info')
        return redirect(url_for('home'))
    title = "Create Account"

    form = Forms.Registration()

    if form.validate_on_submit():
        hash_pass = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(
            id=form.id.data,
            email=form.email.data,
            phone=form.phone.data,
            password=hash_pass,
        )
        db.session.add(user)
        db.session.commit()

        flash(f'Your account has been created! Just One more step!', 'success')
        return redirect(url_for('update_profile'))

    return render_template('register.html', form=form, title=title)

    # update profile details


@app.route('/complete/profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    form = Forms.Profile()
    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        user.first_name = form.firstname.data
        user.last_name = form.lastname.data
        user.county = form.county.data
        user.dob = form.dob.data
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("profile_update.html", form=form)


# Login
# View profile


@app.route('/view', methods=['GET', 'POST'])
def view_profile():
    return render_template('view_profile.html')


# update details


@app.route('/update-profile', methods=['GET', 'POST'])
@login_required
def edit_details():
    profile_image = ""
    if request.method == 'POST':
        if 'profile_image' not in request.files:
            flash("No file info")
            return redirect(url_for('home'))

        myfile = request.files['profile_image']
        # check if the file name is empty

        if myfile.filename == '':
            flash("No selected file", 'info')
            return redirect(url_for('edit_details'))

        if myfile.filename and (myfile.filename):
            enc_file = secrets.token_hex(8)
            profile_image = f'{enc_file}{myfile.filename}'
            image = Image.open(myfile)
            image.thumbnail((70, 70))

            image.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_image))

        else:
            flash('File chosen is not supported', 'info')
            return redirect(url_for('edit_details'))

        county = request.form.get('county')
        last_name = request.form.get('last_name')
        first_name = request.form.get("first_name")
        user = User.query.get(current_user.id)
        if user:
            user.county = county
            user.last_name = last_name
            user.first_name = first_name
            if profile_image != '':
                user.profile_image = profile_image

            db.session.commit()
            flash('Your details have been updated', 'success')

            return redirect(url_for('home'))

    return render_template('profile.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in", 'info')
        return redirect(url_for('home'))

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
                return redirect(url_for('update_profile'))

            # Enable the page to redirect to the initially requested page
            next = request.args.get('next')
            if next:
                return redirect(next)
            return redirect(url_for('home'))

        else:
            form.id.errors.append("Wrong username or password")
            form.password.errors.append("")
            flash("User authentication failed! Invalid credentials", 'danger')
    return render_template("login.html", form=form, title="Go Home")


# Logout user


@app.route("/logout")
def logout():
    logout_user()
    flash("Logout successful", 'success')
    return redirect(url_for('login'))


# file upload function

def checkEXtension(filename):
    if '.' in filename:
        return filename.split('.')[1] in ALLOWED_EXTENSIONS


# Allow the user to view his vaccination status
@app.route("/user/view", methods=['GET', 'POST'])
@login_required
def view_status_user():
    if current_user.is_authenticated:

        user = User.query.get(current_user.id)

        vaccine_details = Vaccination_Detail.query.filter_by(user_id=current_user.id).first()
        if vaccine_details:

            vaccine = Vaccine.query.get(vaccine_details.vaccine_id)
            result = {}

            result['remaining'] = 0
            result['next_dose'] = None

            if vaccine.doses_req > vaccine_details.dose_count:
                result['remaining'] = vaccine.doses_req - vaccine_details.dose_count

                result['next_dose'] = vaccine_details.dose_date + timedelta(
                    vaccine_details.dose_count * vaccine.dose_time)
                print(result)
            result['first'] = vaccine_details.dose_date
            result['Vaccine'] = vaccine.name
            result['dose_req'] = vaccine.doses_req

            return render_template('User_Vacc_details.html', result=result)

    return render_template("User_Vacc_details.html")


# admin operations
@app.route('/admin/vaccine', methods=['GET', 'POST'])
@login_required
def add_vaccine():
    # checks if the user is admin or not
    if not current_user.is_admin:
        flash("Your authentication details restricts access to this resource", 'danger')
        return redirect(url_for('home'))
    form = Forms.Vaccines()
    if form.validate_on_submit():
        vaccine = Vaccine(name=form.name.data.lower(),
                          origin=form.origin.data,
                          doses_req=form.doses_req.data,
                          dose_time=form.dose_time.data)
        db.session.add(vaccine)
        db.session.commit()
        flash("Successfully added", 'success')
        return redirect(url_for('home'))

    return render_template('vaccine.html', form=form)


# View the vaccines being offered
@app.route('/admin/vaccine/available', methods=['GET', 'POST'])
@login_required
def view_vaccines():
    if not current_user.is_admin:
        flash("Your authentication details restricts access to this resource", 'danger')
        return redirect(url_for('home'))

    vaccines = Vaccine.query.all()
    return render_template('vaccines_view.html', vaccines=vaccines)


@login_required
@app.route('/admin/users/vacc-details', methods=['GET', "POST"])
def user_vacc_details():
    if not current_user.is_admin:
        flash("Your authentication details restricts access to this resource", 'danger')
        return redirect(url_for('home'))
    vaccinations = Vaccination_Detail.query.all()

    # Get all the users
    complete_profile = []

    if vaccinations:

        for details in vaccinations:
            user = User.query.get(details.user_id)
            vaccine = Vaccine.query.get(details.vaccine_id)

            if details.dose_count < Vaccine.query.get(details.vaccine_id).doses_req:
                complete_profile.append(
                    {"user": details, "Name": f"{user.first_name} {user.last_name}", "Vaccine": f"{vaccine.name}",
                     'status': False})
            else:
                complete_profile.append(
                    {"user": details, "Name": f"{user.first_name} {user.last_name}", "Vaccine": f"{vaccine.name}",
                     'status': True})
    #  To get the name of the vaccine Ill create a dict

    print(complete_profile)

    return render_template('Vaccinations.html', final_details=complete_profile)


@app.route("/admin/vaccination/add-record", methods=['GET', "POST"])
@login_required
def add_vaccination():
    if not current_user.is_admin:
        flash("Your authentication details restricts access to this resource", 'danger')
        return redirect(url_for('home'))
    form = Forms.Search()

    # Search for the record if exits in the database
    if form.validate_on_submit():
        search = form.search.data
        print(search)

        if search:
            search_result = User.query.filter_by(id=search).first()
            if search_result:
                flash('User found, feel administer the vaccine', 'success')
                vaccines = Vaccine.query.all()
                user = search_result
                return render_template("vaccinate.html", user=user, form=form, vaccine=vaccines)
            else:
                flash("No user matching those details found, please register first", 'info')
                return render_template("vaccinate.html", user=None, form=form)
    if request.form.get('vaccinate') == 'vaccinate' and request.method == "POST":
        vaccine = request.form.get('vaccine')
        user_id = request.form.get('user_id')
        # Do validation
        # This if is checking if the user who is being vaccinated has already been given a dose
        # if so the number doses will be incremented by one otherwise, a new record is inserted into the database
        # Also check if the
        if Vaccination_Detail.query.filter_by(user_id=user_id).first():
            prev_record = Vaccination_Detail.query.filter_by(user_id=user_id).first()
            prev_vaccine = Vaccine.query.filter_by(id=prev_record.vaccine_id).first()

            if prev_vaccine.id != int(vaccine):
                flash(
                    f'Please choose {prev_vaccine.name},because {User.query.get(prev_record.user_id).first_name} received it as the first dose',
                    'danger')
                return render_template("vaccinate.html", user=User.query.get(prev_record.user_id), form=form,
                                       vaccine=Vaccine.query.all())
                #  check if the number of administered vaccines are equal to the required ones
            if prev_record.dose_count >= prev_vaccine.doses_req:
                flash("The individual is already fully vaccinated", 'info')
                return redirect(url_for("add_vaccination"))
            # Uppdate the dose count
            update_vacc = Vaccination_Detail.query.get(prev_record.detail_id)
            update_vacc.dose_count = update_vacc.dose_count + 1

            db.session.commit()
            # Give a feedback if the vaccination is completed
            if prev_record.dose_count == prev_vaccine.doses_req:
                flash(f"Congratulate {User.query.get(prev_record.user_id).first_name} for being fully vaccinated",
                      'success')

            flash(f"Success, Vaccination record saved! {prev_record.dose_count} ", 'success')

            return redirect(url_for('user_vacc_details'))
        new_rec = Vaccination_Detail(vaccine_id=vaccine, user_id=user_id, dose_count=1)
        db.session.add(new_rec)
        db.session.commit()
        flash("Thank you for taking your first vaccine", 'success')
        return redirect(url_for('add_vaccination'))

        # detail = Vaccination_Detail(vaccine_id=vaccine, user_id=user_id, dose_count=dose_left)
        # db.session.add(detail),
        # db.session.commit()
        # flash("detail added successfully", 'success')

    return render_template("vaccinate.html", form=form)


# send email to the user
def sendEmail(user):
    if user:
        token = user.request_token()
        msg = Message(subject="Password Reset Request", recipients=[user.email], sender='noreply@gmail.com')
        msg.body = f'Hey {user.first_name}, If you requested to change your password then click on this link to reset your password {url_for("reset_pass", token=token, _external=True)}'
        mail.send((msg))


@app.route("/forgot-password/password/reset/request/", methods=['GET', 'POST'])
def request_pass_reset_token():
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    form = Forms.EmailReset()

    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            sendEmail(user)
        flash("If the email provided exist, you'll receive reset password instructions shortly", 'info')

    return render_template('email_password.html', form=form)


@app.route("/password-reset/<token>/", methods=['GET', 'POST'])
def reset_pass(token):
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    user = User.verify_token(token)
    if not user:
        flash("Something went wrong", 'danger')
        return redirect(url_for('login'))

    form = Forms.ChangePassword()
    if form.validate_on_submit():
        new_pass = bcrypt.generate_password_hash(form.password.data)
        user.password = new_pass
        db.session.commit()
        flash("Your password changed successfully", "success")
        return redirect(url_for('login'))




    return render_template("reset_pass_form.html", form=form)

