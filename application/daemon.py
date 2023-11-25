import datetime
import json

from flask import Flask
from redis import Redis
from sqlalchemy import and_, asc

from configuration import Configuration
from models import Product, Category, database, Order, ProductOrder

application = Flask(__name__)
application.config.from_object(Configuration)
database.init_app(application)

while True:
    try:
        while True:
            with Redis(host=Configuration.REDIS_HOST) as redis:
                with application.app_context():
                    bytesString = redis.lrange("products", 0, 0)
                    if bytesString == None or len(bytesString) == 0:
                        continue
                    redis.lpop("products")

                    json_string = bytesString[0].decode('utf-8')
                    product = json.loads(json_string)

                    category_names = product["categories"]
                    name = product["name"]
                    qty = int(product["qty"])
                    price = float(product["price"])
                    productDB = Product.query.filter_by(name=name).first()
                    if not productDB:
                        new_categories = []
                        for category in category_names:
                            categoryExists = Category.query.filter_by(name=category).first()
                            if not categoryExists:
                                categoryExists = Category(name=category)
                                database.session.add(categoryExists)
                                database.session.commit()
                            new_categories.append(categoryExists)

                        newProduct = Product(name=name, quantity=qty, price=price, categories=new_categories)
                        database.session.add(newProduct)
                        database.session.commit()
                    else:
                        product_categories = [p.name for p in productDB.categories]
                        if set(product_categories) != set(category_names):
                            continue
                        else:
                            productDB.price = round(
                                ((productDB.quantity * productDB.price + qty * price) / (productDB.quantity + qty)), 2)
                            old_quant = productDB.quantity
                            newQty = productDB.quantity + qty
                            productDB.quantity = newQty

                            database.session.commit()

                    #               check if someone is waiting for this product
                    pendingOrders = Order.query.filter_by(status='PENDING').order_by(Order.timestamp).all()

                    for order in pendingOrders:
                        for product_in_order in order.products:
                            if product_in_order.quantity > 0:
                                productOrder = ProductOrder.query.filter_by(order_id=order.id,
                                                                            product_id=product_in_order.id).first()

                                waitingFor = productOrder.requested - productOrder.recieved
                                if waitingFor > 0:
                                        if product_in_order.quantity >= waitingFor:
                                            product_in_order.quantity -= waitingFor
                                            productOrder.recieved += waitingFor
                                            database.session.commit()

                                        elif product_in_order.quantity < waitingFor:
                                            productOrder.recieved += product_in_order.quantity
                                            product_in_order.quantity = 0
                                            database.session.commit()

                        # for order in pendingOrders:
                        pending = False
                        for product_in_order in order.products:
                            productOrder = ProductOrder.query.filter_by(order_id=order.id,product_id=product_in_order.id).first()
                            if productOrder.recieved != productOrder.requested:
                                pending = True
                                break

                        if not pending:
                            order.status = 'COMPLETE'
                            database.session.commit()

    finally:
        pass
