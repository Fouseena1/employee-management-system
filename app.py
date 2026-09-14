from flask import Flask, render_template, request, session, redirect
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
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

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

if __name__ == "__main__":
    app.run(debug=True)
