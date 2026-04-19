from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, redirect, url_for, flash, request, session
from app import app
from app import db
from app.forms import RegisterForm, LoginForm, PatientProfile, HealthLog, CheckupForm, RelativeApprovalForm
from app.models import User, PatientProfile, HealthLog, Checkup, RelativeApproval
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

        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            date_of_birth=form.date_of_birth.data,
            email=form.email.data,
            role=form.role.data,
        )

        user.set_password(form.password.data)

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

        if user and check_password_hash(user.password_hash, form.password.data):
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
        data = HealthLog()
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

#----------------------------------------------------------------------#
# RELATIVE APPROVAL MANAGEMENT (Story S3)
#----------------------------------------------------------------------#

@app.route('/manage_relatives', methods=['GET', 'POST'])
def manage_relatives():
    """
    Allow patients to view and manage their approved relatives.
    Patients can approve new relatives to access their health records.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('user_role') != 'patient':
        flash("Only patients can manage relatives.")
        return redirect(url_for('index'))

    # Get the patient's profile
    patient_profile = PatientProfile.query.filter_by(user_id=session['user_id']).first()
    if not patient_profile:
        flash("Patient profile not found.")
        return redirect(url_for('index'))

    form = RelativeApprovalForm()

    if form.validate_on_submit():
        # Check if the relative exists in the system
        relative_user = User.query.filter_by(email=form.relative_email.data.lower()).first()

        if not relative_user:
            flash(f"No user found with email: {form.relative_email.data}. Please ensure the relative has registered.")
            return render_template('manage_relatives.html', form=form, approved_relatives=patient_profile.approved_relatives)

        # Check if the relative is actually a relative
        if relative_user.role != "relative":
            flash(f"User {form.relative_email.data} is not registered as a relative.")
            return render_template('manage_relatives.html', form=form, approved_relatives=patient_profile.approved_relatives)

        # Check if already approved
        existing_approval = RelativeApproval.query.filter_by(
            patient_id=patient_profile.id,
            relative_id=relative_user.id
        ).first()

        if existing_approval:
            flash(f"This relative is already approved.")
            return render_template('manage_relatives.html', form=form, approved_relatives=patient_profile.approved_relatives)

        # Create new approval
        try:
            new_approval = RelativeApproval(
                patient_id=patient_profile.id,
                relative_id=relative_user.id
            )
            db.session.add(new_approval)
            db.session.commit()
            flash(f"Successfully approved {form.relative_email.data} as a relative!")
            return redirect(url_for('manage_relatives'))
        except IntegrityError:
            db.session.rollback()
            flash("An error occurred while approving the relative. Please try again.")
            return render_template('manage_relatives.html', form=form, approved_relatives=patient_profile.approved_relatives)

    return render_template('manage_relatives.html', form=form, approved_relatives=patient_profile.approved_relatives)

#----------------------------------------------------------------------#

@app.route('/revoke_relative/<int:approval_id>', methods=['POST'])
def revoke_relative(approval_id):
    """
    Allow patients to revoke approval for a relative to access their health records.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('user_role') != 'patient':
        flash("Only patients can revoke relative approvals.")
        return redirect(url_for('index'))

    # Get the approval record
    approval = RelativeApproval.query.get_or_404(approval_id)

    # Verify this approval belongs to the current patient
    patient_profile = PatientProfile.query.filter_by(user_id=session['user_id']).first()
    if approval.patient_id != patient_profile.id:
        flash("You do not have permission to revoke this approval.")
        return redirect(url_for('manage_relatives'))

    try:
        db.session.delete(approval)
        db.session.commit()
        flash("Relative approval has been revoked.")
        return redirect(url_for('manage_relatives'))
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while revoking the approval.")
        return redirect(url_for('manage_relatives'))
