from flask_sqlalchemy import SQLAlchemy

# Initialize db (no app here)
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    role = db.Column(db.String(10))  # faculty or HOD
    leave_balance = db.Column(db.Integer, default=15)

class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    leave_type = db.Column(db.String(35))
    start_date = db.Column(db.String(15))
    end_date = db.Column(db.String(15))
    days = db.Column(db.Integer)
    reason = db.Column(db.String(100))
    status = db.Column(db.String(10))  # Pending/Approved/Rejected
