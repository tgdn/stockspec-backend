import logging
from rest_framework.decorators import api_view

from rest_framework.response import Response
from rest_framework.request import Request

from am.users.serializers import UserSerializer


logger = logging.getLogger(__name__)


@api_view(["GET"])
def current_user(request: Request):
    user = {}
    if request.user.is_authenticated:
        user = UserSerializer(request.user).data
    return Response(user)
