from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, redirect, url_for, flash, request, session
from app import app
from app import db
from app.forms import RegisterForm, LoginForm, PatientProfile, HealthLog, CheckupForm
from app.models import User, PatientProfile, HealthRecord, Checkup
from sqlalchemy.exc import IntegrityError

#----------------------------------------------------------------------#
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', session=session)

#----------------------------------------------------------------------#

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if request.method == "POST":
        print("POST request received")

    if form.validate_on_submit():
        print("Form validation passed")

        email = form.email.data.lower()
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered!")
            return render_template('register.html', form=form)

        hashed_password = generate_password_hash(form.password.data)

        user = User(
            email=form.email.data,
            password=hashed_password,
            role=form.role.data,
        )

        db.session.add(user)
        db.session.commit()

        print("User saved:", user.email)

        flash("Registration successful!")
        return redirect(url_for("login"))

    else:
        if request.method == "POST":
            print("Form errors:", form.errors)

    return render_template("register.html", form=form)

#----------------------------------------------------------------------#

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, form.password.data):
            session.permanent = True
            session["user_id"] = user.id
            session["user_role"] = user.role

            if user.role == "patient":
                profile = PatientProfile.query.filter_by(user_id=user.id).first()

                if profile:
                    session["user_name"] = f"{profile.first_name} {profile.last_name}"
                else:
                    session["user_name"] = user.email
            else:
                session["user_name"] = user.email
            flash(f"Welcome back, {session['user_name']}!")
            return redirect(url_for("index"))

        else:
            flash("Invalid email and/or password - please try again!")
    return render_template('login.html', form=form)

#----------------------------------------------------------------------#

@app.route('/logout')
def logout_user():
    session.clear()
    flash("You have been logged out!")
    return redirect(url_for('login'))

#----------------------------------------------------------------------#

@app.route('/patient/<int:patient_id>', methods=['GET', 'POST'])
def patient_profile(patient_id):
    profile = PatientProfile.query.filter_by(user_id=patient_id).first()
    if not profile:
        flash("Patient profile not found.")
        return redirect(url_for("index"))

    form = PatientProfile(obj=profile)

    if form.validate_on_submit():
        # Update profile fields
        profile.hypertension = form.hypertension.data
        profile.diabetes = form.diabetes.data
        profile.heart_disease = form.heart_disease.data
        profile.arthritis = form.arthritis.data
        profile.osteoporosis = form.osteoporosis.data
        profile.copd = form.copd.data
        profile.stroke = form.stroke.data
        profile.dementia = form.dementia.data
        profile.vision_problems = form.vision_problems.data
        profile.hearing_loss = form.hearing_loss.data
        profile.allergies = form.allergies.data
        profile.smoking_status = form.smoking_status.data
        profile.alcohol_consumption = form.alcohol_consumption.data
        profile.physical_activity = form.physical_activity.data

        db.session.commit()
        flash("Profile updated successfully!")
        return redirect(url_for("index"))

    return render_template("patient_profile.html", form=form, profile=profile)

#----------------------------------------------------------------------#

# display health data
def get_health_data():
    pass

# update health data
def update_health_data():
    form = HealthLog()
    if form.validate_on_submit():
        data = HealthRecord()
        form.populate_obj(data)
        try:
            db.session.add(data)
            db.session.commit()
            flash("Health data added!")
            return redirect(url_for('index'))
        except IntegrityError:         #modify this to other error in the future
            db.session.rollback()
            flash("Some error", "error")

    return render_template('updateHealth.html',form=form)


# delete health data, only on optional fields
def delete_health_data():
    pass

# send code to relative to verify that they can access patient information
def verify_auth_code():
    pass

@app.route('/check_up', methods=['GET', 'POST'])
def checkup():
    form = CheckupForm()
    if form.validate_on_submit():
        checkup_log = Checkup(
            patient_last_name=form.patient_last_name.data,
            patient_first_name=form.patient_first_name.data,
            checkup_date=form.checkup_date.data,
            medication=form.medication.data,
            dosage=form.dosage.data,
            notes=form.notes.data
        )
        db.session.add(checkup_log)
        db.session.commit()
        flash(f"Check-up details have been successfully logged!")
        return redirect(url_for('checkup'))
    checkups = Checkup.query.all()
    return render_template("checkups.html", form=form, checkups=checkups)

@app.route('/update_check_up/<int:checkup_id>', methods=['GET', 'POST'])
def update_checkup(checkup_id):
    checkup_log = Checkup.query.get_or_404(checkup_id)
    form = CheckupForm(obj=checkup_log)

    if form.validate_on_submit():
        checkup_log.patient_last_name = form.patient_last_name.data
        checkup_log.patient_first_name = form.patient_first_name.data
        checkup_log.checkup_date = form.checkup_date.data
        checkup_log.medication = form.medication.data
        checkup_log.dosage = form.dosage.data
        checkup_log.notes = form.notes.data
        db.session.commit()
        flash(f'Check-up details have been updated successfully!')
        return redirect(url_for('checkup'))
    return render_template('checkups_updating.html', form=form)

@app.route('/delete_check_up/<int:checkup_id>', methods=['GET', 'POST'])
def delete_checkup(checkup_id):
    checkup_log = Checkup.query.get_or_404(checkup_id)
    db.session.delete(checkup_log)
    db.session.commit()
    flash(f'Check-up details have been deleted successfully.')
    return redirect(url_for('checkup'))