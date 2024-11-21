from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import json
import hmac
import hashlib
import base64


SECRET_KEY = "debug" # token yaratish uchun kerak

app = Flask(__name__, template_folder="templates", static_folder="static") # html, css fayllarni qayerdaligini ko'rsatish

app.secret_key = SECRET_KEY 

dir = "users_files" # user file qo'shilayotganda qayerga qo'shilish manzili

def decode_token(token):
        
        # tokenni usernamega aylantirish uchun funksiya

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

@app.route("/", methods=["GET"])
def main():
    if 'token' in session: # session ni ichida token degan o'zgaruvchi bormi shuni tekshiradi
        file = decode_token(session['token']) # tokenni decode qilib usernameni oladi
        with open(f"users_files/{file}.txt") as file: # shu username ga mos file ni topadi
            data = file.readlines() # data ga file dagi malumotlar olinadi

        user = {}
        for i in data:
            key, value = i.split(":", 1) # key va valuega ajratadi misol: ' name ',  ' Abduboriy\n ' 
            user[key.strip().lower()] = value.strip() # buyerda key va value ning atrofidagi qo'shimchalar olib tashlanadi bo'shliqlar misol: 'name', 'Abduboriy' 
        return render_template("index.html", user=user) # index.html ga jo'natiladi
    return redirect(url_for('registration')) # agar sessionda token bo'lmasa bu degani hali user registration qilmagani uchun registration funksiyaga yuboriladi
    

@app.route("/auth/", methods=["POST", "GET"]) # method get va post bolsa ishlaydi /auth/ pathda yani url
def registration():
    if request.method == "POST": # kelayotgan method postlikka tekshiramiz
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password") # user malumotlari olinadi html da formdan jonatilgani uchun request.form.get() qilib olinmoqda
        payload = {'username': username} # tokenni username ga moslab yasalmoqda qayta decode qilish uchun
        payload_bytes = json.dumps(payload).encode('utf-8') # token yaratish jarayoni
        signature = hmac.new(SECRET_KEY.encode('utf-8'), payload_bytes, hashlib.sha256).digest() # token yaratish jarayoni
        token = base64.urlsafe_b64encode(payload_bytes + b"." + signature).decode('utf-8') # token yaratish jarayoni
        file_name = f"{username}.txt" # user ning username miga moslab file ochiladi qaysi fayl kimga tegishli ekanligini topish uchun
        file_path = os.path.join(dir, file_name) # faylni ko'rsatilgan papkaga qo'shadi
        if os.path.exists(file_path): # agar fayl bor bo'lsa demak bu user allaqachon royhatdan otgan
            return jsonify({'error': 'Foydalanuvchi allaqachon ro‘yxatdan o‘tgan!'}), 400 # hatolik
        with open(file_path, 'w') as file: # user malumotlarini shaxsiy fayliga yozish 
            file.write(f"Name: {name}\nusername: {username}\nPassword: {password}\nToken: {token}")
        with open('users.csv', 'a') as file: # user larni saqlab ketish uchun fayl
            file.writelines(f"{name},{username},{password},{token}\n")
        session['token'] = token # session ga token beriladi barcha jarayon amalga oshgandan keyin yani user registratsiya qildi
        return redirect(url_for("main")) # va asosiy sahifaga malumotlarini ko'rish sahifasiga jo'natiladi
    return render_template("registration.html") # agar method POST bo'lmasa registration.html ga jo'natadi




if __name__ == "__main__": 
    os.makedirs(dir, exist_ok=True) # users_files papkasini yaratib qo'yadi agar yo'q bo'lsa
    app.run(debug=True, host='0.0.0.0', port='5000') # serverni run qilish uchun wifi orqali istalgan kishi ulanadi
