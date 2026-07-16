from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Assignment, Attendance, Note, StudyPlan, Goal, ImportantLink, Timetable

app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

db.init_app(app)

with app.app_context():
    db.create_all()

# -------------------------
# Home & Auth Routes
# -------------------------
@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        university = request.form.get("university")
        program = request.form.get("program")
        semester = request.form.get("semester")

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            university=university,
            program=program,
            semester=semester
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            remember = request.form.get("remember") == "on"

            login_user(user, remember=remember)

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.")
    return redirect(url_for("login"))

# -------------------------
# Dashboard Route
# -------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    assignments = Assignment.query.filter_by(user_id=current_user.id).order_by(Assignment.due_date.asc()).limit(3).all()
    attendance_records = Attendance.query.filter_by(user_id=current_user.id).all()
    notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.created_at.desc()).all()
    study_plans = (
    StudyPlan.query
    .filter_by(user_id=current_user.id)
    .order_by(StudyPlan.study_date.asc())
    .limit(2)
    .all()
)
    goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.id.desc()).limit(3).all()
    links = ImportantLink.query.filter_by(user_id=current_user.id).limit(3).all()
    timetable_entries = Timetable.query.filter_by(user_id=current_user.id).all()

    return render_template(
        "dashboard.html",
        current_date=datetime.now().strftime("%A, %d %B %Y"),
        assignments=assignments,
        attendance_records=attendance_records,
        notes=notes,
        study_plans=study_plans,
        goals=goals,
        links=links,
        timetable_entries=timetable_entries
    )

# -------------------------
# Assignments
# -------------------------
@app.route("/assignments")
@login_required
def assignments():
    assignments = Assignment.query.filter_by(user_id=current_user.id).all()
    return render_template("assignments.html", assignments=assignments)

@app.route("/assignment/add", methods=["GET", "POST"])
@login_required
def add_assignment():
    if request.method == "POST":
        due_date = datetime.strptime(request.form.get("due_date"), "%Y-%m-%d").date()
        assignment = Assignment(
            title=request.form.get("title"),
            subject=request.form.get("subject"),
            due_date=due_date,
            priority=request.form.get("priority"),
            status=request.form.get("status"),
            user_id=current_user.id
        )
        db.session.add(assignment)
        db.session.commit()
        flash("Assignment added successfully!")
        return redirect(url_for("assignments"))
    return render_template("add_assignment.html")

@app.route("/assignment/edit/<int:id>")
@login_required
def edit_assignment(id):
    assignment = Assignment.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template("edit_assignment.html", assignment=assignment)

@app.route("/assignment/update/<int:id>", methods=["POST"])
@login_required
def update_assignment(id):
    assignment = Assignment.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    assignment.title = request.form.get("title")
    assignment.subject = request.form.get("subject")
    assignment.due_date = datetime.strptime(request.form.get("due_date"), "%Y-%m-%d").date()
    assignment.priority = request.form.get("priority")
    assignment.status = request.form.get("status")
    db.session.commit()
    flash("Assignment updated successfully!")
    return redirect(url_for("assignments"))

@app.route("/assignment/delete/<int:id>", methods=["POST"])
@login_required
def delete_assignment(id):
    assignment = Assignment.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(assignment)
    db.session.commit()
    flash("Assignment deleted successfully!")
    return redirect(url_for("assignments"))

# -------------------------
# Attendance
# -------------------------
@app.route("/attendance")
@login_required
def attendance():
    attendance_records = Attendance.query.filter_by(user_id=current_user.id).all()
    return render_template("attendance.html", attendance_records=attendance_records)

@app.route("/attendance/add", methods=["GET", "POST"])
@login_required
def add_attendance():
    if request.method == "POST":

        attended = int(request.form.get("attended_classes"))
        total = int(request.form.get("total_classes"))

        if attended > total:
            flash("Attended classes cannot be greater than total classes.")
            return redirect(url_for("add_attendance"))

        new_record = Attendance(
            subject=request.form.get("subject"),
            attended_classes=attended,
            total_classes=total,
            user_id=current_user.id
    )

        db.session.add(new_record)
        db.session.commit()

        flash("Attendance added successfully!")

        return redirect(url_for("attendance"))
    return render_template("add_attendance.html")

@app.route("/attendance/edit/<int:id>")
@login_required
def edit_attendance(id):
    record = Attendance.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template("edit_attendance.html", record=record)

@app.route("/attendance/update/<int:id>", methods=["POST"])
@login_required
def update_attendance(id):

    record = Attendance.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    attended = int(request.form.get("attended_classes"))
    total = int(request.form.get("total_classes"))

    if attended > total:
        flash("Attended classes cannot be greater than total classes.")
        return redirect(url_for("edit_attendance", id=id))

    record.subject = request.form.get("subject")
    record.attended_classes = attended
    record.total_classes = total

    db.session.commit()

    flash("Attendance updated successfully!")

    return redirect(url_for("attendance"))

@app.route("/attendance/delete/<int:id>", methods=["POST"])
@login_required
def delete_attendance(id):
    record = Attendance.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(record)
    db.session.commit()
    flash("Attendance deleted successfully!")
    return redirect(url_for("attendance"))

# -------------------------
# Notes
# -------------------------
@app.route("/notes")
@login_required
def notes():
    notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.created_at.desc()).all()
    return render_template("notes.html", notes=notes)

@app.route("/notes/add", methods=["GET", "POST"])
@login_required
def add_note():
    if request.method == "POST":
        note = Note(
            title=request.form.get("title"),
            content=request.form.get("content"),
            user_id=current_user.id
        )
        db.session.add(note)
        db.session.commit()
        flash("Note added successfully!")
        return redirect(url_for("notes"))
    return render_template("add_note.html")

@app.route("/notes/edit/<int:id>")
@login_required
def edit_note(id):
    note = Note.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template("edit_note.html", note=note)

@app.route("/notes/update/<int:id>", methods=["POST"])
@login_required
def update_note(id):
    note = Note.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    note.title = request.form.get("title")
    note.content = request.form.get("content")
    db.session.commit()
    flash("Note updated successfully!")
    return redirect(url_for("notes"))

@app.route("/notes/delete/<int:id>", methods=["POST"])
@login_required
def delete_note(id):
    note = Note.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(note)
    db.session.commit()
    flash("Note deleted successfully!")
    return redirect(url_for("notes"))

@app.route("/notes/quick-update", methods=["POST"])
@login_required
def quick_update_notes():
    data = request.get_json() or {}
    content = data.get("content", "")
    
    note = Note.query.filter_by(user_id=current_user.id, title="Dashboard Quick Note").first()
    if not note:
        note = Note(title="Dashboard Quick Note", content=content, user_id=current_user.id)
        db.session.add(note)
    else:
        note.content = content
    db.session.commit()
    return {"success": True}

# -------------------------
# Study Planner Core Logic
# -------------------------
@app.route("/planner")
@login_required
def planner():
    study_plans = StudyPlan.query.filter_by(user_id=current_user.id).order_by(StudyPlan.study_date.desc()).all()
    return render_template("planner.html", study_plans=study_plans)

@app.route("/planner/add", methods=["GET", "POST"])
@login_required
def add_plan():
    if request.method == "POST":
        plan = StudyPlan(
            subject=request.form.get("subject"),
            study_date=datetime.strptime(request.form.get("study_date"), "%Y-%m-%d").date(),
            duration=int(request.form.get("duration")),
            completed=request.form.get("completed") == "on",
            user_id=current_user.id
        )
        db.session.add(plan)
        db.session.commit()
        flash("Study plan added successfully!")
        return redirect(url_for("planner"))
    return render_template("add_plan.html")

@app.route("/planner/edit/<int:id>")
@login_required
def edit_plan(id):
    plan = StudyPlan.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template("edit_plan.html", plan=plan)

@app.route("/planner/update/<int:id>", methods=["POST"])
@login_required
def update_plan(id):
    plan = StudyPlan.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    plan.subject = request.form.get("subject")
    plan.study_date = datetime.strptime(request.form.get("study_date"), "%Y-%m-%d").date()
    plan.duration = int(request.form.get("duration"))
    plan.completed = request.form.get("completed") == "on"
    db.session.commit()
    flash("Study plan updated successfully!")
    return redirect(url_for("planner"))

@app.route("/planner/quick-add-dashboard", methods=["POST"])
@login_required
def quick_add_dashboard():
    subject = request.form.get("subject")
    duration = request.form.get("duration", 30)
    if subject:
        plan = StudyPlan(
            subject=subject,
            study_date=datetime.today().date(),
            duration=int(duration) if duration else 30,
            completed=False,
            user_id=current_user.id
        )
        db.session.add(plan)
        db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/planner/toggle/<int:id>", methods=["POST"])
@login_required
def toggle_plan_dashboard(id):
    plan = StudyPlan.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    data = request.get_json() or {}
    plan.completed = data.get("completed", False)
    db.session.commit()
    return {"success": True}

@app.route("/planner/delete-inline/<int:id>", methods=["POST"])
@login_required
def delete_plan_inline(id):
    plan = StudyPlan.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(plan)
    db.session.commit()
    return {"success": True}

@app.route("/planner/delete/<int:id>", methods=["POST"])
@login_required
def delete_plan(id):
    plan = StudyPlan.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(plan)
    db.session.commit()
    flash("Study plan deleted successfully!")
    return redirect(url_for("planner"))

# -------------------------
# Semester Goals Tracker
# -------------------------
@app.route("/goals")
@login_required
def goals():
    goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.id.desc()).all()
    return render_template("goals.html", goals=goals)

@app.route("/goals/add", methods=["GET", "POST"])
@login_required
def add_goal():

    if request.method == "POST":

        completed = request.form.get("completed") == "True"

        if completed:
            progress = 100
        else:
            progress = min(int(request.form.get("progress")), 99)

        goal = Goal(
            goal_title=request.form.get("goal_title"),
            progress=progress,
            completed=completed,
            user_id=current_user.id
        )

        db.session.add(goal)
        db.session.commit()

        flash("Goal added successfully!")
        return redirect(url_for("goals"))

    return render_template("add_goal.html")

@app.route("/goals/edit/<int:id>")
@login_required
def edit_goal(id):

    goal = Goal.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "edit_goal.html",
        goal=goal
    )

@app.route("/goals/update/<int:id>", methods=["POST"])
@login_required
def update_goal(id):

    goal = Goal.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    completed = request.form.get("completed") == "True"

    if completed:
        progress = 100
    else:
        progress = min(int(request.form.get("progress")), 99)

    goal.goal_title = request.form.get("goal_title")
    goal.progress = progress
    goal.completed = completed

    db.session.commit()

    flash("Goal updated successfully!")
    return redirect(url_for("goals"))

@app.route("/goals/delete/<int:id>", methods=["POST"])
@login_required
def delete_goal(id):
    goal = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    flash("Goal deleted successfully!")
    return redirect(url_for("goals"))

# -------------------------
# Important Links
# -------------------------
@app.route("/links")
@login_required
def links():
    links = ImportantLink.query.filter_by(user_id=current_user.id).all()
    return render_template("links.html", links=links)

@app.route("/links/add", methods=["GET", "POST"])
@login_required
def add_link():
    if request.method == "POST":
        link = ImportantLink(title=request.form.get("title"), url=request.form.get("url"), user_id=current_user.id)
        db.session.add(link)
        db.session.commit()
        flash("Link added successfully!")
        return redirect(url_for("links"))
    return render_template("add_link.html")

# -------------------------
# Timetable
# -------------------------
@app.route("/timetable")
@login_required
def timetable():
    timetable_entries = Timetable.query.filter_by(user_id=current_user.id).all()
    return render_template("timetable.html", timetable_entries=timetable_entries)

@app.route("/timetable/add", methods=["GET", "POST"])
@login_required
def add_timetable():
    if request.method == "POST":
        entry = Timetable(
            subject=request.form.get("subject"),
            day=request.form.get("day"),
            start_time=request.form.get("start_time"),
            end_time=request.form.get("end_time"),
            room=request.form.get("room"),
            user_id=current_user.id
        )
        db.session.add(entry)
        db.session.commit()
        flash("Class added successfully!")
        return redirect(url_for("timetable"))
    return render_template("add_timetable.html")

@app.route("/timetable/edit/<int:id>")
@login_required
def edit_timetable(id):
    entry = Timetable.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template("edit_timetable.html", entry=entry)

@app.route("/timetable/update/<int:id>", methods=["POST"])
@login_required
def update_timetable(id):
    entry = Timetable.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    entry.subject = request.form.get("subject")
    entry.day = request.form.get("day")
    entry.start_time = request.form.get("start_time")
    entry.end_time = request.form.get("end_time")
    entry.room = request.form.get("room")
    db.session.commit()
    flash("Class updated successfully!")
    return redirect(url_for("timetable"))

@app.route("/timetable/delete/<int:id>", methods=["POST"])
@login_required
def delete_timetable(id):
    entry = Timetable.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(entry)
    db.session.commit()
    flash("Class deleted successfully!")
    return redirect(url_for("timetable"))



# -------------------------
# Profile Module
# -------------------------
@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")

@app.route("/profile/edit")
@login_required
def edit_profile():
    return render_template("edit_profile.html")

@app.route("/profile/update", methods=["POST"])
@login_required
def update_profile():

    current_user.username = request.form.get("username")
    current_user.university = request.form.get("university")
    current_user.program = request.form.get("program")
    current_user.semester = request.form.get("semester")

    db.session.commit()

    flash("Profile updated successfully!")

    return redirect(url_for("profile"))


if __name__ == "__main__":
    app.run(debug=True)