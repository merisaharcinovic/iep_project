from flask_sqlalchemy import SQLAlchemy;

database = SQLAlchemy ( );

class UserRole ( database.Model ):
    __tablename__ = "userrole";

    id = database.Column ( database.Integer, primary_key = True );
    userId = database.Column ( database.Integer, database.ForeignKey ( "users.id" , ondelete="CASCADE" ), nullable = False  );
    roleId = database.Column ( database.Integer, database.ForeignKey ( "roles.id" ,  ondelete="CASCADE" ), nullable = False);


class User ( database.Model ):
    __tablename__ = "users";

    id = database.Column ( database.Integer, primary_key = True );
    email = database.Column ( database.String ( 256 ), nullable = False, unique = True );
    password = database.Column ( database.String(256), nullable = False );
    forename = database.Column ( database.String(256), nullable = False );
    surname = database.Column ( database.String(256), nullable = False );

    roles = database.relationship ( "Role", secondary = UserRole.__table__, back_populates = "users" );

class Role ( database.Model ):
    __tablename__ = "roles";

    id = database.Column ( database.Integer, primary_key = True );
    name = database.Column ( database.String ( 256 ), nullable = False );

    users = database.relationship ( "User", secondary = UserRole.__table__, back_populates = "roles" );

    def __repr__ ( self ):
        return self.name;
