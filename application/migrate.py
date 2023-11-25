import shutil

from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade;
from configuration import Configuration
from models import database
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

    print("Migrations done!")
