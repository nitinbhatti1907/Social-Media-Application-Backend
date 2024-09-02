from rest_framework.response import Response

def create_response(data, code, message=None, extra={}):
    if not message:
        if code == 400:
            message = "Bad request"

        if code == 200:
            message = "Success"

    return Response(
        {"data": data, "message": message, "code": code, "extra": extra}, code
    )