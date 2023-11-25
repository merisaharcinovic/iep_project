import shutil

from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade;
from configuration import Configuration
from models import database, UserRole, Role, User
from flask_script import Manager
from sqlalchemy_utils import database_exists, create_database;

try:
    shutil.rmtree('migrations')
except:
    print("No directory migrations!")

app = Flask(__name__);
app.config.from_object(Configuration)

migrateObj = Migrate(app, database)

manager = Manager(app);

if (not database_exists(Configuration.SQLALCHEMY_DATABASE_URI)):
    create_database(Configuration.SQLALCHEMY_DATABASE_URI);

database.init_app(app);

with app.app_context() as context:
    init();
    migrate(message="Initial migration");
    upgrade()

    adminRole = Role(name="admin")
    customerRole = Role(name="customer")
    clerkRole = Role(name="storekeeper")

    database.session.add(adminRole)
    database.session.add(customerRole)
    database.session.add(clerkRole)
    database.session.commit()

    admin = User(email="admin@admin.com", forename="admin", surname="admin", password="1")

    database.session.add(admin)
    database.session.commit()
    adminid = admin.id

    adminUserRole = UserRole(
        userId=adminid,
        roleId=1
    )
    database.session.add(adminUserRole)
    database.session.commit()
    print("Migrations done!")
