from datetime import timedelta

import os
databaseUrl = os.environ["DATABASE_URL"]
redisUrl = os.environ["REDIS_URL"]

class Configuration():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/shop"
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost:3306/shop"
    # REDIS_HOST="localhost"
    REDIS_HOST=redisUrl
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)


    # --type
    # all
    # --with-authentication
    # --authentication-address
    # http://127.0.0.1:5001
    # --customer-address
    # http://127.0.0.1:5002
    # --warehouse-address
    # http://127.0.0.1:5003
    # --administrator-address
    # http://127.0.0.1:5004
    # --jwt-secret
    # "JWT_SECRET_KEY"
    # --roles-field
    # roles
    # --administrator-role
    # admin
    # --customer-role
    # customer
    # --warehouse-role
    # storekeeper