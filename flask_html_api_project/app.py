from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    message = None

    if request.method == "POST":
        message = "Welcome to My Flask App"

    return render_template("home.html", message=message)


@app.route("/contact", methods=["GET", "POST"])
def contact():

    message = ""
    error = ""

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")

        if not name or not email:
            error = "Name and Email are required!"
        else:
            message = f"Form submitted successfully! Name: {name}, Email: {email}"

    return render_template("contact.html", message=message, error=error)


if __name__ == "__main__":
    app.run(debug=True)