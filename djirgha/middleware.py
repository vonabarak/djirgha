from uuid import uuid4


class BoardMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        cookie = request.COOKIES.get('board_id')

        response = self.get_response(request)
        if cookie is None:
            response.set_cookie('board_id', str(uuid4()))
        # Code to be executed for each request/response after
        # the view is called.

        return response
