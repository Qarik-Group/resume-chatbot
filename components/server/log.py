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
"""The logging shared module. Used for setting up proper logging levels for various services.

Typical usage:
    Import into another module, set it up, then use the logger:

        from common.log import IPELogger, log
        logger = IPELogger(__name__).get_logger()

        @log
        def function_x():
            logger.debug('Blah blah %s, %s, %s', x, y, z)

"""
import os
import sys
import functools
import logging

_LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')


def setup_logger(log_format: str = '%(message)s', log_name: str = 'undefined_log_name') -> logging.Logger:
    """Initialize logging settings for the caller and return `logger` that can be used as `logger.info('message')`."""
    logger = logging.getLogger(log_name)
    logger.setLevel(_LOG_LEVEL)
    logger.propagate = False
    # See log levels, formatting, etc. in the docs: https://docs.python.org/3/library/logging.html
    formatter = logging.Formatter(log_format)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(_LOG_LEVEL)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
    return logger


class Logger:
    """Logger class for using inside of method body, such as `log.debug()`."""

    def __init__(self, log_name: str = 'my_log') -> None:
        log_format = '%(levelname)s:%(filename)s:%(funcName)s(%(lineno)d): %(message)s'
        log_name_f = f'{log_name}_f'
        self.function_body_logger = setup_logger(log_format, log_name_f)

    def get_logger(self) -> logging.Logger:
        """Return the logger that is used inside of the function code (not annotated method)."""
        return self.function_body_logger


_DECORATOR_LOGGER = setup_logger('%(levelname)s: %(message)s', __name__)


def _log(func, log_params: bool):
    """Log entry and exit from functions.

    Args:
        log_params: True if you want to print log input and output to the annotated function.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        def get_signature():
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f'{k}={v!r}' for k, v in kwargs.items()]
            return ', '.join(args_repr + kwargs_repr)

        fname = '.'.join([func.__module__, func.__qualname__])
        if log_params:
            _DECORATOR_LOGGER.debug('in--> %s -> %s', fname, get_signature())
        else:
            _DECORATOR_LOGGER.debug('in--> %s ->', fname)
        try:
            result = func(*args, **kwargs)
            if log_params:
                _DECORATOR_LOGGER.debug('<-out %s <- %s', fname, result)
            else:
                _DECORATOR_LOGGER.debug('<-out %s <-', fname)
            return result
        except Exception as err:    # noqa: B902
            _DECORATOR_LOGGER.exception('Function %s(%s) threw exception: %s', fname, get_signature(), err)
            raise err

    return wrapper


log = functools.partial(_log, log_params=False)
log_params = functools.partial(_log, log_params=True)
