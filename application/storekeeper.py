import json

import redis
from flask import Flask, request, Response, jsonify
from flask_jwt_extended import jwt_required, JWTManager
import csv
import io

from adminDecorator import roleCheck
from configuration import Configuration
from models import database
from redis import Redis

application = Flask(__name__)
application.config.from_object(Configuration)




@application.route("/update", methods=["POST"])
@jwt_required()
@roleCheck(role="storekeeper")
def update():
    with Redis(host=Configuration.REDIS_HOST) as redis:
        if 'file' not in request.files:
            return jsonify({'message':'Field file is missing.'}), 400
        content = request.files["file"].read().decode("utf-8")
        if content is None:
            return jsonify({"message": "Field file is missing."}), 400
        stream = io.StringIO(content)
        reader = csv.reader(stream)
        products=[]
        i = 0
        for row in reader:
            if len(row) != 4:
                return jsonify({"message": "Incorrect number of values on line {}.".format(i)}), 400

            categories = row[0].split("|")
            name = row[1]
            qty = row[2]
            try:
                qty = int(row[2])
                if qty <= 0:
                    return jsonify({'message': f'Incorrect quantity on line {i}.'}), 400
            except ValueError:
                return jsonify({'message': f'Incorrect quantity on line {i}.'}), 400
                # check price
            try:
                price = float(row[3])
                if price <= 0:
                    return jsonify({'message': f'Incorrect price on line {i}.'}), 400
            except ValueError:
                return jsonify({'message': f'Incorrect price on line {i}.'}), 400

            product = {"categories": categories, "name": name, "qty": qty, "price": price}
            json_string = json.dumps(product)
            products.append(json_string)
            i = i + 1

        for p in products:
            redis.rpush("products", p)

        return Response(status=200)


if __name__ == "__main__":
    jwt = JWTManager(application)
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5003)
