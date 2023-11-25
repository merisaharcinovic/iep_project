from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, User, UserRole
from flask_jwt_extended import JWTManager, create_refresh_token, create_access_token, jwt_required, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_
from adminDecorator import roleCheck
import re

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/register", methods=["POST"])
def register():
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    isCustomer = request.json.get("isCustomer", None)

    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0
    forenameEmpty = len(forename) == 0
    surnameEmpty = len(surname) == 0
    isCustomerEmpty = isCustomer is None

    if forenameEmpty:
        return jsonify({"message": "Field forename is missing."}), 400
    if surnameEmpty:
        return jsonify({"message": "Field surname is missing."}), 400
    if emailEmpty:
        return jsonify({"message": "Field email is missing."}), 400
    if passwordEmpty:
        return jsonify({"message": "Field password is missing."}), 400
    if isCustomerEmpty:
        return jsonify({"message": "Field isCustomer is missing."}), 400

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(regex, email):
        return jsonify({"message": "Invalid email."}), 400

    passwordUpper = any(ele.isupper() for ele in password)
    passwordLower = any(ele.islower() for ele in password)
    passwordNum = False
    for character in password:
        if character.isdigit():
            passwordNum = True
            break

    passwordValid = len(password) >= 8 and passwordLower and passwordUpper and passwordNum

    if not passwordValid:
        return jsonify({"message": "Invalid password."}), 400

    user = User.query.filter(User.email == email).first()
    if user:
        return jsonify({"message": "Email already exists."}), 400

    user = User(email=email, password=password, forename=forename, surname=surname)
    database.session.add(user)
    database.session.commit()

    if isCustomer:
        roleId = 2
    else:
        roleId = 3

    userRole = UserRole(userId=user.id, roleId=roleId)
    database.session.add(userRole)
    database.session.commit()

    return Response(status=200)


@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0

    if emailEmpty:
        return jsonify({"message": "Field email is missing."}), 400
    if passwordEmpty:
        return jsonify({"message": "Field password is missing."}), 400

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(regex, email):
        return jsonify({"message": "Invalid email."}), 400

    user = User.query.filter(and_(User.email == email, User.password == password)).first()
    if not user:
        return jsonify({"message": "Invalid credentials."}), 400

    additionalClaims = {
        "forename": user.forename,
        "surname": user.surname,
        "email": user.email,
        "roles": [str(role) for role in user.roles]
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims,
                                      expires_delta=Configuration.JWT_ACCESS_TOKEN_EXPIRES)
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims,
                                        expires_delta=Configuration.JWT_REFRESH_TOKEN_EXPIRES)
    return jsonify(accessToken=accessToken, refreshToken=refreshToken)


@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refreshClaims = get_jwt()

    # token = request.headers.get("Authorization", "")
    # if len(token) == 0:
    #     return Response(jsonify(msg="Missing Authorization Header"), status=401)

    additionalClaims = {
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "email": refreshClaims["email"],
        "roles": refreshClaims["roles"],
    }

    return jsonify(accessToken=create_access_token(identity=identity, additional_claims=additionalClaims))


@application.route("/delete", methods=["POST"])
@jwt_required()
@roleCheck(role="admin")
def delete():
    email = request.json.get("email", "")
    if len(email) == 0:
        return jsonify({"message": "Field email is missing."}), 400

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(regex, email):
        return jsonify({"message": "Invalid email."}), 400

    user = User.query.filter(User.email == email).first()
    if user is None:
        return jsonify({"message": "Unknown user."}), 400

    # delete user
    database.session.delete(user)
    database.session.commit()
    return Response(status=200)

@application.route("/", methods=["GET"])
def index():
    return "hello world."

if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True,host='0.0.0.0', port=5001)
