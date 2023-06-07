# Copyright 2023 Qarik Group, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Custom FastAPI routers to manipulate request/response flow."""

import json
from typing import Any, Callable

import fastapi
from fastapi import HTTPException, Request, Response
from fastapi.routing import APIRoute
import solution
from log import Logger

logger = Logger(__name__).get_logger()


class DebugHeaders(APIRoute):
    """Print inbound request headers.

    Can be used by adding this to the handler class:
        app.router.route_class = JsonHeaders
    """

    def get_route_handler(self) -> Callable:
        """Insert new handler to manipulate headers."""
        original_route_handler = super().get_route_handler()

        async def print_headers(request: Request) -> Response:
            """Print inbound HTTP headers."""
            logger.debug('All headers=%s', request.headers)
            return await original_route_handler(request)

        return print_headers


class JsonHeaders(APIRoute):
    """Manipulate inbound request headers.

    This can be very useful when PubSub push notification sends data to the service without proper headers set.
    Can be used by adding this to the handler class:
        app.router.route_class = JsonHeaders
    """

    def get_route_handler(self) -> Callable:
        """Insert new handler to manipulate headers."""
        original_route_handler = super().get_route_handler()

        async def add_json_header(request: Request) -> Response:
            """Add content type JSON header to the request."""
            logger.debug('BEFORE: all headers=%s', request.headers)
            new_headers = request.headers.mutablecopy()
            new_headers['Content-Type'] = 'application/json'
            request._headers = new_headers
            # logger.debug('AFTER: all headers=%s', request.headers)
            return await original_route_handler(request)

        return add_json_header


class ErrorHandler(APIRoute):
    """Custom APIRoute that handles application errors and exceptions."""

    def get_route_handler(self) -> Callable:
        """Insert new handler to manipulate headers."""
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            """Add exception handler, so instead of "Internal Server Error" we show the real exception."""
            try:
                # if config_dao.is_read_only_project():
                #     status = solution.health_status()
                #     # Add additional warning message
                #     status['WARNING'] = str(
                #         'This project is read only and does not process or validate input data. '
                #         'This response is generic and is not using the output schema for the API you just called. '
                #         'You can see proper response schema in the OpenAPI spec for this service.')
                #     return Response(content=json.dumps(status))
                #     # raise RuntimeWarning(status)
                return await original_route_handler(request)
            except Exception as err:    # noqa
                if isinstance(err, HTTPException):
                    raise err
                if isinstance(err, ValueError):
                    raise HTTPException(
                        status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail=str(err))
                if isinstance(err, RuntimeError):
                    raise HTTPException(
                        status_code=fastapi.status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(err))

                raise HTTPException(
                    status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))

        return custom_route_handler


class ServiceAPI(fastapi.FastAPI):
    """Custom API class that adds some new behavior to the standard FastAPI."""

    def __init__(self,
                 title: str,
                 description: str,
                 openapi_tags: list[dict[str, Any]] | None = None) -> None:
        super().__init__(
            title=title,
            description=f'{description}  \n{solution.legaleze}',
            version=solution.SW_VERSION,
            docs_url=solution.docs_url,
            redoc_url=solution.redoc_url,
            terms_of_service=solution.terms_of_service,
            contact=solution.contact,
            license_info=solution.license_info)

        self.router.route_class = ErrorHandler
