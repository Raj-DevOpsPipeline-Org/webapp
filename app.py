import os

import psycopg2
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from assignments import assignments_bp
from extensions import auth
from models import Account, db
from populate_db import populate_db

# Load environment variables
load_dotenv('/opt/webapp.properties')

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
if not database_exists(engine.url):
    create_database(engine.url)
    print("Database created:")

# Flask app setup
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.register_blueprint(assignments_bp)

# Initialize the database
db.init_app(app)

# Initialize the Flask_migrate
migrate = Migrate(app, db)

# Initialize the Bcrypt
bcrypt = Bcrypt(app)


# Database Health check
@app.route("/healthz", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def database_health_check():
    # add required Headers
    headers = {
        "Content-Length": "0",
    }

    if request.method != "GET":
        return Response(status=405, headers=headers)

    if request.data or request.form or request.args:
        return Response(status=400, headers=headers)

    try:
        connection = psycopg2.connect(os.getenv("DATABASE_URL"))
        connection.close()
        response = Response(status=200, headers=headers)

    except Exception:
        response = Response(status=503, headers=headers)

    return response


# add required Headers
@app.after_request
def modify_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["content-type"] = "application/json"
    return response


def create_tables():
    with app.app_context():
        db.create_all()


# CLI command to populate database from csv
@app.cli.command("populate_db")
def populate_db_command():
    csv_path = os.getenv("CSV_PATH", "/opt/users.csv")
    if not csv_path:
        print("CSV_PATH environment variable not set!")
        return
    try:
        populate_db(csv_path, bcrypt)
        print("Database populated!")
    except Exception as e:
        print(f"An error occurred: {e}")


# with app.app_context():
#     populate_db("users.csv", bcrypt)


def check_password(hashed_pw, password):
    return bcrypt.check_password_hash(hashed_pw, password)


# verify base64 encoded username and password with HTTPBasic auth
@auth.verify_password
def verify_password(email, password):
    try:
        if not email or not password:
            return False
        user = Account.query.filter_by(email=email).first()
        if user and check_password(user.password, password):
            return user
        return False

    except SQLAlchemyError:
        return jsonify({"message": "Database error occurred."}), 503

    except Exception as e:
        return (
            jsonify({"message": "Unable to fetch assignments."}),
            400,
        )
