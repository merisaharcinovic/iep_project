from flask import Flask, request, Response, jsonify

from adminDecorator import roleCheck
from configuration import Configuration
from models import database, Product, Category, ProductCategory, Order, ProductOrder
from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_refresh_token, create_access_token, jwt_required, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_, desc, asc

application = Flask(__name__)
application.config.from_object(Configuration)


@application.route('/productStatistics', methods=['GET'])
@roleCheck(role='admin')
def productStatistics():
    statistics = []
    products = Product.query.all()
    added_products = []
    query_stats = []
    stats = Product.query \
        .join(ProductOrder, Product.id == ProductOrder.product_id) \
        .with_entities(Product.id, Product.name, database.func.sum(ProductOrder.requested).label('sold'),
                       database.func.sum(ProductOrder.requested - ProductOrder.recieved).label('waiting')) \
        .group_by(Product.id, Product.name).all()
    for s in stats:
        query_stat = {"name": str(s[1]), "sold": int(s[2]), "waiting": int(s[3])}
        query_stats.append(query_stat)
    print(query_stats)

    return jsonify({'statistics': query_stats}), 200


@application.route('/categoryStatistics', methods=['GET'])
@roleCheck(role='admin')
def getCategoryStatistics():
    categories = Category.query \
        .join(ProductCategory, Category.id == ProductCategory.category_id, isouter=True) \
        .join(ProductOrder, ProductCategory.product_id == ProductOrder.product_id,isouter=True) \
        .with_entities(Category.id, Category.name, database.func.coalesce(database.func.sum(ProductOrder.requested),0).label('sold')) \
        .group_by(Category.id, Category.name) \
        .order_by(desc('sold'), asc(Category.name)).all()


    result = {"statistics":[c.name for c in categories]}
    return jsonify(result), 200


if __name__ == "__main__":
    jwt = JWTManager(application)
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5004)
