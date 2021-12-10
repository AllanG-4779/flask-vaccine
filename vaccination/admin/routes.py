from flask import Blueprint, redirect, url_for, render_template, request
from flask import flash
from vaccination.admin import forms as Forms
from vaccination.models import *
from vaccination import db
from flask_login import current_user, login_required

admin = Blueprint('admin', __name__)

# admin operations
@admin.route('/admin/vaccine', methods=['GET', 'POST'])
@login_required
def add_vaccine():
    # checks if the user is admin or not
    if not current_user.is_admin:
        flash("Your authentication details restricts access to this resource", 'danger')
        return redirect(url_for('general.home'))
    form = Forms.Vaccines()
    if form.validate_on_submit():
        vaccine = Vaccine(
                          name=form.name.data.lower(),
                          origin=form.origin.data,
                          doses_req=form.doses_req.data,
                          dose_time=form.dose_time.data
                          )
        db.session.add(vaccine)
        db.session.commit()
        flash("Successfully added", 'success')
        return redirect(url_for('admin.view_vaccines'))

    return render_template('vaccine.html', form=form)


# View the vaccines being offered
@admin.route('/admin/vaccine/available', methods=['GET', 'POST'])
@login_required
def view_vaccines():
    if not current_user.is_admin:
        flash("Your authentication details restricts access to this resource", 'danger')
        return redirect(url_for('general.home'))

    vaccines = Vaccine.query.all()
    return render_template('vaccines_view.html', vaccines=vaccines)


@login_required
@admin.route('/admin/users/vacc-details', methods=['GET', "POST"])
def user_vacc_details():
    if not current_user.is_admin:
        flash("Your authentication details restricts access to this resource", 'danger')
        return redirect(url_for('general.home'))
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


@admin.route("/admin/vaccination/add-record", methods=['GET', "POST"])
@login_required
def add_vaccination():
    if not current_user.is_admin:
        flash("Your authentication details restricts access to this resource", 'danger')
        return redirect(url_for('genearal.home'))
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
                return redirect(url_for("admin.add_vaccination"))
            # Uppdate the dose count
            update_vacc = Vaccination_Detail.query.get(prev_record.detail_id)
            update_vacc.dose_count = update_vacc.dose_count + 1

            db.session.commit()
            # Give a feedback if the vaccination is completed
            if prev_record.dose_count == prev_vaccine.doses_req:
                flash(f"Congratulate {User.query.get(prev_record.user_id).first_name} for being fully vaccinated",
                      'success')

            flash(f"Success, Vaccination record saved! {prev_record.dose_count} ", 'success')

            return redirect(url_for('admin.user_vacc_details'))
        new_rec = Vaccination_Detail(vaccine_id=vaccine, user_id=user_id, dose_count=1)
        db.session.add(new_rec)
        db.session.commit()
        flash("Thank you for taking your first vaccine", 'success')
        return redirect(url_for('admin.add_vaccination'))

        # detail = Vaccination_Detail(vaccine_id=vaccine, user_id=user_id, dose_count=dose_left)
        # db.session.add(detail),
        # db.session.commit()
        # flash("detail added successfully", 'success')

    return render_template("vaccinate.html", form=form)

