from app import db
from app.models import User, PatientProfile, HealthLog, Checkup, RelativeApproval
from datetime import date

def reset_database():
    """Drop all tables, recreate them, and insert basic test data."""
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

    robin = User(
        first_name='Robin',
        last_name='Williams',
        date_of_birth=date(1992, 7, 21),
        email='r.williams2107@gmail.com',
        role='gp'
    )
    robin.set_password('FriendLikeMe')

    bobby = User(
        first_name='Bobby',
        last_name='Smith',
        date_of_birth=date(1985,8, 13),
        email='smithbob1308@gmail.com',
        role='relative'
    )
    bobby.set_password('iluvmemum1985')

    db.session.add_all([margaret, robin, bobby])
    db.session.commit()

    # --- Create Patient Profiles --- #

    # --- Create Health Logs --- #

    # --- Create Checkup Logs --- #

    # --- Create Relative Approvals --- #

    print('Database reset and test data inserted.')