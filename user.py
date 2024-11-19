from flask import Flask, render_template, request
from flask_restx import Api, Resource, fields
import secrets

app = Flask(__name__, template_folder="templates")
api = Api(app, version='1.0', title='User Registration API', description='A simple registration API with Swagger',
          doc='/docs')

users = {}

user_model = api.model('User', {
    'name': fields.String(description='The name of the user', required=True),
    'name': fields.String(description='The name of the user', required=True),
    'email': fields.String(description='The email of the user', required=True),
    'password': fields.String(description='The password of the user', required=True),
    'token': fields.String(description='Unique token for the user', required=True),
})


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

    return render_template("create_post.html", name="Create Post page")


@api.route('/users')
class UsersList(Resource):
    def get(self):
        return users

    @api.expect(user_model)
    @api.response(201, 'User successfully registered')
    def post(self):
        data = api.payload
        index = len(users)
        users[index] = {
            'name': data['name'],
            'email': data['email'],
            'password': data['password'],
            'token': secrets.token_hex(8)
        }
        return {'message': 'User successfully registered'}, 201


@api.route('/users/<int:user_id>')
class User(Resource):
    def get(self, user_id):
        if user_id not in users:
            api.abort(404, 'User not found')
        return users[user_id]

    @api.response(204, 'User successfully deleted')
    def delete(self, user_id):
        if user_id not in users:
            api.abort(404, 'User not found')
        del users[user_id]
        return '', 204


if __name__ == "__main__":
    app.run(debug=True)
