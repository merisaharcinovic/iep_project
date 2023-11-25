import datetime
import json

from flask import Flask, request, Response, jsonify
from flask_jwt_extended import get_jwt_identity, JWTManager

from configuration import Configuration
from models import database, Product, Category, Order, ProductOrder, ProductCategory

from adminDecorator import roleCheck
from sqlalchemy import and_

application = Flask(__name__)
application.config.from_object(Configuration)


@application.route('/search', methods=["GET"])
@roleCheck(role='customer')
def search():
    product_name = request.args.get('name')
    category_name = request.args.get('category')

    if not product_name:
        product_name = ""
    if not category_name:
        category_name = ""

    products = Product.query.filter(Product.name.contains(product_name)).all()
    categories = Category.query.filter(Category.name.contains(category_name)).all()

    products_categories = [p for p in products if any(c in categories for c in p.categories)]
    categories_products = []

    for p in products_categories:
        categories_products.extend(p.categories)
    categories_products = set(categories_products)

    products_list = []
    for product in products_categories:
        product_dict = {
            'categories': [c.name for c in product.categories],
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "quantity": product.quantity
        }
        products_list.append(product_dict)

    return jsonify({
        'products': products_list,
        'categories': [c.name for c in list(categories_products)]
    }), 200


@application.route("/order", methods=["POST"])
@roleCheck(role='customer')
def order():
    data = json.loads(request.data)
    if 'requests' not in data:
        return jsonify({'message': 'Field requests is missing.'}), 400
    customer_email = get_jwt_identity()
    total_price = 0
    order_items = []
    productsDB = []
    i = 0
    for req in data['requests']:
        if 'id' not in req:
            return jsonify({'message': f'Product id is missing for request number {i}.'}), 400
        if 'quantity' not in req:
            return jsonify({'message': f'Product quantity is missing for request number {i}.'}), 400
        try:
            product_id = int(req['id'])
        except ValueError:
            return jsonify({'message': f'Invalid product id for request number {i}.'}), 400

        try:
            quantity = int(req['quantity'])
        except ValueError:
            return jsonify({'message': f'Invalid product quantity for request number {i}.'}), 400

        if product_id <= 0:
            return jsonify({'message': f'Invalid product id for request number {i}.'}), 400
        if quantity <= 0:
            return jsonify({'message': f'Invalid product quantity for request number {i}.'}), 400

        product = Product.query.filter_by(id=product_id).first()
        if product is None:
            return jsonify({'message': f'Invalid product for request number {i}.'}), 400
        i += 1

    for rq in data['requests']:
        product_id = int(rq['id'])
        quantity = int(rq['quantity'])
        product = Product.query.filter_by(id=product_id).first()

        recieved = 0
        if product.quantity >= quantity:
            recieved = quantity
        elif product.quantity < quantity:
            recieved = product.quantity

        orderedProduct = ProductOrder(product_id=product.id, requested=quantity, recieved=recieved, price=product.price)
        newQty = product.quantity - recieved
        product.quantity = newQty
        order_items.append(orderedProduct)

        total_price += product.price * quantity


    database.session.commit()

    newOrder = Order(
        email=customer_email,
        timestamp=datetime.datetime.utcnow(),
        price=total_price,
        products=productsDB
    )

    pending = False
    for item in order_items:
        if item.requested != item.recieved:
            pending = True

    if not pending:
        newOrder.status = "COMPLETE"
    else:
        newOrder.status = "PENDING"

    database.session.add(newOrder)
    database.session.commit()
    print(newOrder)

    for item in order_items:
        item.order_id = newOrder.id
        database.session.add(item)
    database.session.commit()

    return jsonify({'id': newOrder.id}), 200


@application.route("/status", methods=["GET"])
@roleCheck(role='customer')
def status():
    customer_email = get_jwt_identity()
    orders = Order.query.filter_by(email=customer_email).all()
    orders_list = []

    for myorder in orders:
        products_list = []
        for product in myorder.products:
            productFromOrder = ProductOrder.query.filter_by(order_id=myorder.id, product_id=product.id).first()
            # mainProduct = Product.query.filter_by(id=productFromOrder.product_id).first()
            product_dict = {
                'name': product.name,
                'price': productFromOrder.price,
                'categories': [c.name for c in product.categories],
                'requested': productFromOrder.requested,
                'received': productFromOrder.recieved
            }
            products_list.append(product_dict)

        order_dict = {
            'products': products_list,
            'price': myorder.price,
            'status': myorder.status,
            'timestamp': myorder.timestamp.isoformat(),
        }
        orders_list.append(order_dict)

    return jsonify({'orders': orders_list}), 200


if __name__ == "__main__":
    jwt = JWTManager(application)
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
