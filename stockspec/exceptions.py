from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    if isinstance(response.data, list):
        data = dict(messages=response.data)
        response.data = data
    response.data["ok"] = False

    return response


class APIRateLimited(Exception):
    """Rate limited by AlphaVantage"""

    def __init__(self, symbol: str):
        super().__init__(f"{symbol}: api ratelimit")


class SerializerRequestMissing(Exception):
    """Raised when a serializer is missing request in context"""
