from .. import modelDBConnection as con

import datetime


# onstraints parameter for the functions is used to keep query context flexible
# and add constraints at a later time without rewriting all the functions every time
# constraints are dictionaries/maps as used in mongodb query. They all get merged to create a query

context_extension_id = "http://lrs.learninglocker.net/define/extensions/moodle_logstore_standard_log"

# Fields
RES_USED_LIST = 'resources_list'
RES_USED_FIELD = 'resource_accesses'
DISTINCT_RES_USED = 'distinct_resource_accesses'


# TODO Write Tests because this won't work from the start :)

course_schema = "context.extensions.courseid"
group_schema = ""
artefact_schema = "artefact.id"
artefact_type_schema = "artefact.definition.type"
user_schema = "actor.name"
time_stamp_schema = "timestamp"
action_schema = "verb.id"
verb_schema = "verb.id"
# Retrieve


def course_query(course):
    if course is None:
        return {}
    else:
        query = {
            course_schema: course
        }
        return query


def group_query(group):
    if group is None:
        return {}
    else:
        query = {
            group_schema: group
        }
        return query


def user_query(user):
    query = {
        user_schema: user
    }
    return query


def verb_query(verb):
    query = {
        verb_schema: verb
    }
    return query


def artefact_query(artefact):
    query = {
        artefact_schema: artefact
    }
    return query


def artefact_type_query(artefact_type):
    query = {
        artefact_type_schema: artefact_type
    }
    return query


def get_all_user_statements(user, *constraints):
    query = merge_query(user_query(user), *constraints)
    result = con.db.xapi_statements.find(query)
    return list(result)


def get_all_user_times(user, course, *constraints):
    query = merge_query(user_query(user), course_query(course), *constraints)
    result = con.db.xapi_statements.find(query, {time_stamp_schema: 1})
    result = list(set([item[time_stamp_schema] for item in result]))
    result.sort()
    return result


def get_all_courses():
    return list(con.db.xapi_statements.distinct(course_schema))


def get_all_users():
    return list(con.db.xapi_statements.distinct(user_schema))


def get_all_users_for_course(course, *constraints):

    result = list(con.db.xapi_statements.distinct(user_schema, course_query(course), *constraints))
    return result


def get_all_courses_for_user(user):
    result = list(con.db.xapi_statements.distinct(course_schema, user_query(user)))
    return result


def get_user_active_days(user, course, *constraints):
    epoch_times = get_all_user_times(user, course, *constraints)
    datetimes = [datetime.datetime.utcfromtimestamp(item) for item in epoch_times]
    dates = [item.date() for item in datetimes]
    distinct_dates = set(dates)
    sorted_date_list = sorted(list(distinct_dates))
    sorted_date_list = [date.isoformat() for date in sorted_date_list]
    return sorted_date_list


def get_user_artefact_actions(user, artefact, *constraints):
    query = merge_query(user_query(user), artefact_query(artefact), *constraints)
    result = list(con.db.xapi_statements.find(query))
    return result


def get_user_verbs(user, course, *constraints):
    query = merge_query(user_query(user), course_query(course), *constraints)
    return list(con.db.xapi_statements.distinct(verb_schema, query))


def get_user_artefact_types(user, course, *constraints):
    query = merge_query(user_query(user), course_query(course), *constraints)
    return list(con.db.xapi_statements.distinct(artefact_type_schema, query))


def get_user_verbs_for_artefact_type(user, artefact_type, course, *constraints):
    query = merge_query(user_query(user),
                        artefact_type_query(artefact_type),
                        course_query(course),
                        *constraints)
    return list(con.db.xapi_statements.distinct(verb_schema, query))


def get_user_artefact_action_stats(user, artefact, verb):

    query = merge_query(user_query(user), artefact_query(artefact), verb_query(verb))
    result = list(con.db.xapi_statements.find(query))
    return {"count": len(result)}


def get_user_artefact_type_action_stats(user, artefact_type, verb, course, *constraints):
    query = merge_query(user_query(user),
                        artefact_type_query(artefact_type),
                        verb_query(verb),
                        course_query(course),
                        *constraints)
    artefact_list = list(con.db.xapi_statements.distinct(artefact_schema, query))
    result = []
    for artefact in artefact_list:
        stats = get_user_artefact_action_stats(user, artefact, verb)
        data = {
            "id": artefact,
            **stats,
        }
        result.append(data)
    return result


def get_user_average_latency(user, course, *constraints):

    times = get_all_user_times(user, course, *constraints)

    latencies = []
    for first, second in zip(times[:-1], times[1:]):
        latencies.append(second-first)

    avg_latency = sum(latencies)/len(latencies)
    return avg_latency


def get_user_model_for_course(user, course, *constraints):
    # TODO Update Usermodel on Site
    course_constraint = course_query(course)
    artefact_types = get_user_artefact_types(user, course, *constraints)
    artefacts = []
    for artefact_type in artefact_types:
        artefact_type_stats = []
        verbs = get_user_verbs_for_artefact_type(user, artefact_type, course, *constraints)
        for verb in verbs:
            verb_stats = get_user_artefact_type_action_stats(user, artefact_type, verb, course, *constraints)
            artefact_type_stats.append({verb: verb_stats})

        artefacts.append({artefact_type: artefact_type_stats})

    user_model = {
        "uid": user,
        "course_id": course,
        "updated_at": get_user_last_updated_at(user, course, *constraints),
        "active_days": get_user_active_days(user, course, *constraints),
        "artifacts": artefacts,
    }
    return user_model


def get_user_last_updated_at(user, course, *constraints):
    return get_all_user_times(user, course, *constraints)[-1]


def merge_query(*args):
    merged_query = {

    }
    for arg in args:
        merged_query.update(arg)

    return merged_query

# Exception classes
class NoSuchUserException(Exception):
    def __init__(self, user, course):
        self.message = "No such user {} in course {}".format(user, course)


class NoSuchCourseException(Exception):
    def __init__(self, course):
        self.message = "No such course {}".format(course)
