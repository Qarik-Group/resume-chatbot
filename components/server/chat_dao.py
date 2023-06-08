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
"""Data Access Object to abstract access to the database from the rest of the app."""

from datetime import datetime
from typing import Any
import firestore_tools
from google.cloud import firestore    # type: ignore
import solution
from log import Logger, log

logger = Logger(__name__).get_logger()


class ChatDao:
    """Device object that handles database persistence."""

    def __init__(self) -> None:
        self._db = firestore_tools.create_firestore_client()
        self._collection = self._db.collection(f'{solution.RESOURCE_PREFIX}_users')
        """Firestore collection that keeps track of users known to the system."""

    @log
    def _get_doc_ref_by_id(self, user_id: str) -> firestore.DocumentReference | None:
        """Find device Firestore Doc Ref by its ID. Return None if does not exist."""
        doc_ref = self._collection.document(user_id)
        return doc_ref if doc_ref.get().exists else None

    @log
    def create(self, user_id: str) -> Any:
        """Create new user document and return DocRef."""
        doc_ref = self._collection.document(user_id)
        doc_ref.set({'user_id': user_id, 'first_login': datetime.now(tz=solution.TIMEZONE)})
        return doc_ref

    @log
    def get_by_id(self, user_id: str) -> Any:
        """Find user by its ID."""
        doc_ref = self._get_doc_ref_by_id(user_id)
        return doc_ref.get().to_dict() if doc_ref is not None else None

    @log
    def exists(self, user_id: str) -> bool:
        """Check for existence of the user by its ID."""
        doc_ref = self._get_doc_ref_by_id(user_id)
        return bool(doc_ref)

    @log
    def save_question_answer(self, user_id: str, question: Any, answer: Any) -> Any:
        """Update user document."""
        doc_ref = self._get_doc_ref_by_id(user_id)
        if doc_ref is None:
            doc_ref = self.create(user_id)
        interaction: dict[str, Any] = {
            'question': question,
            'answer': answer,
            'timestamp': datetime.now(tz=solution.TIMEZONE)
        }
        # Append new interaction to the list of existing interactions in the user document
        data = {'interactions': firestore.ArrayUnion([interaction])}
        return doc_ref.set(data, merge=True)

    @log
    def delete(self, user_id: str) -> Any:
        """Delete user document."""
        doc_ref = self._collection.document(user_id)
        if not doc_ref.get().exists:
            return None
        return doc_ref.delete()

    @log
    def get_all_users(self) -> list[dict[str, Any]]:
        """Return list of all users in the database."""
        users: list[dict[str, Any]] = []
        for doc in self._collection.stream():
            users.append(doc.to_dict())
        logger.debug('Found %s users in the database', len(users))
        return users
