from uuid import UUID

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from extensions import auth
from models import Account, Assignment, db

# create Blueprint to modularize the code
assignments_bp = Blueprint("assignments", __name__)

version = "v1"


# use login_required decorator to verify authentication
@assignments_bp.route(f"/{version}/assignments", methods=["GET"])
@auth.login_required
def get_assignments():
    # do not accept any payload or query params
    if request.data or request.form or request.args:
        return jsonify({"message": "Bad Request"}), 400

    try:
        # all authenticated users can see assignments
        assignments = Assignment.query.all()
        return jsonify([assignment.to_dict() for assignment in assignments]), 200

    except SQLAlchemyError:
        return jsonify({"message": "Database error occurred."}), 503

    except Exception as e:
        return (
            jsonify({"message": "Unable to fetch assignments."}),
            400,
        )


def create_or_update_assignment(data, user, assignment=None):
    if not assignment:
        assignment = Assignment()

    assignment.name = data["name"]
    assignment.points = data["points"]
    assignment.num_of_attempts = data["num_of_attempts"]
    assignment.deadline = data["deadline"]
    assignment.account_id = user.id

    return assignment


@assignments_bp.route(f"/{version}/assignments", methods=["POST"])
@auth.login_required
def create_assignment():
    try:
        data = request.get_json()

        # add code level checks before database constraints
        if not (1 <= data["points"] <= 100):
            return (
                jsonify({"message": "Assignment points must be between 1 and 100."}),
                400,
            )

        if not (1 <= data["num_of_attempts"] <= 10):
            return (
                jsonify({"message": "Number of attempts must be between 1 and 10."}),
                400,
            )

        # get the logged in user info
        user_email = auth.current_user().email
        user = Account.query.filter_by(email=user_email).first()

        if not user:
            return jsonify({"message": "User not found."}), 403

        assignment = create_or_update_assignment(data, user)
        db.session.add(assignment)
        db.session.commit()

        return jsonify(assignment.to_dict()), 201

    except SQLAlchemyError as sqlerror:
        print(sqlerror)
        return jsonify({"message": "Database error occurred."}), 503

    except Exception as e:
        return (
            jsonify({"message": "Unable to create assignment."}),
            400,
        )


# check if the id is UUID
def is_valid_uuid(val):
    try:
        UUID(str(val))
        return True
    except ValueError:
        return False


@assignments_bp.route(f"/{version}/assignments/<assignment_id>", methods=["GET"])
@auth.login_required
def get_assignment_detail(assignment_id):
    try:
        # do not accept any payload or query params
        if request.data or request.form or request.args:
            return jsonify({"message": "Bad Request"}), 400

        if not is_valid_uuid(assignment_id):
            return jsonify({"message": "Invalid assignment ID"}), 400

        # retrieve the assignment using assignment_id sent in the request
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            return jsonify({"message": "Assignment not found"}), 404
        return jsonify(assignment.to_dict()), 200

    except SQLAlchemyError:
        return jsonify({"message": "Database error occurred."}), 503

    except Exception as e:
        return (
            jsonify({"message": "Unable to fetch assignment."}),
            400,
        )


@assignments_bp.route(f"/{version}/assignments/<assignment_id>", methods=["DELETE"])
@auth.login_required
def delete_assignment(assignment_id):
    try:
        if not is_valid_uuid(assignment_id):
            return jsonify({"message": "Invalid assignment ID"}), 400

        # get the logged in user info
        user_email = auth.current_user().email
        user = Account.query.filter_by(email=user_email).first()

        if not user:
            return jsonify({"message": "User not found."}), 403

        # retrieve the assignment using assignment_id sent in the request
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            return jsonify({"message": "Assignment not found"}), 404

        # check if the assignment owner and logged in user is same
        if assignment.account_id != user.id:
            return jsonify({"message": "Permission denied"}), 403

        db.session.delete(assignment)
        db.session.commit()
        return jsonify({"message": "Assignment deleted successfully"}), 204

    except SQLAlchemyError:
        return jsonify({"message": "Database error occurred."}), 503

    except Exception as e:
        return (
            jsonify({"message": "Unable to delete the assignment."}),
            400,
        )


@assignments_bp.route(f"/{version}/assignments/<assignment_id>", methods=["PUT"])
@auth.login_required
def update_assignment(assignment_id):
    try:
        data = request.get_json()

        # add code level checks before database constraints
        if not (1 <= data["points"] <= 100):
            return (
                jsonify({"message": "Assignment points must be between 1 and 100."}),
                400,
            )

        if not (1 <= data["num_of_attempts"] <= 10):
            return (
                jsonify({"message": "Number of attempts must be between 1 and 10."}),
                400,
            )

        # get the logged in user info
        user_email = auth.current_user().email
        user = Account.query.filter_by(email=user_email).first()

        if not user:
            return jsonify({"message": "User not found."}), 403

        # retrieve the assignment using assignment_id sent in the request
        assignment = Assignment.query.get(assignment_id)

        if not assignment:
            return jsonify({"message": "Assignment not found"}), 404

        # check if the assignment owner and logged in user is same
        if assignment.account_id != user.id:
            return jsonify({"message": "Permission denied"}), 403

        updated_assignment = create_or_update_assignment(data, user, assignment)
        db.session.commit()

        return jsonify(updated_assignment.to_dict()), 200

    except SQLAlchemyError:
        return jsonify({"message": "Database error occurred."}), 503

    except Exception as e:
        return (
            jsonify({"message": "Unable to update assignment."}),
            400,
        )
