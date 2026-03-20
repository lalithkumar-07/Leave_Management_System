from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import shutil
from datetime import datetime

# --- App Setup ---
app = Flask(__name__)
app.secret_key = "secret-key"

# ✅ Ensure instance folder exists
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
if not os.path.exists(INSTANCE_DIR):
    os.makedirs(INSTANCE_DIR)

# ✅ Database path setup inside instance folder
db_path = os.path.join(INSTANCE_DIR, "leaves.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    available_leaves = db.Column(db.Integer, default=15)
    role = db.Column(db.String(10))  # faculty or hod
    leave_balance = db.Column(db.Integer, default=15)


class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    leave_type = db.Column(db.String(50))
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))
    days = db.Column(db.Integer)
    reason = db.Column(db.String(200))
    status = db.Column(db.String(20), default="Pending")


# --- Routes ---
@app.route('/')
def home():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user.role == 'hod':
            return redirect(url_for('dashboard_hod'))
        return redirect(url_for('dashboard_faculty'))
    return redirect(url_for('login'))


# 🟢 Public Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists! Please choose another.")
            return redirect(url_for('register'))

        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for('login'))

    return render_template('register_form.html')


# 🟢 HOD Register Page
@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if 'user_id' not in session or session.get('role') != 'hod':
        flash("Only HOD can register new users!")
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists! Please choose another.")
            return redirect(url_for('register_user'))

        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash(f"{role.capitalize()} '{username}' registered successfully!")
        return redirect(url_for('dashboard_hod'))

    return render_template('register_user.html')


# 🟡 Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            flash("Login successful!")
            if user.role == 'hod':
                return redirect(url_for('dashboard_hod'))
            return redirect(url_for('dashboard_faculty'))
        flash("Invalid credentials. Please try again or register.")

    return render_template('login.html', show_register_link=True)


# 🟢 Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!")
    return redirect(url_for('login'))


# 🟢 Faculty Dashboard
@app.route('/dashboard_faculty')
def dashboard_faculty():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    leaves = Leave.query.filter_by(user_id=user.id).all()
    return render_template('faculty_dashboard.html', user=user, leaves=leaves, leave_balance=user.leave_balance)


# 🟣 HOD Dashboard (with summary graph)
@app.route('/dashboard_hod')
def dashboard_hod():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    # ✅ Only show pending leaves
    pending_leaves = Leave.query.filter_by(status="Pending").all()

    # ✅ Prepare summary for graph
    status_summary = {"Approved": 0, "Pending": 0, "Rejected": 0}
    all_leaves = Leave.query.all()
    for leave in all_leaves:
        if leave.status in status_summary:
            status_summary[leave.status] += 1

    chart_data = {
        "labels": list(status_summary.keys()),
        "values": list(status_summary.values())
    }

    return render_template('hod_dashboard.html', user=user, leaves=pending_leaves, chart_data=chart_data)


# 🟢 Backup Database
@app.route('/backup_data', methods=['POST'])
def backup_data():
    if 'user_id' not in session or session.get('role') != 'hod':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login'))

    try:
        # Ensure backup folder exists
        backup_folder = os.path.join(BASE_DIR, "backup")
        os.makedirs(backup_folder, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_folder, f"leaves_backup_{timestamp}.db")

        shutil.copy2(db_path, backup_file)
        flash(f"✅ Backup created successfully! ({backup_file})", "success")

        # Offer file for download
        return send_file(backup_file, as_attachment=True)

    except Exception as e:
        flash(f"❌ Backup failed: {str(e)}", "danger")
        return redirect(url_for('dashboard_hod'))


# 🟢 Delete All Data
@app.route('/delete_all_data', methods=['POST'])
def delete_all_data():
    if 'user_id' not in session or session.get('role') != 'hod':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login'))

    try:
        Leave.query.delete()
        User.query.filter(User.role == 'faculty').delete()
        db.session.commit()
        flash('✅ All faculty accounts and leave data deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error deleting data: {str(e)}', 'danger')

    return redirect(url_for('dashboard_hod'))


# 🟢 HOD - View All Faculty
@app.route('/faculty_list')
def faculty_list():
    if 'user_id' not in session or session['role'] != 'hod':
        return redirect(url_for('login'))
    faculty_members = User.query.filter_by(role='faculty').all()
    return render_template('faculty_list.html', faculty_members=faculty_members)


# 🟢 Faculty Details (with Graph)
@app.route('/faculty/<int:faculty_id>')
def faculty_detail(faculty_id):
    if 'user_id' not in session or session['role'] != 'hod':
        return redirect(url_for('login'))

    faculty = User.query.get_or_404(faculty_id)
    leaves = Leave.query.filter_by(user_id=faculty.id).all()

    # ✅ Prepare data for Chart.js (types vs days)
    type_summary = {}
    for leave in leaves:
        type_summary[leave.leave_type] = type_summary.get(leave.leave_type, 0) + leave.days

    chart_data = {
        'labels': list(type_summary.keys()),
        'values': list(type_summary.values())
    }

    return render_template('faculty_detail.html', faculty=faculty, leaves=leaves, chart_data=chart_data)


# 🟢 Apply Leave (Faculty)
@app.route('/apply_leave', methods=['POST'])
def apply_leave():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    leave_type = request.form['leave_type']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    days = int(request.form['days'])
    reason = request.form['reason']

    if user.leave_balance < days:
        flash("Insufficient leave balance!")
        return redirect(url_for('dashboard_faculty'))

    new_leave = Leave(
        user_id=user.id,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        days=days,
        reason=reason,
        status="Pending"
    )
    db.session.add(new_leave)
    db.session.commit()
    flash("Leave applied successfully!")
    return redirect(url_for('dashboard_faculty'))


# 🟢 Edit Leave (Faculty)
@app.route('/edit_leave/<int:leave_id>', methods=['GET', 'POST'])
def edit_leave(leave_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    leave = Leave.query.get_or_404(leave_id)
    user = User.query.get(session['user_id'])

    if leave.user_id != user.id:
        flash("Unauthorized access.")
        return redirect(url_for('dashboard_faculty'))

    if leave.status != "Pending":
        flash("Only pending leaves can be modified.")
        return redirect(url_for('dashboard_faculty'))

    if request.method == 'POST':
        leave.leave_type = request.form['leave_type']
        leave.start_date = request.form['start_date']
        leave.end_date = request.form['end_date']
        leave.reason = request.form['reason']
        leave.days = int(request.form['days'])
        db.session.commit()
        flash("Leave updated successfully!")
        return redirect(url_for('dashboard_faculty'))

    return render_template('edit_leave.html', leave=leave)


# 🟢 Leave Action (Approve/Reject by HOD)
@app.route('/leave_action/<int:leave_id>/<string:action>')
def leave_action(leave_id, action):
    if 'user_id' not in session or session['role'] != 'hod':
        return redirect(url_for('login'))

    leave = Leave.query.get(leave_id)
    if not leave:
        flash("Leave not found!")
        return redirect(url_for('dashboard_hod'))

    if action == 'approve' and leave.status == 'Pending':
        leave.status = 'Approved'
        user = User.query.get(leave.user_id)
        user.leave_balance = max(user.leave_balance - leave.days, 0)
        flash("Leave approved successfully!")
    elif action == 'reject' and leave.status == 'Pending':
        leave.status = 'Rejected'
        flash("Leave rejected successfully!")

    db.session.commit()
    return redirect(url_for('dashboard_hod'))


# --- Run App ---
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
