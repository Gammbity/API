from flask import Flask, render_template, request, jsonify
import secrets
import os

app = Flask(__name__, template_folder="templates")

dir = "users_files"

@app.route("/", methods=["GET"])
def main():
    return render_template("registration.html", name="Registration page")

@app.route("/submit/", methods=["POST"])
def registration():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    token = secrets.token_hex(8)
    file_name = f"{email}.txt"
    file_path = os.path.join(dir, file_name)
    if os.path.exists(file_path):
        return jsonify({'error': 'Foydalanuvchi allaqachon ro‘yxatdan o‘tgan!'}), 400
    with open(file_path, 'w') as file:
        file.write(f"Name: {name}\nEmail: {email}\nPassword: {password}\nToken: {token}")
    with open('users.csv', 'a') as file:
        file.writelines(f"{name},{email},{password},{token}\n")
    return render_template("my_file.html", name="Create Post page")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='5000')
