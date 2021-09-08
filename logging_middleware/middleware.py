"""Logging middleware"""

import logging
from django.utils import timezone
from ipware import get_client_ip


class LoggingMiddleware:
    """Middleware that logs all requests/responses"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.log = logging.getLogger('log-http-requests')
        self.log.info("Logging middleware inititalized")

    def __call__(self, request):
        # Pre-request
        started_at = timezone.now()
        client_ip, _ = get_client_ip(request)

        response = self.get_response(request)

        # Post-request
        finished_at = timezone.now()

        took = finished_at - started_at

        extra = {
            'remote-host': client_ip,
            'request-time': took.total_seconds(),
            'path': request.path,
            'method': request.method,
        }

        if hasattr(request, 'user'):
            extra['user'] = str(request.user)

        if response.streaming:
            extra['streaming'] = True
        else:
            extra['response-size'] = len(response.content)

        self.log.info("Finished request to %s", request.path, extra=extra)
        return response
