from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, redirect, url_for, flash, request, session, abort
from app import app
from app import db
from app.forms import RegisterForm, LoginForm, PatientProfileForm, HealthLogForm, CheckupForm, RelativeApprovalForm, CalendarForm
from app.models import User, PatientProfile, HealthLog, Checkup, RelativeApproval, RelativeInvite
from sqlalchemy.exc import IntegrityError
from datetime import date, datetime, timedelta

#----------------------------------------------------------------------#
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', session=session)

#----------------------------------------------------------------------#
# REGISTER, LOGIN, LOGOUT
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
# ALLOW GP AND PATIENT TO CREATE, UPDATE, READ, AND DELETE HEALTH RECORDS
#----------------------------------------------------------------------#

@app.route('/profile', methods=['GET', 'POST'])
def patient_profile():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    user = User.query.get_or_404(session['user_id'])

    profile = PatientProfile.query.filter_by(user_id=session["user_id"]).first()

    if not profile:

        form = PatientProfileForm()

        if form.validate_on_submit():
            patient_profile = PatientProfile(
                user_id=session['user_id'],
                first_name=user.first_name,
                last_name=user.last_name,
                date_of_birth=user.date_of_birth,
                hypertension=form.hypertension.data,
                diabetes=form.diabetes.data,
                heart_disease=form.heart_disease.data,
                arthritis=form.arthritis.data,
                osteoporosis=form.osteoporosis.data,
                copd=form.copd.data,
                stroke=form.stroke.data,
                dementia=form.dementia.data,
                vision_problems=form.vision_problems.data,
                hearing_loss=form.hearing_loss.data,
                allergies=form.allergies.data,
                smoking_status=form.smoking_status.data,
                alcohol_consumption=form.alcohol_consumption.data,
                physical_activity=form.physical_activity.data
            )
            db.session.add(patient_profile)
            db.session.commit()
            flash('Your patient profile has been successfully created!')
            return redirect(url_for('index'))

    else:
        return redirect(url_for('get_patient_profile', patient_id=profile.user_id))
    return render_template('patient_profile.html', form=form)

@app.route('/get_profile/<int:patient_id>', methods=['GET', 'POST'])
def get_patient_profile(patient_id):
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))

    patient = db.session.query(PatientProfile)\
    .filter(PatientProfile.user_id == patient_id).first()

    return render_template('view_profile.html', patient=patient)

@app.route('/update_profile/<int:patient_id>', methods=['GET', 'POST'])
def update_patient_profile(patient_id):
    if 'user_id' not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))

    profile = PatientProfile.query.filter_by(user_id=patient_id).first()
    if not profile:
        flash("Patient profile not found.")
        return redirect(url_for("index"))

    form = PatientProfileForm(obj=profile)

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
        return redirect(url_for("get_patient_profile", patient_id=profile.user_id))

    return render_template("update_profile.html", form=form, profile=profile)

#----------------------------------------------------------------------#

@app.route('/health_log', methods=['GET', 'POST'])
def health_log():
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))

    # Get patient profile
    profile = PatientProfile.query.filter_by(user_id=session["user_id"]).first()

    if not profile:
        flash("Patient profile not found.")
        return redirect(url_for("index"))

    form = HealthLogForm()

    if form.validate_on_submit():
        health_log = HealthLog(
            patient_id=profile.user_id,
            temperature=form.temperature.data,
            bp_systolic=form.bp_systolic.data,
            bp_diastolic=form.bp_diastolic.data,
            mood=form.mood.data,
            notes=form.notes.data
        )
        db.session.add(health_log)
        db.session.commit()
        flash('Your health update has been successfully logged!')
        return redirect(url_for('health_log'))
    logs = HealthLog.query.filter_by(patient_id=profile.user_id)\
           .order_by(HealthLog.created_at.desc()).all()
    return render_template('health_logs.html', form=form, logs=logs, profile=profile)

# display health data
@app.route('/get_healthlog/<int:patient_id>', methods=['GET', 'POST'])
def get_health_log(patient_id):
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))

    form = CalendarForm()

    start = datetime.combine(date.today() - timedelta(days=7), datetime.min.time())
    end = datetime.combine(date.today(), datetime.max.time())

    if form.validate_on_submit():
        start = datetime.combine(form.start_date.data, datetime.min.time())
        end = datetime.combine(form.end_date.data, datetime.max.time())
        flash('Report successfully generated!')

    healthlog = (
        db.session.query(HealthLog)
        .join(PatientProfile, PatientProfile.user_id == HealthLog.patient_id)
        .filter(HealthLog.patient_id == patient_id)
        .filter(HealthLog.created_at >= start)
        .filter(HealthLog.created_at <= end)
        .order_by(HealthLog.created_at.desc())
        .all()
    )

    # Get patient profile
    profile = PatientProfile.query.filter_by(user_id=patient_id).first()

    if not profile:
        flash("Patient profile not found.")
        return redirect(url_for("index"))

    return render_template("view_healthlog.html", form=form, healthlog=healthlog, patient=profile,
                           patient_id=patient_id)

#----------------------------------------------------------------------#
# update health data
@app.route('/health/update/<int:log_id>', methods=['GET', 'POST'])
def update_health_data(log_id):
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))

    profile = PatientProfile.query.filter_by(user_id=session["user_id"]).first()

    if not profile:
        flash("Patient profile not found.")
        return redirect(url_for("index"))

    health_log = HealthLog.query.get_or_404(log_id)
    if health_log.patient_id != session["user_id"]:
        abort(403)
    form = HealthLogForm(obj=health_log)

    if form.validate_on_submit():
        health_log.temperature = form.temperature.data
        health_log.bp_systolic = form.bp_systolic.data
        health_log.bp_diastolic = form.bp_diastolic.data
        health_log.mood = form.mood.data
        health_log.notes = form.notes.data
        db.session.commit()
        flash('Your health log has been updated successfully!')
        return redirect(url_for('get_health_log', patient_id=profile.user_id))
    return render_template('updateHealth.html', form=form, profile=profile)

#----------------------------------------------------------------------#

# delete health data, only on optional fields
@app.route('/health/delete/<int:log_id>', methods=['GET','POST'])
def delete_health_data(log_id):
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))

    profile = PatientProfile.query.filter_by(user_id=session["user_id"]).first()

    if not profile:
        flash("Patient profile not found.")
        return redirect(url_for("index"))

    health_log = HealthLog.query.get_or_404(log_id)
    if health_log.patient_id != session["user_id"]:
        abort(403)
    db.session.delete(health_log)
    db.session.commit()
    flash('Your health log has been deleted successfully.')
    return redirect(url_for("get_health_log", patient_id=profile.user_id))

#----------------------------------------------------------------------#

@app.route('/get_checkups/<int:patient_id>', methods=['GET', 'POST'])
def get_checkups(patient_id):
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    form = CalendarForm()

    start = datetime.combine(date.today() - timedelta(days=7), datetime.min.time())
    end = datetime.combine(date.today(), datetime.max.time())

    if form.validate_on_submit():
        start = datetime.combine(form.start_date.data, datetime.min.time())
        end = datetime.combine(form.end_date.data, datetime.max.time())
        flash('Report successfully generated!')

    checkups = (db.session.query(Checkup)
        .join(PatientProfile, PatientProfile.user_id == Checkup.patient_id)
        .filter(Checkup.patient_id == patient_id)
        .filter(Checkup.checkup_date >= start)
        .filter(Checkup.checkup_date <= end)
        .order_by(Checkup.checkup_date.desc())
        .all()
    )

    profile = PatientProfile.query.filter_by(user_id=session['user_id']).first()

    if not profile:
        flash('Patient profile not found.')
        return redirect(url_for('index'))

    return render_template('view_checkups.html', form=form, checkups=checkups, patient=profile,
                           patient_id=patient_id)

#----------------------------------------------------------------------#
# ALLOW GP TO CREATE, UPDATE, AND DELETE CHECK-UPS
#----------------------------------------------------------------------#

@app.route('/check_up', methods=['GET', 'POST'])
def checkup():
    form = CheckupForm()
    if form.validate_on_submit():
        checkup_log = Checkup(
            patient_last_name=form.patient_last_name.data,
            patient_first_name=form.patient_first_name.data,
            gp_id=session["user_id"],
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

#----------------------------------------------------------------------#

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

#----------------------------------------------------------------------#

@app.route('/delete_check_up/<int:checkup_id>', methods=['GET', 'POST'])
def delete_checkup(checkup_id):
    checkup_log = Checkup.query.get_or_404(checkup_id)
    db.session.delete(checkup_log)
    db.session.commit()
    flash(f'Check-up details have been deleted successfully.')
    return redirect(url_for('checkup'))

#----------------------------------------------------------------------#
# ALLOW PATIENT TO MANAGE RELATIVE ACCESS
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
            patient_id=patient_profile.user_id,
            relative_id=relative_user.id
        ).first()

        if existing_approval:
            flash(f"This relative is already approved.")
            return render_template('manage_relatives.html', form=form, approved_relatives=patient_profile.approved_relatives)

        # Create new approval
        try:
            new_approval = RelativeApproval(
                patient_id=patient_profile.user_id,
                relative_id=relative_user.id,
                relationship = form.relationship.data
            )
            db.session.add(new_approval)
            db.session.commit()
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
    if approval.patient_id != patient_profile.user_id:
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

#----------------------------------------------------------------------#
# ALLOW RELATIVE TO VIEW PATIENT RECORD
#----------------------------------------------------------------------#

# create invite – patient side
def create_relative_invite(patient_id, relative_email, hours_valid=24):
    invite = RelativeInvite(
        patient_id=patient_id,
        relative_email=relative_email.lower(),
        expires_at=datetime.utcnow() + timedelta(hours=hours_valid)
    )
    invite.generate_token()

    db.session.add(invite)
    db.session.commit()

    return invite.token

#----------------------------------------------------------------------#

# approve from token – relative side
def approve_relative_from_token(token, relative_user_id):
    invite = RelativeInvite.query.filter_by(token=token).first()

    if not invite or not invite.is_valid():
        return False, "Invalid or expired code"

    relative_user = User.query.get(relative_user_id)

    if not relative_user or relative_user.email.lower() != invite.relative_email:
        return False, "This code is not assigned to your account"

    existing = RelativeApproval.query.filter_by(
        patient_id=invite.patient_id,
        relative_id=relative_user_id
    ).first()

    if existing:
        return False, "Already approved"

    approval = RelativeApproval(
        patient_id=invite.patient_id,
        relative_id=relative_user_id
    )

    invite.used = True

    db.session.add(approval)
    db.session.commit()

    return True, "Access granted"

#----------------------------------------------------------------------#

@app.route('/generate_relative_code/<int:relative_id>', methods=['GET', 'POST'])
def generate_relative_code(relative_id):
    if 'user_id' not in session or session.get('user_role') != 'patient':
        return redirect(url_for('login'))

    patient_profile = PatientProfile.query.filter_by(user_id=session['user_id']).first()

    relative = User.query.get_or_404(relative_id)
    relative_email = relative.email

    token = create_relative_invite(patient_profile.user_id, relative_email)

    flash(f"Access code for {relative_email}: {token}")
    print(token)
    return redirect(url_for('manage_relatives'))

#----------------------------------------------------------------------#

@app.route('/use_relative_code', methods=['GET','POST'])
def use_relative_code():
    if 'user_id' not in session or session.get('user_role') != 'relative':
        return redirect(url_for('login'))

    token = request.form.get('code')

    success, message = approve_relative_from_token(token, session['user_id'])

    flash(message)
    return redirect(url_for('index'))

#----------------------------------------------------------------------#

@app.route('/select_patient')
def select_patient():
    """
    Takes relatives to a menu where they can choose whose health records they'd like to check.
    If only one patient has approved, this will immediately redirect to their information page.
    """
    # Basic security gates - only the 'relative' user type can access this page:
    if 'user_id' not in session:
        return redirect(url_for('login'))

    elif session.get('user_role') != 'relative':
        flash('Only approved relatives can view patient data with these settings.')
        return redirect(url_for('index'))

    patient_approvals = RelativeApproval.query.filter_by(relative_id=session['user_id']).all()

    # if no patients have approved the relative, redirect to index:
    if not patient_approvals:
        flash('No patients have approved you yet!')
        return redirect(url_for('index'))

    # if at least one patient has approved the relative, pull their name from their patient profile:
    patients = (
        db.session.query(PatientProfile)
        .join(RelativeApproval, RelativeApproval.patient_id == PatientProfile.user_id)
        .filter(RelativeApproval.relative_id == session['user_id'])
        .all()
    )
    approval_list = [
        {
            'patient_id': patient.user_id,
            'last_name': patient.last_name,
            'first_name': patient.first_name
        }
        for patient in patients
    ]
    approval_list.sort(key=lambda p: (p['last_name'].lower(), p['first_name'].lower()))

    # if only one patient has approved the relative, automatically redirect to that patient's info page:
    if len(approval_list) == 1:
        return redirect(url_for('patient_info', patient_id=approval_list[0]['patient_id']))

    # if two or more patients have approved the relative, the html page will render.
    return render_template('select_patient.html', approval_list=approval_list)

#----------------------------------------------------------------------#

@app.route('/patient_information/<int:patient_id>')
def patient_info(patient_id):
    """
    Displays a menu where you can choose to read the patient's profile,
    look through their history of health reports,
    or read their checkup history.
    """
    # Basic security gates - only the 'relative' user type can access this page:
    if 'user_id' not in session:
        return redirect(url_for('login'))

    elif session.get('user_role') != 'relative':
        flash('Only approved relatives can view patient data with these settings.')
        return redirect(url_for('index'))

    # if user has exactly one patient's approval, they should be able to return straight to dashboard:
    patient_approvals = RelativeApproval.query.filter_by(relative_id=session['user_id']).all()
    only_approval = False
    if len(patient_approvals) == 1:
        only_approval = True

    # pull the patient's name into the html page:
    patient = (
        db.session.query(PatientProfile)
        .join(RelativeApproval, RelativeApproval.patient_id == PatientProfile.user_id)
        .filter(PatientProfile.user_id == patient_id)
        .first()
    )
    patient_dict = {
        'patient_id': patient.user_id,
        'last_name': patient.last_name,
        'first_name': patient.first_name
    }

    # you can access each part of the patient's record via the following html page:
    return render_template('patient_info.html', patient_dict=patient_dict, only_approval=only_approval)

#----------------------------------------------------------------------#

@app.route('/view_profile/<int:patient_id>')
def view_profile(patient_id):
    """
    Allows relative to view basic information provided by the patient.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('user_role') != 'relative':
        flash('Unauthorized.')
        return redirect(url_for('index'))

    approval = RelativeApproval.query.filter_by(
        patient_id=patient_id,
        relative_id=session['user_id']
    ).first()

    if not approval:
        flash("Unauthorized access.")
        return redirect(url_for('index'))

    # query patient profile to get all rows of information about the patient:
    patient = (
        db.session.query(PatientProfile)
        .join(RelativeApproval, RelativeApproval.patient_id == PatientProfile.user_id)
        .filter(PatientProfile.user_id == patient_id)
        .first()
    )
    return render_template('view_profile.html', patient=patient)

#----------------------------------------------------------------------#

@app.route('/view_healthlog/<int:patient_id>', methods=['GET', 'POST'])
def view_healthlog(patient_id):
    """
    Allows relative to view all health logs made by the patient themselves.
    Functions as a calendar with a form that allows you to filter down to a specific date range.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('user_role') != 'relative':
        flash('Unauthorized.')
        return redirect(url_for('index'))

    approval = RelativeApproval.query.filter_by(
        patient_id=patient_id,
        relative_id=session['user_id']
    ).first()

    if not approval:
        flash("Unauthorized access.")
        return redirect(url_for('index'))

    # pull a date range from the form and use it to filter through health updates:
    form = CalendarForm()

    # create default start and end dates to display the last week by default:
    start = datetime.combine(date.today() - timedelta(days=7), datetime.min.time())
    end = datetime.combine(date.today(), datetime.max.time())

    # submitting the form will change these dates:
    if form.validate_on_submit():
        start = datetime.combine(form.start_date.data, datetime.min.time())
        end = datetime.combine(form.end_date.data, datetime.max.time())
        flash('Report successfully generated!')

    # now pull data from within the date range:
    healthlog = (
        db.session.query(HealthLog)
        .join(RelativeApproval, RelativeApproval.patient_id == HealthLog.patient_id)
        .filter(HealthLog.patient_id == patient_id)
        .filter(HealthLog.created_at >= start)
        .filter(HealthLog.created_at <= end)
        .order_by(HealthLog.created_at.desc())
        .all()
    )

    # pull in the patient's profile too - just for their name:
    patient = (
        db.session.query(PatientProfile.first_name, PatientProfile.last_name)
        .join(RelativeApproval, RelativeApproval.patient_id == PatientProfile.user_id)
        .filter(PatientProfile.user_id == patient_id)
        .first()
    )
    return render_template('view_healthlog.html', form=form, healthlog=healthlog, patient=patient,
                           patient_id=patient_id)

#----------------------------------------------------------------------#

@app.route('/view_checkups/<int:patient_id>', methods=['GET', 'POST'])
def view_checkups(patient_id):
    """
    Allows relative to view all health logs made by the patient themselves.
    Functions as a calendar with a form that allows you to filter down to a specific date range.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('user_role') != 'relative':
        flash('Unauthorized.')
        return redirect(url_for('index'))

    approval = RelativeApproval.query.filter_by(
        patient_id=patient_id,
        relative_id=session['user_id']
    ).first()

    if not approval:
        flash("Unauthorized access.")
        return redirect(url_for('index'))

    # pull a date range from the form and use it to filter through health updates:
    form = CalendarForm()

    # create default start and end dates to display the last week by default:
    start = datetime.combine(date.today() - timedelta(days=7), datetime.min.time())
    end = datetime.combine(date.today(), datetime.max.time())

    # submitting the form will change these dates:
    if form.validate_on_submit():
        start = datetime.combine(form.start_date.data, datetime.min.time())
        end = datetime.combine(form.end_date.data, datetime.max.time())
        flash('Report successfully generated!')

    # now pull data from within the date range:
    checkups = (
        db.session.query(Checkup)
        .join(RelativeApproval, RelativeApproval.patient_id == Checkup.patient_id)
        .filter(Checkup.patient_id == patient_id)
        .filter(Checkup.checkup_date >= start)
        .filter(Checkup.checkup_date <= end)
        .order_by(Checkup.checkup_date.desc())
        .all()
    )

    # pull in the patient's profile too - just for their name:
    patient = (
        db.session.query(PatientProfile.first_name, PatientProfile.last_name)
        .join(RelativeApproval, RelativeApproval.patient_id == PatientProfile.user_id)
        .filter(PatientProfile.user_id == patient_id)
        .first()
    )
    return render_template('view_checkups.html', form=form, checkups=checkups, patient=patient,
                           patient_id=patient_id)

#----------------------------------------------------------------------#