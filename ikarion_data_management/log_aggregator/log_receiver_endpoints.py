from flask import Blueprint
from ..data_access_layer.model_db_access_layer import user_model_dao
#from ..data_access_layer.model_db_access_layer import group_model_dao
from flask import request
from flask import Response
from ikarion_data_management.data_access_layer import modelDBConnection as con
from ikarion_data_management.log_aggregator.statement_processing import *

log_receiver_endpoints = Blueprint('log_receiver_endpoints', __name__)


@log_receiver_endpoints.route('/about')
def about():
    return 'Log receiver endpoints.'

# The LRS fowards resource access logs to this endpoint.
# Log forwarding has to be specified in learning locker first.
# (See https://ht2ltd.zendesk.com/hc/en-us/articles/115002026451--NEW-LL-Statement-Forwarding)
@log_receiver_endpoints.route('/resource_access')
def processResourceAccessLog():
    statement = request.get_json()
    relevant = statement_relevant(statement)
    if relevant:
        statement["timestamp"] = convert_timestamp(statement)
        restructure_extensions(statement)
        con.db.xapi_statements.insert_one(statement)
    return Response(status=200)






