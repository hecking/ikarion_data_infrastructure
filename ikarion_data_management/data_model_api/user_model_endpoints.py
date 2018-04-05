from flask import Blueprint, jsonify, request
from ..data_access_layer.model_db_access_layer import user_model_dao as umd

user_model_endpoints = Blueprint('user_model_endpoints', __name__)


@user_model_endpoints.route('/about')
def about():
    return 'User model endpoints.'


# User models
@user_model_endpoints.route("/model/<course>/<user>")
def get_user_model(course, user):
    return jsonify(model=umd.get_user_model_for_course(user, course))


@user_model_endpoints.route("/models/<course>")
def get_all_user_models(course):
    users = umd.get_all_users_for_course(course)
    user_models = [umd.get_user_model_for_course(user, course) for user in users]
    return jsonify(models=user_models)


# List of users
@user_model_endpoints.route("/")
def get_all_users():
    return jsonify(users=umd.get_all_users())


@user_model_endpoints.route("/<course>")
def get_all_users_for_course(course):
    return jsonify(users=umd.get_all_users_for_course(course))


# List of courses
@user_model_endpoints.route("/courses")
def get_all_courses():
    return jsonify(courses=umd.get_all_courses())


@user_model_endpoints.route("/times/<user>/<course>")
def get_all_user_times(user, course):
    return jsonify(courses=umd.get_all_user_times(user, course))

@user_model_endpoints.route("/active_days/<user>/<course>")
def get_user_active_days(user, course):
    return jsonify(umd.get_user_active_days(user, course))

@user_model_endpoints.route("/avg_latency/<user>/<course>")
def get_avg_latency(user, course):
    if request.is_json:
        constraints = request.get_json()
    else:
        constraints = []
    latency = umd.get_user_average_latency(user, course, *constraints)
    return jsonify({"avg_latency": latency})

@user_model_endpoints.route("/courses/<user>")
def get_all_courses_for_user(user):

    return jsonify(courses=umd.get_all_courses_for_user(user))

