from flask import Flask, render_template, request, jsonify, session
import os
import json
import hmac
import hashlib
import base64


SECRET_KEY = "debug"

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = SECRET_KEY

dir = "users_files"

@app.route("/", methods=["GET"])
def main():
    isTokenHave = False
    if 'token' in session:
        isTokenHave = True
    return render_template("index.html", name="", token=isTokenHave)

@app.route("/submit/", methods=["POST"])
def registration():
    data = json.loads(request.data)
    name = data.get("name")
    username = data.get("username")
    password = data.get("password")
    payload = {'username': username}
    payload_bytes = json.dumps(payload).encode('utf-8')
    signature = hmac.new(SECRET_KEY.encode('utf-8'), payload_bytes, hashlib.sha256).digest()
    token = base64.urlsafe_b64encode(payload_bytes + b"." + signature).decode('utf-8')
    file_name = f"{username}.txt"
    file_path = os.path.join(dir, file_name)
    if os.path.exists(file_path):
        return jsonify({'error': 'Foydalanuvchi allaqachon ro‘yxatdan o‘tgan!'}), 400
    with open(file_path, 'w') as file:
        file.write(f"Name: {name}\nusername: {username}\nPassword: {password}\nToken: {token}")
    with open('users.csv', 'a') as file:
        file.writelines(f"{name},{username},{password},{token}\n")
    session['token'] = token
    return jsonify({
        "token":token
    }), 200

def decode_token(token):
    try:
        token_bytes = base64.urlsafe_b64decode(token.encode('utf-8'))
        payload_bytes, signature = token_bytes.rsplit(b".", 1)
        expected_signature = hmac.new(SECRET_KEY.encode('utf-8'), payload_bytes, hashlib.sha256).digest()

        if not hmac.compare_digest(signature, expected_signature):
            return "Token noto'g'ri yoki buzilgan!"

        payload = json.loads(payload_bytes)
        return payload["username"]
    except Exception:
        return "Token noto'g'ri yoki buzilgan!"

if __name__ == "__main__":
    os.makedirs(dir, exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port='5000')
