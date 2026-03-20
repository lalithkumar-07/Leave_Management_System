from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leaves.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# --- Models ---
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
    status = db.Column(db.String(10)) # Pending/Approved/Rejected

# --- Utility functions ---
def is_logged_in():
    return 'user_id' in session

def current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

# --- Routes ---
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username'],
                                   password=request.form['password']).first()
        if user:
            session['user_id'] = user.id
            if user.role == 'hod':
                return redirect(url_for('dashboard_hod'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    u = current_user()
    if not u or u.role != 'faculty':
        return redirect(url_for('login'))
    leaves = Leave.query.filter_by(user_id=u.id).all()
    return render_template('faculty_dashboard.html', user=u, leaves=leaves, leave_balance=u.leave_balance)

@app.route('/apply_leave', methods=['POST'])
def apply_leave():
    u = current_user()
    if not u or u.role != 'faculty':
        return redirect(url_for('login'))
    days_applied = int(request.form['days'])
    if u.leave_balance < days_applied:
        flash('Not enough leave balance!')
        return redirect(url_for('dashboard'))
    u.leave_balance -= days_applied
    leave = Leave(
        user_id = u.id,
        leave_type = request.form['leave_type'],
        start_date = request.form['start_date'],
        end_date = request.form['end_date'],
        days = days_applied,
        reason = request.form['reason'],
        status = 'Pending'
    )
    db.session.add(leave)
    db.session.commit()
    flash('Leave applied!')
    return redirect(url_for('dashboard'))

@app.route('/update_leave/<int:leave_id>', methods=['POST'])
def update_leave(leave_id):
    leave = Leave.query.get(leave_id)
    u = current_user()
    if not leave or leave.user_id != u.id or leave.status != "Pending":
        return "Not allowed", 403
    leave.leave_type = request.form['leave_type']
    leave.start_date = request.form['start_date']
    leave.end_date = request.form['end_date']
    leave.days = int(request.form['days'])
    leave.reason = request.form['reason']
    db.session.commit()
    flash('Leave updated!')
    return redirect(url_for('dashboard'))

@app.route('/leave_action/<int:leave_id>/<action>')
def leave_action(leave_id, action):
    u = current_user()
    if not u or u.role != 'hod':
        return redirect(url_for('login'))
    leave = Leave.query.get(leave_id)
    if leave and leave.status == 'Pending':
        leave.status = 'Approved' if action == 'approve' else 'Rejected'
        db.session.commit()
        flash(f'Leave {leave.status}!')
    return redirect(url_for('dashboard_hod'))

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    u = current_user()
    if not u or u.role != 'hod':  # Only HOD can add new users
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        balance = int(request.form['leave_balance']) if 'leave_balance' in request.form else 15
        if not username or not password or role not in ['faculty', 'hod']:
            flash("Invalid input")
        elif User.query.filter_by(username=username).first():
            flash("Username already exists")
        else:
            db.session.add(User(username=username, password=password, role=role, leave_balance=balance))
            db.session.commit()
            flash(f'User {username} added as {role}!')
    return render_template('register_user.html')

@app.route('/edit_leave/<int:leave_id>', methods=['GET', 'POST'])
def edit_leave(leave_id):
    leave = Leave.query.get(leave_id)
    u = current_user()
    if not leave or leave.user_id != u.id or leave.status != "Pending":
        return "Not allowed", 403
    if request.method == 'POST':
        # Store original days before updating
        original_days = leave.days
        new_days = int(request.form['days'])

        # Update leave info from form
        leave.leave_type = request.form['leave_type']
        leave.start_date = request.form['start_date']
        leave.end_date = request.form['end_date']
        leave.days = new_days
        leave.reason = request.form['reason']

        # Update available leaves: restore original, remove new
        u.available_leaves += original_days   # restore leaves as if leave was cancelled
        u.available_leaves -= new_days        # deduct for new value

        db.session.commit()
        flash('Leave updated!')
        return redirect(url_for('dashboard'))
    return render_template('edit_leave.html', leave=leave)

@app.route('/dashboard_hod')
def dashboard_hod():
    u = current_user()
    if not u:
        return redirect(url_for('login'))
    if u.role == 'faculty':
        return redirect(url_for('dashboard'))
    elif u.role == 'hod':
        leaves = Leave.query.filter_by(status='Pending').all()
        return render_template('hod_dashboard.html', user=u, leaves=leaves)
    else:
        return "Access denied", 403

@app.route('/leave_balance')
def leave_balance():
    user = current_user()
    if not user or user.role != 'faculty':
        return jsonify({"error": "Not allowed"}), 403
    return jsonify({"leave_balance": user.leave_balance})
@app.route('/faculty_dashboard')
def faculty_dashboard():
    faculty_names = ['faculty1', 'faculty2', 'fa7', 'fa8']
    leaves_taken = [5, 3, 7, 2]
    leaves_left = [10, 12, 8, 13]
    return render_template('faculty_dashboard.html',
                           faculty_names=faculty_names,
                           leaves_taken=leaves_taken,
                           leaves_left=leaves_left)
# --- Run ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Add demo users if database is empty
        if not User.query.first():
            db.session.add(User(username='faculty1', password='pwd1', role='faculty', leave_balance=15))
            db.session.add(User(username='hod1', password='pwd2', role='hod', leave_balance=15))
            db.session.commit()
    app.run(debug=True)