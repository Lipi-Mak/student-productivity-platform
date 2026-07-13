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
from models import db, User, Assignment, Attendance


app = Flask(__name__)

app.config.from_object(Config)



# -------------------------
# Login Manager
# -------------------------

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"



@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))





# -------------------------
# Database
# -------------------------

db.init_app(app)


with app.app_context():

    db.create_all()





# -------------------------
# Home
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



        existing_user = User.query.filter_by(
            email=email
        ).first()



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



        user = User.query.filter_by(
            email=email
        ).first()



        if user and check_password_hash(
            user.password_hash,
            password
        ):


            login_user(user)


            flash("Login successful!")


            return redirect(
                url_for("dashboard")
            )



        flash("Invalid email or password.")



    return render_template("login.html")







# -------------------------
# Dashboard
# -------------------------

@app.route("/dashboard")
@login_required
def dashboard():


    upcoming_assignments = (
        Assignment.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Assignment.due_date
        )
        .limit(3)
        .all()
    )


    return render_template(
        "dashboard.html",
        current_date=datetime.now().strftime(
            "%A, %d %B %Y"
        ),
        upcoming_assignments=upcoming_assignments
    )







# -------------------------
# Logout
# -------------------------

@app.route("/logout")
@login_required
def logout():

    logout_user()


    flash("Logged out successfully.")


    return redirect(
        url_for("login")
    )







# -------------------------
# Assignment List
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


# -------------------------
# Add Assignment
# -------------------------

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



        new_assignment = Assignment(

            title=title,

            subject=subject,

            due_date=due_date,

            priority=priority,

            status=status,

            user_id=current_user.id

        )



        db.session.add(new_assignment)

        db.session.commit()



        flash("Assignment added successfully!")



        return redirect(
            url_for("assignments")
        )



    return render_template(
        "add_assignment.html"
    )


# -------------------------
# Edit Assignment Page
# -------------------------

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


# -------------------------
# Update Assignment
# -------------------------

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



    return redirect(
        url_for("assignments")
    )


# -------------------------
# Delete Assignment
# -------------------------

@app.route("/assignment/delete/<int:id>", methods=["POST"])
@login_required
def delete_assignment(id):


    assignment = Assignment.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()



    db.session.delete(assignment)

    db.session.commit()



    flash("Assignment deleted successfully!")



    return redirect(
        url_for("assignments")
    )



# -------------------------
# Attendance Page
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

        subject = request.form.get("subject")

        attended_classes = int(
            request.form.get("attended_classes")
        )

        total_classes = int(
            request.form.get("total_classes")
        )

        attendance = Attendance(
            subject=subject,
            attended_classes=attended_classes,
            total_classes=total_classes,
            user_id=current_user.id
        )

        db.session.add(attendance)
        db.session.commit()

        flash("Attendance record added successfully!")

        return redirect(url_for("attendance"))

    return render_template("add_attendance.html")


# -------------------------
# Edit Attendance
# -------------------------
@app.route("/attendance/edit/<int:id>", methods=["GET"])
@login_required
def edit_attendance(id):

    attendance = Attendance.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "edit_attendance.html",
        attendance=attendance
    )


# -------------------------
# Update Attendance
# -------------------------
@app.route("/attendance/update/<int:id>", methods=["POST"])
@login_required
def update_attendance(id):

    attendance = Attendance.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    attendance.subject = request.form.get("subject")
    attendance.attended_classes = int(
        request.form.get("attended_classes")
    )
    attendance.total_classes = int(
        request.form.get("total_classes")
    )

    db.session.commit()

    flash("Attendance updated successfully!")

    return redirect(url_for("attendance"))


# -------------------------
# Delete Attendance
# -------------------------
@app.route("/attendance/delete/<int:id>", methods=["POST"])
@login_required
def delete_attendance(id):

    attendance = Attendance.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(attendance)
    db.session.commit()

    flash("Attendance deleted successfully!")

    return redirect(url_for("attendance"))



# -------------------------
# Run App
# -------------------------

if __name__ == "__main__":

    app.run(debug=True)