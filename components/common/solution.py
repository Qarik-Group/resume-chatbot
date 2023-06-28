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
"""Project wide settings and constants."""

from common.cache import cache, getenv_no_cache


@cache
def getenv(key: str, default: str | None = None) -> str:
    """Get an environment variable using the cache.

    The optional second argument can specify an alternate default.
    If no default is specified and env variable does not exist, then raise an exception.

    Args:
        key - environment variable to lookup
        default (optional) - if env var was not defined, return this default val

    Return:
        string value of the environment variable

    Raise:
        Exception if variable does not exist AND the default is not provided
    """
    return getenv_no_cache(key=key, default=default)


#########################################################
# Project specific settings
#########################################################
SW_VERSION: str = getenv('SW_VERSION', '0.1.12')
"""Version of this project."""

SW_DATE: str = getenv('SW_DATE', 'June 27, 2023')
"""Release date of this project."""

RESOURCE_PREFIX: str = getenv('RESOURCE_PREFIX', 'skb')
"""Added to resource names so that in GCP Console it is easy to see what relates to this solution vs other resources."""

license_info = {
    'name': 'Apache 2.0',
    'url': 'https://www.apache.org/licenses/LICENSE-2.0.html',
}

contact = {
    'name': 'Qarik Group',
    'url': 'https://www.qarik.com',
    'email': 'rkharkovski@qarik.com',
}

terms_of_service = 'This is experimental software and no warranty of any kind is implied or expressed.'

docs_url = '/'
"""Location of the Swagger docs for REST endpoints for each service."""

redoc_url = '/about'
"""Location of the custom Swagger docs for REST endpoints for each service."""

legaleze = """Copyright 2023 Qarik Group, LLC LLC."""

JSON_CONTENT_HEADER: dict = {'Content-type': 'application/json'}


def health_status() -> dict:
    """Return status message with version number and release date for healthcheck for service endpoints."""
    return {
        'status': 'ok',
        'version': SW_VERSION,
        'releaseDate': SW_DATE,
    }
