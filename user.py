from flask import Flask, render_template, request
import secrets

app = Flask(__name__, template_folder="templates")

users = {}

@app.route("/", methods=["GET"])
def main():
    return render_template("registration.html", name="Registration page")

@app.route("/submit/", methods=["POST"])
def registration():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    token = secrets.token_hex(8)
    index = len(users)
    users[index] = {"name": name, "email": email, "password": password, "token": token}
    with open('users.csv', 'a') as file:
        file.writelines(f"{name},{email},{password},{token}\n")
    return render_template("create_post.html", name="Create Post page")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5000')
