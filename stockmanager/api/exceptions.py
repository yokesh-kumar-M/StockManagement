import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        logger.error(
            "Unhandled exception in %s: %s",
            context.get("view", "unknown"),
            exc,
            exc_info=True,
        )
        return Response(
            {"error": "An unexpected error occurred. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Normalise detail → error for consistent API responses
    if isinstance(response.data, dict):
        if "detail" in response.data:
            response.data["error"] = str(response.data.pop("detail"))
        response.data["status_code"] = response.status_code

    return response
