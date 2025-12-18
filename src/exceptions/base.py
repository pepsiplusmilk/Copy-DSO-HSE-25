from typing import Optional, Type


class ApiException(Exception):
    status_code = 400
    code = "unidentified_api_exception"
    message = "Something went wrong"

    def __init__(self, message: Optional[str] = None):
        if message:
            self.message = message


class NotFoundException(ApiException):
    status_code = 404
    object_name = "Object"
    code = f"{object_name.lower()}_not_found"
    message = f"{object_name} Not Found"

    def __init__(self, obj_type: Optional[Type] = None):
        if obj_type:
            self.object_type = obj_type
