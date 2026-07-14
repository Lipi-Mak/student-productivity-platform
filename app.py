from datetime import datetime

from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    flash
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)

from config import Config
from models import (
    db,
    User,
    Assignment,
    Attendance,
    Timetable,
    Note,
    StudyPlan,
    Goal
)

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
# Home Route
# -------------------------
@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# -------------------------
# Register
# -------------------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

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
            password_hash=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.")

        return redirect(url_for("login"))

    return render_template("register.html")


# -------------------------
# Login
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):

            login_user(user)

            flash("Login successful!")

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")


# -------------------------
# Dashboard
# -------------------------
@app.route("/dashboard")
@login_required
def dashboard():

    assignments = Assignment.query.filter_by(
        user_id=current_user.id
    ).order_by(Assignment.due_date.asc()).limit(3).all()

    attendance_records = Attendance.query.filter_by(
        user_id=current_user.id
    ).all()

    notes = Note.query.filter_by(
        user_id=current_user.id
    ).order_by(Note.created_at.desc()).limit(3).all()

    study_plans = StudyPlan.query.filter_by(
        user_id=current_user.id
    ).order_by(StudyPlan.study_date.asc()).limit(3).all()

    goals = Goal.query.filter_by(
        user_id=current_user.id
    ).order_by(Goal.id.desc()).limit(3).all()

    return render_template(
        "dashboard.html",
        current_date=datetime.now().strftime("%A, %d %B %Y"),
        assignments=assignments,
        attendance_records=attendance_records,
        notes=notes,
        study_plans=study_plans,
        goals=goals
    )

# -------------------------
# Logout
# -------------------------
@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully.")

    return redirect(url_for("login"))

# -------------------------
# Assignments
# -------------------------

@app.route("/assignments")
@login_required
def assignments():

    assignments = Assignment.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "assignments.html",
        assignments=assignments
    )


@app.route("/assignment/add", methods=["GET", "POST"])
@login_required
def add_assignment():

    if request.method == "POST":

        title = request.form.get("title")
        subject = request.form.get("subject")
        due_date = request.form.get("due_date")
        priority = request.form.get("priority")
        status = request.form.get("status")


        due_date = datetime.strptime(
            due_date,
            "%Y-%m-%d"
        ).date()


        assignment = Assignment(
            title=title,
            subject=subject,
            due_date=due_date,
            priority=priority,
            status=status,
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

    assignment = Assignment.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "edit_assignment.html",
        assignment=assignment
    )


@app.route("/assignment/update/<int:id>", methods=["POST"])
@login_required
def update_assignment(id):

    assignment = Assignment.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    assignment.title = request.form.get("title")
    assignment.subject = request.form.get("subject")

    assignment.due_date = datetime.strptime(
        request.form.get("due_date"),
        "%Y-%m-%d"
    ).date()

    assignment.priority = request.form.get("priority")
    assignment.status = request.form.get("status")

    db.session.commit()

    flash("Assignment updated successfully!")

    return redirect(url_for("assignments"))


@app.route("/assignment/delete/<int:id>", methods=["POST"])
@login_required
def delete_assignment(id):

    assignment = Assignment.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first()

    if assignment:

        db.session.delete(assignment)
        db.session.commit()

        flash("Assignment deleted successfully!")

    else:

        flash("Assignment not found.")

    return redirect(url_for("assignments"))


# -------------------------
# Attendance List
# -------------------------

@app.route("/attendance")
@login_required
def attendance():

    attendance_records = Attendance.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "attendance.html",
        attendance_records=attendance_records
    )


# -------------------------
# Add Attendance
# -------------------------

@app.route("/attendance/add", methods=["GET", "POST"])
@login_required
def add_attendance():

    if request.method == "POST":

        new_record = Attendance(

            subject=request.form.get("subject"),

            attended_classes=int(
                request.form.get("attended_classes")
            ),

            total_classes=int(
                request.form.get("total_classes")
            ),

            user_id=current_user.id

        )

        db.session.add(new_record)
        db.session.commit()

        flash("Attendance added successfully!")

        return redirect(
            url_for("attendance")
        )

    return render_template(
        "add_attendance.html"
    )


# -------------------------
# Edit Attendance
# -------------------------

@app.route("/attendance/edit/<int:id>")
@login_required
def edit_attendance(id):

    record = Attendance.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "edit_attendance.html",
        record=record
    )


# -------------------------
# Update Attendance
# -------------------------

@app.route("/attendance/update/<int:id>", methods=["POST"])
@login_required
def update_attendance(id):

    record = Attendance.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    record.subject = request.form.get("subject")

    record.attended_classes = int(
        request.form.get("attended_classes")
    )

    record.total_classes = int(
        request.form.get("total_classes")
    )

    db.session.commit()

    flash("Attendance updated successfully!")

    return redirect(
        url_for("attendance")
    )


# -------------------------
# Delete Attendance
# -------------------------

@app.route("/attendance/delete/<int:id>", methods=["POST"])
@login_required
def delete_attendance(id):

    record = Attendance.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(record)

    db.session.commit()

    flash("Attendance deleted successfully!")

    return redirect(
        url_for("attendance")
    )




# -------------------------
# Notes Page
# -------------------------
@app.route("/notes")
@login_required
def notes():

    notes = Note.query.filter_by(
        user_id=current_user.id
    ).order_by(Note.created_at.desc()).all()

    return render_template(
        "notes.html",
        notes=notes
    )


# -------------------------
# Add Note
# -------------------------
@app.route("/notes/add", methods=["GET", "POST"])
@login_required
def add_note():

    if request.method == "POST":

        title = request.form.get("title")
        content = request.form.get("content")

        note = Note(
            title=title,
            content=content,
            user_id=current_user.id
        )

        db.session.add(note)
        db.session.commit()

        flash("Note added successfully!")

        return redirect(url_for("notes"))

    return render_template("add_note.html")


# -------------------------
# Edit Note
# -------------------------
@app.route("/notes/edit/<int:id>")
@login_required
def edit_note(id):

    note = Note.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "edit_note.html",
        note=note
    )


# -------------------------
# Update Note
# -------------------------
@app.route("/notes/update/<int:id>", methods=["POST"])
@login_required
def update_note(id):

    note = Note.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    note.title = request.form.get("title")
    note.content = request.form.get("content")

    db.session.commit()

    flash("Note updated successfully!")

    return redirect(url_for("notes"))


# -------------------------
# Delete Note
# -------------------------
@app.route("/notes/delete/<int:id>", methods=["POST"])
@login_required
def delete_note(id):

    note = Note.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(note)
    db.session.commit()

    flash("Note deleted successfully!")

    return redirect(url_for("notes"))




# -------------------------
# Study Planner Page
# -------------------------
@app.route("/planner")
@login_required
def planner():

    study_plans = StudyPlan.query.filter_by(
        user_id=current_user.id
    ).order_by(StudyPlan.study_date.asc()).all()

    return render_template(
        "planner.html",
        study_plans=study_plans
    )

# -------------------------
# Add Study Plan
# -------------------------
@app.route("/planner/add", methods=["GET", "POST"])
@login_required
def add_plan():

    if request.method == "POST":

        plan = StudyPlan(
            subject=request.form.get("subject"),
            study_date=datetime.strptime(
                request.form.get("study_date"),
                "%Y-%m-%d"
            ).date(),
            duration=int(request.form.get("duration")),
            completed=request.form.get("completed") == "on",
            user_id=current_user.id
        )

        db.session.add(plan)
        db.session.commit()

        flash("Study plan added successfully!")

        return redirect(url_for("planner"))

    return render_template("add_plan.html")


# -------------------------
# Edit Study Plan
# -------------------------
@app.route("/planner/edit/<int:id>")
@login_required
def edit_plan(id):

    plan = StudyPlan.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "edit_plan.html",
        plan=plan
    )


# -------------------------
# Update Study Plan
# -------------------------
@app.route("/planner/update/<int:id>", methods=["POST"])
@login_required
def update_plan(id):

    plan = StudyPlan.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    plan.subject = request.form.get("subject")
    plan.study_date = datetime.strptime(
        request.form.get("study_date"),
        "%Y-%m-%d"
    ).date()
    plan.duration = int(request.form.get("duration"))
    plan.completed = request.form.get("completed") == "on"

    db.session.commit()

    flash("Study plan updated successfully!")

    return redirect(url_for("planner"))


# -------------------------
# Delete Study Plan
# -------------------------
@app.route("/planner/delete/<int:id>", methods=["POST"])
@login_required
def delete_plan(id):

    plan = StudyPlan.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(plan)
    db.session.commit()

    flash("Study plan deleted successfully!")

    return redirect(url_for("planner"))




# -------------------------
# Goals Page
# -------------------------
@app.route("/goals")
@login_required
def goals():

    goals = Goal.query.filter_by(
        user_id=current_user.id
    ).order_by(Goal.id.desc()).all()

    return render_template(
        "goals.html",
        goals=goals
    )


# -------------------------
# Add Goal
# -------------------------
@app.route("/goals/add", methods=["GET", "POST"])
@login_required
def add_goal():

    if request.method == "POST":

        goal = Goal(
            goal_title=request.form.get("goal_title"),
            progress=int(request.form.get("progress")),
            completed=request.form.get("completed") == "on",
            user_id=current_user.id
        )

        db.session.add(goal)
        db.session.commit()

        flash("Goal added successfully!")

        return redirect(url_for("goals"))

    return render_template("add_goal.html")


# -------------------------
# Edit Goal
# -------------------------
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


# -------------------------
# Update Goal
# -------------------------
@app.route("/goals/update/<int:id>", methods=["POST"])
@login_required
def update_goal(id):

    goal = Goal.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    goal.goal_title = request.form.get("goal_title")
    goal.progress = int(request.form.get("progress"))
    goal.completed = request.form.get("completed") == "on"

    db.session.commit()

    flash("Goal updated successfully!")

    return redirect(url_for("goals"))


# -------------------------
# Delete Goal
# -------------------------
@app.route("/goals/delete/<int:id>", methods=["POST"])
@login_required
def delete_goal(id):

    goal = Goal.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(goal)
    db.session.commit()

    flash("Goal deleted successfully!")

    return redirect(url_for("goals"))


# -------------------------
# Timetable
# -------------------------

@app.route("/timetable")
@login_required
def timetable():

    timetable_entries = Timetable.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "timetable.html",
        timetable_entries=timetable_entries
    )


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

        return redirect(
            url_for("timetable")
        )


    return render_template(
        "add_timetable.html"
    )

# -------------------------
# Edit Timetable
# -------------------------

@app.route("/timetable/edit/<int:id>")
@login_required
def edit_timetable(id):

    entry = Timetable.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()


    return render_template(
        "edit_timetable.html",
        entry=entry
    )



# -------------------------
# Update Timetable
# -------------------------

@app.route("/timetable/update/<int:id>", methods=["POST"])
@login_required
def update_timetable(id):

    entry = Timetable.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()


    entry.subject = request.form.get("subject")
    entry.day = request.form.get("day")
    entry.start_time = request.form.get("start_time")
    entry.end_time = request.form.get("end_time")
    entry.room = request.form.get("room")


    db.session.commit()


    flash("Timetable updated successfully!")


    return redirect(
        url_for("timetable")
    )



# -------------------------
# Delete Timetable
# -------------------------

@app.route("/timetable/delete/<int:id>", methods=["POST"])
@login_required
def delete_timetable(id):

    entry = Timetable.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()


    db.session.delete(entry)

    db.session.commit()


    flash("Class deleted successfully!")


    return redirect(
        url_for("timetable")
    )

# -------------------------
# Run App
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)