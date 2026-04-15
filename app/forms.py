from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, BooleanField, TextAreaField, IntegerField, FloatField
from wtforms.fields.datetime import DateField
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from datetime import date

#----------------------------------------------------------------------#

class RegisterForm(FlaskForm):
    first_name = StringField("First name(s):", validators=[DataRequired()])
    last_name = StringField("Last name:", validators=[DataRequired()])
    date_of_birth = DateField("Date of birth:", format="%Y-%m-%d", validators=[DataRequired()])
    email = StringField("Email:", validators=[DataRequired(), Length(min=8)])
    password = PasswordField("Password:", validators=[DataRequired(), Length(min=8)])
    role = SelectField("What's your role?", choices=[
        ("patient", "Patient"),
        ("relative", "Relative of a patient"),
        ("gp", "General Practitioner (GP)")],
        validators=[DataRequired()])
    submit = SubmitField("Register")

#----------------------------------------------------------------------#

class LoginForm(FlaskForm):
    email = StringField("Email:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Login")

#----------------------------------------------------------------------#

# initial health log, to be displayed once after registration only
class PatientProfile(FlaskForm):
    # health conditions
    hypertension = BooleanField('Hypertension')
    diabetes = BooleanField('Diabetes')
    heart_disease = BooleanField('Heart Disease')
    arthritis = BooleanField('Arthritis')
    osteoporosis = BooleanField('Osteoporosis')
    copd = BooleanField('COPD')
    stroke = BooleanField('Stroke')
    dementia = BooleanField('Dementia / Alzheimer’s')
    vision_problems = BooleanField('Vision Problems')
    hearing_loss = BooleanField('Hearing Loss')

    # allergies
    allergies = TextAreaField('Allergies / Reactions', validators=[Optional()])

    # medication
    medication_name = StringField("Medication name:", validators=[Optional(), Length(max=100)])
    dosage = StringField("Dosage (e.g., 10mg)", validators=[Optional()])
    notes = TextAreaField("Notes:", validators=[Optional(), Length(max=300)])

    # lifestyle
    smoking_status = SelectField('Smoking Status',
                                 choices=[('never', 'Never'), ('former', 'Former'), ('current', 'Current')],
                                 validators=[Optional()])
    alcohol_consumption = SelectField('Alcohol Consumption',
                                      choices=[('none', 'None'), ('occasional', 'Occasional'), ('regular', 'Regular')],
                                      validators=[Optional()])
    physical_activity = SelectField('Physical Activity',
                                    choices=[('low', 'Low'), ('moderate', 'Moderate'), ('high', 'High')],
                                    validators=[Optional()])
    submit = SubmitField('Submit Health Record')

#----------------------------------------------------------------------#

# form that can be completed whenever patient needs, will be a <a href="">
class HealthLog(FlaskForm):
    temperature = FloatField(
        "Temperature (°C)",
        validators=[
            Optional(),
            NumberRange(min=30, max=45)],
        render_kw={"placeholder": "e.g. 36.5"})
    bp_systolic = IntegerField(
        "Blood Pressure - Top Number",
        validators=[
            Optional(),
            NumberRange(min=70, max=250)],
        render_kw={"placeholder": "e.g. 120"})
    bp_diastolic = IntegerField(
        "Blood Pressure - Bottom Number",
        validators=[
            Optional(),
            NumberRange(min=40, max=150)],
        render_kw={"placeholder": "e.g. 80"})
    mood = SelectField(
        "How are you feeling today?",
        choices=[
            ("", "Select"),
            ("good", "Good"),
            ("okay", "Okay"),
            ("low", "Low"),
            ("unwell", "Feeling unwell")],
        validators=[Optional()])
    notes = TextAreaField(
        "Notes (optional)",
        validators=[Optional(), Length(max=500)],
        render_kw={"placeholder": "Anything else you'd like to record? (e.g. fall/injury)"})
    submit = SubmitField("Save Health Record")

# ----------------------------------------------------------------------#

# form to be completed by GP whenever they have a check-up with a patient.
class CheckupForm(FlaskForm):
    patient_last_name = StringField("Last name of patient:", validators=[DataRequired()])
    patient_first_name = StringField("First name(s) of patient:", validators=[DataRequired()])
    checkup_date = DateField("Date:", format="%Y-%m-%d", default=date.today, validators=[DataRequired()])
    medication = StringField(
        "Prescribed Medication(s) (Type N/A if none):",
        validators=[DataRequired(), Length(max=100)]
    )
    dosage = StringField(
        "Dosage(s) (Type N/A if none):",
        validators=[DataRequired(), Length(max=100)]
    )
    notes = TextAreaField(
        "Check-up Notes:",
        validators=[DataRequired(), Length(max=500)]
    )
    submit = SubmitField("Submit Check-up Record")