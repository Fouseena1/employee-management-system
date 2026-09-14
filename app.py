from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/login', methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        return f"username: {username}, password: {password}"

    return render_template("login.html")


@app.route('/register', methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        return f"username: {username}, password: {password}, confirm_password: {confirm_password}"

    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)
