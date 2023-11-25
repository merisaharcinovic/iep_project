from flask_sqlalchemy import SQLAlchemy
import datetime

database = SQLAlchemy()


class ProductCategory(database.Model):
    __tablename__ = "productcategory";
    product_id = database.Column(database.Integer,database.ForeignKey('product.id', ondelete='CASCADE', onupdate='CASCADE'),
                                 primary_key=True)
    category_id = database.Column(database.Integer,database.ForeignKey('category.id', ondelete='CASCADE', onupdate='CASCADE'),
                                  primary_key=True)


class Category(database.Model):
    __tablename__ = "category"
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(50), unique=True, nullable=False)
    products = database.relationship('Product', secondary=ProductCategory.__table__,
                                     back_populates='categories', cascade="all,delete")

    def __repr__(self):
        return self.name

class ProductOrder(database.Model):
    __tablename__ = "productorder"

    id = database.Column(database.Integer, primary_key=True)
    product_id = database.Column(database.Integer, database.ForeignKey("product.id"), nullable=False)
    order_id = database.Column(database.Integer, database.ForeignKey("order.id"), nullable=False)
    requested = database.Column(database.Integer, nullable=False)
    recieved = database.Column(database.Integer, nullable=False)
    price = database.Column(database.Float, nullable=False)

class Product(database.Model):
    __tablename__ = "product"
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(50), unique=True, nullable=False)
    quantity = database.Column(database.Integer, nullable=False)
    price = database.Column(database.Float, nullable=False)
    categories = database.relationship('Category', secondary=ProductCategory.__table__,
                                       back_populates='products', cascade="all,delete")
    orders = database.relationship("Order", secondary=ProductOrder.__table__, back_populates="products")

    def __repr__(self):
        return f"{self.id} {self.name} {self.quantity} {self.price} {self.categories}"

class Order(database.Model):
    __tablename__ = "order"

    id = database.Column(database.Integer, primary_key=True)
    price = database.Column(database.Float, nullable=False)
    status = database.Column(database.String(20), nullable=False)
    timestamp = database.Column(database.DateTime, nullable=False, default=datetime.datetime.now())
    email = database.Column(database.String(256), nullable=False)

    products = database.relationship("Product", secondary=ProductOrder.__table__, back_populates="orders")

    def __repr__(self):
        return f" ID: {self.id}, {self.email}, price;{self.price}, status:{self.status}"