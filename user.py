from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import json
import base64
import re


SECRET_KEY = "detjhghg" # token yaratish uchun kerak

app = Flask(__name__, template_folder="templates", static_folder="static") # html, css fayllarni qayerdaligini ko'rsatish

app.secret_key = SECRET_KEY 


def decode_token(token):
    try:
        # Base64 formatdan dekodlash (padding to'g'irlash)
        padded_token = token + "=" * (-len(token) % 4)
        decoded_bytes = base64.urlsafe_b64decode(padded_token)

        # UTF-8 formatga o'tkazish va JSON ni o'qish            
        payload = json.loads(decoded_bytes.decode("utf-8"))

        # Username ni qaytarish
        return payload.get("username", "Username not found")
    except json.JSONDecodeError:
        return "Token JSON formatda emas"
    except base64.binascii.Error:
        return "Token Base64 formatda emas"
    except UnicodeDecodeError:
        return "Token UTF-8 formatda emas yoki noto'g'ri kodlangan"
    except Exception as e:
        print(f"Error decoding token: {e}")
        return 400

@app.route("/token/", methods=["GET"])
def main():
    if 'token' in session: # session ni ichida token degan o'zgaruvchi bormi shuni tekshiradi
        return render_template("token.html", token=session['token']) # token.html ga jo'natiladi
    return redirect(url_for('registration')) # agar sessionda token bo'lmasa bu degani hali user registration qilmagani uchun registration funksiyaga yuboriladi
    

@app.route("/auth/", methods=["POST", "GET"]) # method get va post bolsa ishlaydi /auth/ pathda yani url
def registration():
    if request.method == "POST": # kelayotgan method postlikka tekshiramiz
        name = request.form.get("name")
        username = request.form.get("username")#{"name":"Abduboriy", "username":"Gammbity", "password":"qwe123"}
        password = request.form.get("password") # user malumotlari olinadi html da formdan jonatilgani uchun request.form.get() qilib olinmoqda
        
            # Payload yaratisha  
        payload = {"username": username}
            # JSON ma'lumotlarni stringga aylantirish
        payload_json = json.dumps(payload)
            # UTF-8 formatda baytlarga aylantirish va Base64 formatda kodlash
        token = base64.urlsafe_b64encode(payload_json.encode("utf-8")).decode("utf-8")

        file_name = f"{username}.txt" # user ning username miga moslab file ochiladi qaysi fayl kimga tegishli ekanligini topish uchun  Gam.txt
        # print(file_name)
        # file_path = os.path.join('users_files', file_name) # faylni ko'rsatilgan papkaga qo'shadi
        # print(file_path) "users_files/gam.txt"
        file_path = f"users_files/{file_name}"
        print(file_path)
        if os.path.exists(file_path): # agar fayl bor bo'lsa demak bu user allaqachon royhatdan otgan
            return jsonify({'error': 'Foydalanuvchi allaqachon ro‘yxatdan o‘tgan!'}), 400 # hatolik
        with open(file_path, 'w') as file: # user malumotlarini shaxsiy fayliga yozish 
            file.write(f"Name: {name}\nusername: {username}\nPassword: {password}\nToken: {token}")
        with open('users.csv', 'a') as file: # user larni saqlab ketish uchun fayl
            file.write(f"{name},{username},{password},{token}\n")
        session['token'] = token # session ga token beriladi barcha jarayon amalga oshgandan keyin yani user registratsiya qildi
        return redirect(url_for("main")) # va asosiy sahifaga malumotlarini ko'rish sahifasiga jo'natiladi
    return render_template("registration.html") # agar method POST bo'lmasa registration.html ga jo'natadi

@app.route("/", methods=['POST', 'GET'])
def check_token():
    """
    Tokenni tekshirish uchun foydalanuvchi kirilgan tokenlarni qabul qiladi va agar token mavjud bo'lsa 
    shu token ga mos foydalanuvchining akkauntiga yozib qoyiladi qaysi user kirdi.
    Agar token mavjud bo'lmasa error beradi.
    """
    if request.method == "POST":
        personal_token = request.form.get('personal_token')
        if request.form['additional_token'] and personal_token != request.form['additional_tokengit']:
            additional_token = request.form.get('additional_token')
            personal_username = decode_token(personal_token) # tokenni decode qilib usernameni olad
            additional_username = decode_token(additional_token) # tokenni decode qilib usernameni olad
            if additional_username != 400:
                lenngth = 0
                with open(f"users_files/{additional_username}.txt", 'r') as file: # shu username ga mos file ni topadi
                    data = file.readlines() # data ga file dagi malumotlar olinadi
                    lenngth = len(data) # 
                with open(f"users_files/{additional_username}.txt", 'a') as file: # foydalanuvchi tomonidan kirilgan userning akkauntiga yozib qoyish qaysi user kirdi
                    file.write(f"\nVisitor-{lenngth-3}: {personal_username}")
                user = {}
                visitors = []
                for i in data:
                    key, value = i.split(":")# key va valuega ajratadi misol: ' name ',  ' Abduboriy\n ' 
                    if re.match(r'^Visitor-\d+$', key):
                        visitors.append(value)
                    user[key.strip().lower()] = value.strip() # buyerda key va value ning atrofidagi qo'shimchalar olib tashlanadi bo'shliqlar misol: 'name', 'Abduboriy' 
                return render_template("index.html", user=user, visitors=visitors) # token.html ga jo'natiladi
            return render_template("token.html", error="Token mavjud emas!")
        else:
            personal_username = decode_token(personal_token) # tokenni decode qilib usernameni olad 
            if personal_username != 400:
                with open(f"users_files/{personal_username}.txt", 'r') as file: # shu username ga mos file ni topadi
                    data = file.readlines() # data ga file dagi malumotlar olinadi
                user = {}
                visitors = []
                for i in data:
                    key, value = i.split(":", 1)# key va valuega ajratadi misol: ' name ',  ' Abduboriy\n ' 
                    if re.match(r'^Visitor-\d+$', key):
                        visitors.append(value)
                    user[key.strip().lower()] = value.strip() # buyerda key va value ning atrofidagi qo'shimchalar olib tashlanadi bo'shliqlar misol: 'name', 'Abduboriy' 
                return render_template("index.html", user=user, visitors=visitors) # token.html ga jo'natiladi
            return render_template("token.html", error="Token mavjud emas!")
    return redirect(url_for('registration')) # agar method POST bo'lmasa qaytadan funksiyani chaqiradi


if __name__ == "__main__": 
    os.makedirs('users_files', exist_ok=True) # users_files papkasini yaratib qo'yadi agar yo'q bo'lsa
    app.run(debug=True, host='0.0.0.0', port='5000') # serverni run qilish uchun wifi orqali istalgan kishi ulanadi
