from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from pyramid.view import view_config
from pyramid.response import Response

import logging
import json
import logging_config.config as logging_config
from users.models.user import User

users_global_dict = {}
logger = logging.getLogger()


@view_config(route_name="save_user", renderer="json")
def save_user(request):
    logger.info("Started create_user")
    request_body = request.body
    try:
        user_dict = json.loads(request_body.decode("utf-8"))
    except json.JSONDecodeError:
        msg = "Failed to decode the payload"
        logger.exception(msg)
        return Response(body=msg, status=400)
    try:
        user = User(**user_dict)
    except TypeError:
        msg = "Required fields are missing in received object"
        logger.exception(msg)
        return Response(body=msg, status=400)
    if not user.id:
        msg = "The value of id is empty"
        logger.error(msg)
        return Response(body=msg, status=400)
    if not isinstance(user.id, int):
        msg = "The value of id is not int"
        logger.error(msg)
        return Response(body=msg, status=400)
    users_global_dict[user.id] = user
    logger.info("Completed create_user")
    return Response(
        json_body=vars(user),
        status=201
    )


@view_config(route_name="get_users", renderer="json")
def get_users(request):
    res = []
    if users_global_dict:
        for user in users_global_dict.values():
            res.append(vars(user))
    return res


@view_config(route_name="get_user_by_id", renderer="json")
def get_user_by_id(request):
    logger.info("Started get_user_by_id")
    ok, msg = validate_user_id(request)
    if not ok:
        return Response(body=msg, status=400)
    logger.info("Completed get_user_by_id")
    return vars(users_global_dict[int(request.matchdict['id'])])


@view_config(route_name="update_user", renderer="json")
def update_user(request):
    logger.info("Started update_user")
    request_body = request.body
    try:
        user_dict = json.loads(request_body.decode("utf-8"))
    except json.JSONDecodeError:
        msg = "Failed to decode the payload"
        logger.exception(msg)
        return Response(body=msg, status=400)
    user = User(**user_dict)
    ok, msg = validate_user_id(request, user)
    if not ok:
        return Response(body=msg, status=400)
    users_global_dict[user.id] = user
    logger.info("Completed update_user")
    return Response(
        json_body=vars(user),
        status=201
    )


@view_config(route_name="delete_user_by_id", renderer="json")
def delete_user_by_id(request):
    logger.info("Started delete_user_by_id")
    ok, msg = validate_user_id(request)
    if not ok:
        return Response(body=msg, status=400)
    users_global_dict.pop(int(request.matchdict['id']))
    logger.info("Completed delete_user_by_id")
    return Response(status=204)


def validate_user_id(request, user_param=None):
    msg = None
    user_id_str = ""
    try:
        user_id_str = request.matchdict['id']
        user_id = int(user_id_str)
    except ValueError:
        msg = "id: " + user_id_str + " not a valid integer"
    if msg is None:
        if user_id not in users_global_dict:
            msg = "User with id: " + str(user_id) + " not found"
        else:
            user = users_global_dict[user_id]
            if user_param is not None and user.id != user_param.id:
                msg = "id: " + str(user_id) + " in path variable doesn't match id: " \
                      + str(user_param.id) + " in received object"
    if msg is not None:
        logger.error(msg)
        return False, msg
    return True, None


def make_wsgi_app():
    configurator = Configurator()
    configurator.add_route("save_user", "/users", request_method="POST")
    configurator.add_route("get_users", "/users", request_method="GET")
    configurator.add_route("get_user_by_id", "/users/{id}", request_method="GET")
    configurator.add_route("update_user", "/users/{id}", request_method="PUT")
    configurator.add_route("delete_user_by_id", "/users/{id}", request_method="DELETE")
    configurator.scan()
    return configurator.make_wsgi_app()


if __name__ == "__main__":
    logging_config.init()
    app = make_wsgi_app()
    server = make_server("127.0.0.1", 9090, app)
    server.serve_forever()
