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

from datetime import datetime
from typing import Any
from common import firestore_tools, solution
from common.log import Logger, log_params

logger = Logger(__name__).get_logger()

CURRENT_CONFIG = 'current_config'


class AdminDAO:
    """Handles database persistence or configuration data."""

    def __init__(self):
        """Initialize backend."""
        self._db = firestore_tools.create_firestore_client()
        self._collection = self._db.collection(f'{solution.RESOURCE_PREFIX}_config')
        """Firestore collection that keeps track of admin and configuration data."""
        super().__init__()

    @log_params
    def touch_resumes(self, timestamp: datetime | None) -> datetime:
        """Save config with the most recent timestamp when resumes were last updated in the system."""
        if timestamp is None:
            timestamp = solution.now()
        doc_ref = self._collection.document(CURRENT_CONFIG)
        doc_ref.set({'last_resume_update': timestamp, 'info': 'Updated resume refresh timestamp.'}, merge=True)
        return timestamp

    @log_params
    def get_resumes_timestamp(self) -> datetime | None:
        """Get most recent timestamp when resumes were updated."""
        doc_ref = self._collection.document(CURRENT_CONFIG)
        if not doc_ref.get().exists:
            return None
        return doc_ref.get().to_dict()['last_resume_update']

    @log_params
    def erase_resumes_timestamp(self) -> None:
        """Erase the value of the most recent timestamp when resumes were updated."""
        doc_ref = self._collection.document(CURRENT_CONFIG)
        if not doc_ref.get().exists:
            return

        data: dict[str, Any] = {'last_resume_update': None, 'info': 'Erased resume refresh timestamp.'}
        doc_ref.set(data, merge=True)
