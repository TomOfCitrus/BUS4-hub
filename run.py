from app import app, db
from setup import reset_database

if __name__ == '__main__':
    with app.app_context():
        reset_database()
    app.run(debug=True)