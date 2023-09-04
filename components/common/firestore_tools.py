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
"""Set of utility functions to work with Firestore."""

import os

from common import solution
from common.log import Logger, log
from google.cloud import firestore  # type: ignore

logger = Logger(__name__).get_logger()


@log
def create_firestore_client():
    """Set up Firestore client."""
    if os.environ.get('FIRESTORE_EMULATOR_HOST'):
        from google.auth.credentials import AnonymousCredentials
        return firestore.Client(project=solution.PROJECT_ID, credentials=AnonymousCredentials())
    else:
        return firestore.Client()
