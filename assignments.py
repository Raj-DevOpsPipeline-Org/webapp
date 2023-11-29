from datetime import datetime
from uuid import UUID

from flask import Blueprint
from flask import current_app as app
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from extensions import auth
from models import Account, Assignment, AssignmentSubmission, db

# create Blueprint to modularize the code
assignments_bp = Blueprint("assignments", __name__)

version = "v1"


# use login_required decorator to verify authentication
@assignments_bp.route(f"/{version}/assignments", methods=["GET"])
@auth.login_required
def get_assignments():
    # do not accept any payload or query params
    if request.data or request.form or request.args:
        app.logger.warning("Bad request: unexpected data received in get_assignments")
        return jsonify({"message": "Bad Request"}), 400

    try:
        # all authenticated users can see assignments
        assignments = Assignment.query.all()
        app.logger.info(f"Retrieved {len(assignments)} assignments successfully.")
        return jsonify([assignment.to_dict() for assignment in assignments]), 200

    except SQLAlchemyError as e:
        app.logger.error(f"Database error occurred: {e}")
        return jsonify({"message": "Database error occurred."}), 503

    except Exception as e:
        app.logger.error(f"Unexpected error in get_assignments: {e}")
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
        if not (1 <= data.get("points", 0) <= 100):
            app.logger.warning("Assignment points out of range.")
            return (
                jsonify({"message": "Assignment points must be between 1 and 100."}),
                400,
            )

        if not (1 <= data.get("num_of_attempts", 0) <= 10):
            app.logger.warning("Number of attempts out of range.")
            return (
                jsonify({"message": "Number of attempts must be between 1 and 10."}),
                400,
            )

        # get the logged in user info
        user_email = auth.current_user().email
        user = Account.query.filter_by(email=user_email).first()

        if not user:
            app.logger.error(f"User not found for email: {user_email}")
            return jsonify({"message": "User not found."}), 403

        assignment = create_or_update_assignment(data, user)
        db.session.add(assignment)
        db.session.commit()
        app.logger.info(f"Assignment created successfully by user: {user_email}")

        return jsonify(assignment.to_dict()), 201

    except SQLAlchemyError as sqlerror:
        app.logger.error(
            f"Database error occurred while creating assignment: {sqlerror}"
        )
        return jsonify({"message": "Database error occurred."}), 503

    except Exception as e:
        app.logger.error(f"Unexpected error while creating assignment: {e}")
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
            app.logger.warning("Received unexpected data in get_assignment_detail")
            return jsonify({"message": "Bad Request"}), 400

        if not is_valid_uuid(assignment_id):
            app.logger.warning(
                "Received invalid assignment ID in get_assignment_detail"
            )
            return jsonify({"message": "Invalid assignment ID"}), 400

        # retrieve the assignment using assignment_id sent in the request
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            app.logger.warning("Assignment not found for ID: {}".format(assignment_id))
            return jsonify({"message": "Assignment not found"}), 404
        app.logger.info("Assignment detail retrieved for ID: {}".format(assignment_id))
        return jsonify(assignment.to_dict()), 200

    except SQLAlchemyError as e:
        app.logger.error(
            "Database error occurred in get_assignment_detail: {}".format(e)
        )
        return jsonify({"message": "Database error occurred."}), 503

    except Exception as e:
        app.logger.error("Unexpected error in get_assignment_detail: {}".format(e))
        return jsonify({"message": "Unable to fetch assignment."}), 400


@assignments_bp.route(f"/{version}/assignments/<assignment_id>", methods=["DELETE"])
@auth.login_required
def delete_assignment(assignment_id):
    try:
        if not is_valid_uuid(assignment_id):
            app.logger.warning(f"Invalid assignment ID received: {assignment_id}")
            return jsonify({"message": "Invalid assignment ID"}), 400

        # get the logged in user info
        user_email = auth.current_user().email
        user = Account.query.filter_by(email=user_email).first()

        if not user:
            app.logger.error(f"User not found for email: {user_email}")
            return jsonify({"message": "User not found."}), 403

        # retrieve the assignment using assignment_id sent in the request
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            app.logger.warning(f"Assignment not found for ID: {assignment_id}")
            return jsonify({"message": "Assignment not found"}), 404

        # check if the assignment owner and logged in user is same
        if assignment.account_id != user.id:
            app.logger.warning(
                f"User {user_email} attempted to delete an assignment without permission"
            )
            return jsonify({"message": "Permission denied"}), 403

        db.session.delete(assignment)
        db.session.commit()
        app.logger.info(
            f"Assignment {assignment_id} deleted successfully by user {user_email}"
        )

        return jsonify({"message": "Assignment deleted successfully"}), 204

    except SQLAlchemyError as e:
        app.logger.error(
            f"Database error occurred while deleting assignment {assignment_id}: {e}"
        )
        return jsonify({"message": "Database error occurred."}), 503

    except Exception as e:
        app.logger.error(
            f"Unexpected error while deleting assignment {assignment_id}: {e}"
        )
        return jsonify({"message": "Unable to delete the assignment."}), 400


@assignments_bp.route(f"/{version}/assignments/<assignment_id>", methods=["PUT"])
@auth.login_required
def update_assignment(assignment_id):
    try:
        data = request.get_json()

        # add code level checks before database constraints
        if not (1 <= data.get("points", 0) <= 100):
            app.logger.warning(
                f"Assignment points out of range for assignment {assignment_id}"
            )
            return (
                jsonify({"message": "Assignment points must be between 1 and 100."}),
                400,
            )

        if not (1 <= data.get("num_of_attempts", 0) <= 10):
            app.logger.warning(
                f"Number of attempts out of range for assignment {assignment_id}"
            )
            return (
                jsonify({"message": "Number of attempts must be between 1 and 10."}),
                400,
            )

        # get the logged in user info
        user_email = auth.current_user().email
        user = Account.query.filter_by(email=user_email).first()

        if not user:
            app.logger.error(
                f"User not found for email: {user_email} during assignment update"
            )
            return jsonify({"message": "User not found."}), 403

        # retrieve the assignment using assignment_id sent in the request
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            app.logger.warning(f"Assignment {assignment_id} not found for update")
            return jsonify({"message": "Assignment not found"}), 404

        # check if the assignment owner and logged in user is same
        if assignment.account_id != user.id:
            app.logger.warning(
                f"User {user_email} attempted to update an assignment without permission"
            )
            return jsonify({"message": "Permission denied"}), 403

        updated_assignment = create_or_update_assignment(data, user, assignment)
        db.session.commit()
        app.logger.info(
            f"Assignment {assignment_id} updated successfully by user {user_email}"
        )

        return jsonify(updated_assignment.to_dict()), 200

    except SQLAlchemyError as e:
        app.logger.error(
            f"Database error occurred while updating assignment {assignment_id}: {e}"
        )
        return jsonify({"message": "Database error occurred."}), 503

    except Exception as e:
        app.logger.error(
            f"Unexpected error while updating assignment {assignment_id}: {e}"
        )
        return (
            jsonify({"message": "Unable to update assignment."}),
            400,
        )

@assignments_bp.route(f"/{version}/assignments/<assignment_id>/submission", methods=["POST"])
@auth.login_required
def submit_assignment(assignment_id):
    try:
        data = request.get_json()
        submission_url = data.get("submission_url")
        
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            app.logger.warning(f"Assignment {assignment_id} not found")
            return jsonify({"message": "Assignment not found"}), 404
        
        # check the deadline
        if datetime.utcnow() > assignment.deadline:
            app.logger.warning(f"Assignment {assignment_id} submission deadline passed")
            return jsonify({"message": "Submission deadline has passed."}), 403

        # check number of attempts
        user_id = auth.current_user().id
        submission_count = AssignmentSubmission.query.filter_by(assignment_id=assignment_id, account_id=user_id).count()
        
        if submission_count >= assignment.num_of_attempts:
            app.logger.warning(f"Maximum number of attempts exceeded for Assignment {assignment_id}")
            return jsonify({"message": "Maximum number of attempts exceeded."}), 403
        
        # create a new submission
        new_submission = AssignmentSubmission(
        assignment_id=assignment.id,
        account_id=user_id,
        submission_url=submission_url
        )
        db.session.add(new_submission)
        db.session.commit()

        return jsonify(new_submission.to_dict()), 201

    except SQLAlchemyError as e:
        app.logger.error(
            f"Database error occurred while submitting for assignment {assignment_id}: {e}"
        )
        return jsonify({"message": "Database error occurred."}), 503

    except Exception as e:
        app.logger.error(
            f"Unexpected error while submitting the assignment {assignment_id}: {e}"
        )
        return jsonify({"message": "Unable to submit."}), 400

# To have original submission timstamp and modified updated tiemstamp

# @assignments_bp.route(
#     f"/{version}/assignments/<assignment_id>/submission", methods=["POST"]
# )
# @auth.login_required
# def submit_assignment(assignment_id):
#     try:
#         data = request.get_json()
#         submission_url = data.get("submission_url")

#         assignment = Assignment.query.get(assignment_id)
#         if not assignment:
#             app.logger.warning(f"Assignment {assignment_id} not found")
#             return jsonify({"message": "Assignment not found"}), 404
#         # check the deadline
#         if datetime.utcnow() > assignment.deadline:
#             app.logger.warning(f"Assignment {assignment_id} submission deadline passed")
#             return jsonify({"message": "Submission deadline has passed."}), 403

#         user_id = auth.current_user().id
#         existing_submission = AssignmentSubmission.query.filter_by(
#             assignment_id=assignment_id, account_id=user_id
#         ).first()

#         if existing_submission:
#             if existing_submission.attempts < assignment.num_of_attempts:
#                 existing_submission.submission_url = submission_url
#                 existing_submission.submission_updated = datetime.utcnow()
#                 existing_submission.attempts += 1
#                 db.session.commit()
#                 response_message = existing_submission.to_dict()
#                 status_code = 200
#             else:
#                 return jsonify({"message": "Maximum number of attempts exceeded."}), 403

#         else:
#             new_submission = AssignmentSubmission(
#                 assignment_id=assignment.id,
#                 account_id=user_id,
#                 submission_url=submission_url,
#             )
#             db.session.add(new_submission)
#             db.session.commit()
#             response_message = new_submission.to_dict()
#             status_code = 201

#         return jsonify(response_message), status_code

#     except SQLAlchemyError as e:
#         app.logger.error(
#             f"Database error occurred while submitting for assignment {assignment_id}: {e}"
#         )
#         return jsonify({"message": "Database error occurred."}), 503

#     except Exception as e:
#         app.logger.error(
#             f"Unexpected error while submitting the assignment {assignment_id}: {e}"
#         )
#         return jsonify({"message": "Unable to submit."}), 400
