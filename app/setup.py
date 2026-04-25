from app import create_app, db
from app.models import User, PatientProfile, HealthLog, Checkup, RelativeApproval
from datetime import date

app = create_app()

def reset_database():
    """Drop all tables, recreate them, and insert basic test data."""
    with app.app_context():
        db.drop_all()
        db.create_all()

        # --- Create Users --- #
        margaret = User(
            first_name='Margaret',
            last_name='Smith',
            date_of_birth=date(1956, 12, 12),
            email='grannysmith@gmail.com',
            role='patient'
        )
        margaret.set_password('ilovemyson1956')

        william = User(
            first_name='William',
            last_name='Smith',
            date_of_birth=date(1952, 10, 21),
            email='willsmith@gmail.com',
            role='patient'
        )
        william.set_password('RewindTime')

        robin = User(
            first_name='Robin',
            last_name='Williams',
            date_of_birth=date(1992, 7, 21),
            email='r.williams2107@gmail.com',
            role='gp'
        )
        robin.set_password('FriendLikeMe')

        alex = User(
            first_name='Alex',
            last_name='Gudgin',
            date_of_birth=date(1994, 9, 18),
            email='a.gudgin1809@gmail.com',
            role='gp'
        )
        alex.set_password('DoctorAte')

        bobby = User(
            first_name='Bobby',
            last_name='Smith',
            date_of_birth=date(1985,8, 13),
            email='smithbob1308@gmail.com',
            role='relative'
        )
        bobby.set_password('iluvmemum1985')

        sarah = User(
            first_name='Sarah',
            last_name='Smith',
            date_of_birth=date(1980, 5, 26),
            email='smithsarah2605@gmail.com',
            role='relative'
        )
        sarah.set_password('IndependenceDay')

        db.session.add_all([margaret, william, robin, alex, bobby, sarah])
        db.session.commit()

        # --- Create Patient Profiles --- #

        margaret_profile = PatientProfile(
            user_id=margaret.id,
            first_name=margaret.first_name,
            last_name=margaret.last_name,
            date_of_birth=margaret.date_of_birth,

            hypertension=False,
            diabetes=True,
            heart_disease=False,
            arthritis=False,
            osteoporosis=False,
            copd=True,
            stroke=False,
            dementia=False,
            vision_problems=False,
            hearing_loss=False,
            allergies='Tree Nut Allergy',
            smoking_status='never',
            alcohol_consumption='none',
            physical_activity='moderate'
        )

        william_profile=PatientProfile(
            user_id=william.id,
            first_name=william.first_name,
            last_name=william.last_name,
            date_of_birth=william.date_of_birth,

            hypertension=False,
            diabetes=False,
            heart_disease=False,
            arthritis=True,
            osteoporosis=False,
            copd=False,
            stroke=False,
            dementia=True,
            vision_problems=True,
            hearing_loss=True,
            allergies='None',
            smoking_status='former',
            alcohol_consumption='none',
            physical_activity='low'
        )

        db.session.add_all([margaret_profile, william_profile])
        db.session.commit()

        # --- Create Health Logs --- #

        margaret_health_log = HealthLog(
            patient_id=margaret_profile.user_id,

            temperature=37.3,
            bp_systolic=124,
            bp_diastolic=86,
            mood='low',
            notes='Worried about William',
            created_at=date(2026, 3, 12)
        )

        william_health_log = HealthLog(
            patient_id = william_profile.user_id,
            temperature=36.6,
            bp_systolic=97,
            bp_diastolic=68,
            mood='okay',
            notes='Been forgetful lately',
            created_at=date(2026, 4, 3)
        )

        db.session.add_all([margaret_health_log, william_health_log])
        db.session.commit()

        # --- Create Checkup Logs --- #

        margaret_checkup = Checkup(
            patient_id=margaret_profile.user_id,
            patient_first_name=margaret_profile.first_name,
            patient_last_name=margaret_profile.last_name,

            gp_id=robin.id,

            checkup_date=date(2026, 2, 14),
            medication='Paracetamol',
            dosage='2x 500mg tablets - take dose 4 times in 24 hours',
            notes='Patient reports headache, likely common cold'
        )

        william_checkup = Checkup(
            patient_id=william_profile.user_id,
            patient_first_name=william_profile.first_name,
            patient_last_name=william_profile.last_name,

            gp_id=alex.id,

            checkup_date=date(2026, 3, 29),
            medication='Cetirizine',
            dosage='1x 10mg tablet - take dose once every 24 hours',
            notes='Patient reports runny nose, likely irritated by pollen'
        )

        db.session.add_all([margaret_checkup, william_checkup])
        db.session.commit()

        # --- Create Relative Approvals --- #

        m_b_approval = RelativeApproval(
            patient_id=margaret_profile.user_id,
            relative_id=bobby.id,

            approved_at=date(2026, 2, 17)
        )

        w_s_approval = RelativeApproval(
            patient_id=william_profile.user_id,
            relative_id=sarah.id,

            approved_at=date(2026, 3, 30)
        )

        db.session.add_all([m_b_approval, w_s_approval])
        db.session.commit()

        # -----------------------------------------------------------#

        print('Database reset and test data inserted.')