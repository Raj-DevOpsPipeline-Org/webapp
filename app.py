import logging
import os
import time
from logging import FileHandler

import psycopg2
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from pythonjsonlogger import jsonlogger
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_utils import create_database, database_exists
from statsd import StatsClient

from assignments import assignments_bp
from extensions import auth
from models import Account, db
from populate_db import populate_db

# Load environment variables
if os.path.exists("/opt/webapp.properties"):
    load_dotenv("/opt/webapp.properties")
else:
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
if not database_exists(engine.url):
    create_database(engine.url)
    print("Database created:")

# Flask app setup
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.register_blueprint(assignments_bp)

# Initialize Logging
# file_handler = FileHandler("/var/log/webapp/csye6225.log")
file_handler = FileHandler("test.log")
file_handler.setLevel(logging.INFO)


class UTCJsonFormatter(jsonlogger.JsonFormatter):
    converter = time.gmtime


formatter = UTCJsonFormatter(
    fmt="%(asctime)s %(levelname)s %(message)s",
    rename_fields={"asctime": "date_time", "levelname": "log_level"},
    datefmt="%a %b %d %H:%M:%S %Z %Y",
)

file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# Statsd Metrics
statsd = StatsClient("localhost", 8125)

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

    app.logger.info(f"Health check endpoint called with method: {request.method}")

    if request.method != "GET":
        app.logger.warning("Health check endpoint called with non-GET method")
        return Response(status=405, headers=headers)

    if request.data or request.form or request.args:
        app.logger.warning("Health check endpoint called with unexpected data")
        return Response(status=400, headers=headers)

    try:
        connection = psycopg2.connect(os.getenv("DATABASE_URL"))
        connection.close()
        app.logger.info("Database connection successful for health check")
        response = Response(status=200, headers=headers)

    except Exception as e:
        app.logger.error(f"Database connection failed for health check: {e}")
        response = Response(status=503, headers=headers)

    return response


# add required Headers
@app.after_request
def modify_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["content-type"] = "application/json"
    if response.status_code == 405:
        response.data = ""
        response.headers["Content-Length"] = "0"
    if request.endpoint and isinstance(request.endpoint, str):
        endpoint = request.endpoint.split(".")[-1]
        method = request.method.lower()
        metric_name = f"csye6225_endpoint_{endpoint}_http_{method}"
        statsd.incr(metric_name)
    return response


def create_tables():
    with app.app_context():
        db.create_all()


# CLI command to populate database from csv
@app.cli.command("populate_db")
def populate_db_command():
    csv_path = os.getenv("CSV_PATH", "/opt/users.csv")
    if not csv_path:
        app.logger.error("CSV_PATH environment variable not set!")
        return
    try:
        populate_db(csv_path, bcrypt)
        app.logger.info("Database populated successfully.")
    except Exception as e:
        app.logger.error(f"An error occurred while populating the database: {e}")


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
        app.logger.warning(
            "Authentication failed for user: {email}".format(email=email)
        )
        return False

    except SQLAlchemyError as e:
        app.logger.error(
            f"Database error occurred during authentication for user {email}: {e}"
        )
        return jsonify({"message": "Database error occurred."}), 503

    except Exception as e:
        app.logger.error(
            f"Unexpected error during authentication for user {email}: {e}"
        )
        return (
            jsonify({"message": "Unable to verify user."}),
            400,
        )
