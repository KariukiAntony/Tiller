import json


class TillerException(Exception):
    def __init__(self, message: str, *args: object, **kwargs: dict) -> None:
        super().__init__(*args)
        self.message = message

    def __str__(self) -> str:
        return self.message


def handle_404_error(error):
    response = error.get_response()
    response.data = json.dumps(
        {
            "status code": error.code,
            "name": error.name,
            "description": error.description,
        }
    )
    response.content_type = "application/json"
    return response


def handle_500_error(error):
    response = error.get_response()
    response.data = json.dumps(
        {
            "status code": error.code,
            "name": error.name,
            "description": error.description,
        }
    )
    response.content_type = "application/json"
    return response


def handle_403_error(error):
    response = error.get_response()
    response.data = json.dumps(
        {
            "status code": error.code,
            "name": error.name,
            "description": error.description,
        }
    )
    response.content_type = "application/json"
    return response


# error_bp = Blueprint("error_bp", __name__)
# @error_bp.errorhandler(404)
# def handle_404_exception(error):
#     response = error.get_response()
#     response.data = json.dumps({
#         "status code": error.code,
#         "name": error.name,
#         "description": error.description,
#     })
#     response.content_type = "application/json"
#     return response
