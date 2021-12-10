from flask import Blueprint,redirect, request, flash, url_for, render_template
from vaccination import  bcrypt, db, app
from vaccination.Regular import  forms as Forms
from vaccination.models import  User
from flask_login import current_user, login_required
import secrets, os
from datetime import timedelta
from vaccination.models import  *

from PIL import  Image


from vaccination.Regular import ALLOWED_EXTENSIONS

regular = Blueprint('regular', __name__)

@regular.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash("You are already logged in, please logout to register a new account", 'info')
        return redirect(url_for('general.home'))
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
        return redirect(url_for('regular.update_profile'))

    return render_template('register.html', form=form, title=title)

    # update profile details


@regular.route('/complete/profile', methods=['GET', 'POST'])
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
        return redirect(url_for('general.home'))

    return render_template("profile_update.html", form=form)


# Login
# View profile


@regular.route('/view', methods=['GET', 'POST'])
def view_profile():
    return render_template('view_profile.html')


# update details


@regular.route('/update-profile', methods=['GET', 'POST'])
@login_required
def edit_details():
    profile_image = ""
    if request.method == 'POST':
        if 'profile_image' not in request.files:
            flash("No file info")
            return redirect(url_for('general.home'))

        myfile = request.files['profile_image']
        # check if the file name is empty

        if myfile.filename == '':
            flash("No selected file", 'info')
            return redirect(url_for('regular.edit_details'))

        if myfile.filename and myfile.filename.split('.')[-1]  in ALLOWED_EXTENSIONS:
            enc_file = secrets.token_hex(8)
            profile_image = f'{enc_file}{myfile.filename}'
            image = Image.open(myfile)
            image.thumbnail((70, 70))

            image.save(os.path.join(app.config['UPLOAD_FOLDER'], profile_image))

        else:
            flash('File chosen is not supported', 'info')
            return redirect(url_for('regular.edit_details'))

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

            return redirect(url_for('general.home'))

    return render_template('profile.html')


@regular.route("/user/view", methods=['GET', 'POST'])
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

