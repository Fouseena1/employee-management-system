from flask import Flask, render_template, request, session,  redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
from datetime import datetime


load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    hashed_password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="employee")


class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Integer, nullable=False)


class Leave(db.Model):
    __tablename__ = "leaves"

    id = db.Column(db.Integer, primary_key=True)

    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False)

    start_date = db.Column(db.Date, nullable=False)

    end_date = db.Column(db.Date, nullable=False)

    reason = db.Column(db.String(500), nullable=False)

    status = db.Column(db.String(20), nullable=False, default="Pending")

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/login', methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user is None:
            return "Invalid username or password"

        if check_password_hash(user.hashed_password, password):
            session["username"] = user.username
            session["role"] = user.role

            if user.role == "admin":
                return redirect("/admin-dashboard")


            return redirect("/employee-dashboard")

        return "Invalid username or password"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/add_employee", methods=["GET", "POST"])
def add_employee():

    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return "Access Denied"

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        department = request.form.get("department", "").strip()
        salary = request.form.get("salary", "").strip()

        # Check required fields
        if not name or not email or not department or not salary:
            return "All fields are required"

        if "@" not in email:
            return "Enter valid email address"

        try:
            salary = int(salary)
        except ValueError:
            return "Salary must be a number"

        if salary <= 0:
            return "Salary must be greater than 0"

        # Check whether username already exists
        existing_user = User.query.filter_by(username=email).first()

        if existing_user:
            return "An account with this email already exists"

        # Temporary password
        temporary_password = os.getenv("TEMPORARY_EMPLOYEE_PASSWORD")

        # Create User account
        user = User(
            username=email,
            hashed_password=generate_password_hash(temporary_password),
            role="employee"
        )

        db.session.add(user)
        db.session.flush()

        # Create Employee record
        employee = Employee(
            user_id=user.id,
            name=name,
            email=email,
            department=department,
            salary=salary
        )

        db.session.add(employee)

        db.session.commit()

        return redirect(url_for("employees"))

    return render_template("add_employee.html")

@app.route("/employees")
def employees():

    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return "Access Denied"

    employees = Employee.query.all()

    return render_template("employees.html", employees=employees)

@app.route("/edit_employee/<int:id>", methods=["GET", "POST"])
def edit_employee(id):

    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return "Access Denied"

    employee = Employee.query.get_or_404(id)

    if request.method == "POST":
        employee.name = request.form.get("name", "").strip()
        employee.email = request.form.get("email", "").strip()
        employee.department = request.form.get("department", "").strip()
        employee.salary = int(request.form.get("salary", "0"))

        db.session.commit()

        return redirect(url_for("employees"))

    return render_template(
        "edit_employee.html",
        employee=employee)

@app.route("/delete_employee/<int:id>", methods=["POST"])
def delete_employee(id):

    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return "Access Denied"
    
    employee = Employee.query.get_or_404(id)

    db.session.delete(employee)
    db.session.commit()

    return redirect(url_for("employees"))

@app.route("/admin-dashboard")
def admin_dashboard():

    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return "Access Denied"

    return render_template("admin_dashboard.html")


@app.route("/employee-dashboard")
def employee_dashboard():

    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "employee":
        return "Access Denied"

    return render_template("employee_dashboard.html")


@app.route("/my-profile")
def my_profile():

    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "employee":
        return "Access Denied"

    user = User.query.filter_by(username=session["username"]).first()

    employee = Employee.query.filter_by(user_id=user.id).first()

    if employee is None:
        return "Employee profile not found"

    return render_template("my_profile.html", employee=employee)


@app.route("/apply-leave", methods=["GET", "POST"])
def apply_leave():

    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "employee":
        return "Access Denied"

    user = User.query.filter_by(username=session["username"]).first()

    employee = Employee.query.filter_by(user_id=user.id).first()

    if employee is None:
        return "Employee profile not found"

    if request.method == "POST":


        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        reason = request.form.get("reason", "").strip()

        if not start_date or not end_date or not reason:
            return "All fields are required"

        # Convert date strings to date objects

        start_date = datetime.strptime(
            start_date,
     "%Y-%m-%d"
        ).date()

        end_date = datetime.strptime(
            end_date,
     "%Y-%m-%d"
        ).date()

        if start_date > end_date:
            return "End date must be after start date"


        leave = Leave(
            employee_id=employee.id,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )


        db.session.add(leave)
        db.session.commit()

        return "Leave applied Successfully"

    return render_template("apply_leave.html")

@app.route("/my-leaves")
def my_leaves():

    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "employee":
        return "Access Denied"

    user = User.query.filter_by(username=session["username"]).first()

    employee = Employee.query.filter_by(user_id=user.id).first()

    if employee is None:
        return "Employee profile not found"

    leaves = Leave.query.filter_by(employee_id=employee.id).all()

    return render_template("my_leaves.html", leaves=leaves)


@app.route("/leave-requests")
def leave_requests():

    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return "Access Denied"

    leaves = Leave.query.all()

    employee_data = []

    for leave in leaves:
        employee = Employee.query.get(leave.employee_id)
        employee_data.append((leave, employee))

    return render_template("leave_requests.html", employee_data=employee_data)

@app.route("/approve-leave/<int:id>", methods=["POST"])
def approve_leave(id):

    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return "Access Denied"

    # Find the leave request
    leave = Leave.query.get(id)

    if leave is None:
        return "Leave request not found"

    if leave.status != "Pending":
        return "Leave request already processed"

    # Approve pending leave request
    leave.status = "Approved"

    db.session.commit()

    return redirect(url_for("leave_requests"))

@app.route("/reject-leave/<int:id>", methods=["POST"])
def reject_leave(id):

    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return "Access Denied"

    # Find the leave request
    leave = Leave.query.get(id)

    if leave is None:
        return "Leave request not found"

    if leave.status != "Pending":
        return "Leave request already processed"

    # Find the leave request
    leave.status = "Rejected"

    db.session.commit()

    return redirect(url_for("leave_requests"))


if __name__ == "__main__":
    app.run()
