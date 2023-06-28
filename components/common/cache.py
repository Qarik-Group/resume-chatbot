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
"""Utility functions used across multiple components.

Use: Annotate functions with cache capability as following:
    @cache
"""

import functools
import os
import time

from common import constants
from common.log import Logger

logger = Logger(__name__).get_logger()
logger.info('Initializing...')


def getenv_no_cache(key: str, default: str | None = None) -> str:
    """Get an environment variable without using the cache.

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
    result = os.getenv(key)
    if result is not None:
        logger.info('%s=%s', key, result)
        return result

    if default is not None:
        logger.info('%s=%s', key, default)
        return default

    raise ValueError(f'Environment variable "{key}" has not been defined')


CACHE_TIMEOUT = int(getenv_no_cache('CACHE_TIMEOUT', f'{constants.MINUTE * 1}'))
"""How long to cache results of call to the admin service for configuration state."""


def _ttl_cache(func, ttl_sec: int = CACHE_TIMEOUT, max_size: int = 2**14, typed: bool = True):
    """Cache decorator with time-based cache invalidation.

    Args:
        ttl_sec: Time to live for cached results (in seconds).
        max_size: Maximum cache size (see `functools.lru_cache`).
        typed: Cache on distinct input types (see `functools.lru_cache`).
    """

    @functools.lru_cache(maxsize=max_size, typed=typed)
    def _cached(*args, _salt, **kwargs):
        """Cache the execution of the 'func' based on the value of '_salt' relative to current time."""
        return func(*args, **kwargs)

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        """Invoke '_cached' function with the proper time salt."""
        return _cached(*args, **kwargs, _salt=int(time.time() / ttl_sec))

    return _wrapper


cache = functools.partial(_ttl_cache)
