from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

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
            return "Login Successful"

        return "Invalid username or password"

    return render_template("login.html")


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
