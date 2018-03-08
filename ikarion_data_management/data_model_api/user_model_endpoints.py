from flask import Blueprint, jsonify
from ..data_access_layer.model_db_access_layer import user_model_dao

user_model_endpoints = Blueprint('user_model_endpoints', __name__)


@user_model_endpoints.route('/about')
def about():
    return 'User model endpoints.'


# User models
@user_model_endpoints.route("/models/<course>/<user>")
def getUserModel(course, user):

    return jsonify(model=user_model_dao.getUserModel(course, user))


@user_model_endpoints.route("/models/<course>")
def getAllUserModels(course):

    return jsonify(model=user_model_dao.getUserModelsForCourse(course))


# List of users
@user_model_endpoints.route("/")
def getAllUsers():

    return jsonify(result=user_model_dao.get_all_users())


@user_model_endpoints.route("/<course>")
def getAllUsersForCourse(course):
    return jsonify(users=user_model_dao.get_all_users_for_course(course))


# List of courses
@user_model_endpoints.route("/courses")
def getAllCourses():

    return jsonify(result=user_model_dao.get_all_courses())


@user_model_endpoints.route("/courses/<user>")
def getAllCoursesForUser(user):

    return jsonify(courses=user_model_dao.get_all_courses_for_user(user))