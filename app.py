from flask import Flask, render_template, request, session,  redirect ,url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    hashed_password = db.Column(db.String(200), nullable=False)


class Employee(db.Model):
    __tablename__ = "employees"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Integer, nullable=False)


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
            return redirect("/dashboard")

        return "Invalid username or password"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    return render_template("dashboard.html", username=username)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/login")

@app.route('/register', methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not password or not confirm_password:
            return "All fields are required"

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return "Username already exists"

        if password != confirm_password:
            return "passwords do not match"

        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            hashed_password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        return "Registration Successful"

    return render_template("register.html")

@app.route("/add_employee", methods=["GET", "POST"])
def add_employee():

    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        department = request.form.get("department", "").strip()
        salary = request.form.get("salary", "")

        employee = Employee(
            name=name,
            email=email,
            department=department,
            salary=salary
        )

        db.session.add(employee)
        db.session.commit()

        return "employee added successfully"

    return render_template("add_employee.html")

@app.route("/employees")
def employees():

    if "username" not in session:
        return redirect(url_for("login"))

    employees = Employee.query.all()

    return render_template("employees.html", employees=employees)

@app.route("/edit_employee/<int:id>", methods=["GET", "POST"])
def edit_employee(id):

    if "username" not in session:
        return redirect(url_for("login"))

    employee = Employee.query.get_or_404(id)

    if request.method == "POST":
        employee.name = request.form.get("name", "").strip()
        employee.email = request.form.get("email", "").strip()
        employee.department = request.form.get("department", "").strip()
        employee.salary = request.form.get("salary", "")

        db.session.commit()

        return "Employee updated successfully"

    return render_template("edit_employee.html", employee=employee)

@app.route("/delete_employee/<int:id>", methods=["POST"])
def delete_employee(id):

    if "username" not in session:
        return redirect(url_for("login"))
    
    employee = Employee.query.get_or_404(id)

    db.session.delete(employee)
    db.session.commit()

    return redirect(url_for("employees"))

if __name__ == "__main__":
    app.run(debug=True)
