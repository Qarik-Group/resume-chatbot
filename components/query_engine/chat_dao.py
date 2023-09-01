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

from typing import Any

from common import firestore_tools, solution
from common.log import Logger, log
from google.cloud import firestore  # type: ignore
from pydantic import BaseModel, Field

logger = Logger(__name__).get_logger()


class VoteStatistic(BaseModel):
    """Input parameters for the vote endpoint."""
    name: str = Field(description='Name of the LLM backend', example='ChatGPT', min_length=1, max_length=100)
    up: int = Field(description='Number of upvotes for this LLM backend', example=11, ge=0)
    down: int = Field(description='Number of downvotes for this LLM backend', example=-22, le=0)


class BaseDao:
    """Generic object that handles database persistence."""

    def __init__(self, collection_name: str) -> None:
        """Initialize the DAO with proper resources."""
        self._db = firestore_tools.create_firestore_client()
        self._collection = self._db.collection(collection_name)


class VoteDao(BaseDao):
    """Handle database persistence for votes on LLM answers. The collection structure is as following:

    votes
    ├── llm: string
    │   ├── up: int
    │   ├── down: int
    │   └── submissions: list of questions and answers submitted by users
    │       ├── question: string
    │       ├── answer: string
    │       ├── upvoted: bool
    │       └── timestamp: timestamp
    └── llm_2
        ...
    """

    def __init__(self) -> None:
        """Initialize the DAO with proper resources."""
        super().__init__(f'{solution.RESOURCE_PREFIX}_votes')
        """Firestore collection that keeps track of users known to the system."""

    @log
    def _get_doc_ref_by_llm(self, llm: str) -> firestore.DocumentReference | None:
        """Find device Firestore Doc Ref by its ID. Return None if does not exist."""
        doc_ref = self._collection.document(llm)
        return doc_ref if doc_ref.get().exists else None

    @log
    def create(self, llm: str) -> Any:
        """Create new vote document and return DocRef."""
        doc_ref = self._collection.document(llm)
        doc_ref.set({'llm': llm, 'up': 0, 'down': 0})
        return doc_ref

    @log
    def submit_vote(self, llm: str, question: str, answer: str, upvoted: bool) -> Any:
        """Submit new vote."""
        doc_ref = self._get_doc_ref_by_llm(llm)
        if doc_ref is None:
            doc_ref = self.create(llm)
        submission: dict[str, Any] = {
            'answer': answer,
            'question': question,
            'timestamp': solution.now(),
            'upvoted': upvoted
        }
        up: int = 1 if upvoted else 0
        down: int = 0 if upvoted else -1
        data = {'submissions': firestore.ArrayUnion([submission]),
                'up': firestore.Increment(up),
                'down': firestore.Increment(down),
                }
        return doc_ref.set(data, merge=True)

    @log
    # Return vote counts for each llm
    def get_llm_totals(self) -> list[VoteStatistic]:
        """Return list of all votes in the database."""
        votes: list[VoteStatistic] = []
        for doc in self._collection.stream():
            vote: dict[str, Any] = doc.to_dict()
            votes.append(VoteStatistic(name=vote['llm'], up=vote['up'], down=vote['down']))
        return votes


class UserDao(BaseDao):
    """Handle database persistence for users and their query history. The collection structure is as following:

    users
    ├── user_id_1 (email)
    │   ├── first_login: timestamp
    │   ├── user_id: string (yes, it duplicates the document ID)
    │   └── interactions: list of interactions
    │       ├── question: string
    │       ├── answer: string
    │       ├── llm: string
    │       └── timestamp: timestamp
    └── user_id_2
        ...
    """

    def __init__(self) -> None:
        """Initialize the DAO with proper resources."""
        super().__init__(f'{solution.RESOURCE_PREFIX}_users')
        """Firestore collection that keeps track of users known to the system."""

    def _get_doc_ref_by_id(self, user_id: str) -> firestore.DocumentReference | None:
        """Find device Firestore Doc Ref by its ID. Return None if does not exist."""
        doc_ref = self._collection.document(user_id)
        return doc_ref if doc_ref.get().exists else None

    @log
    def create(self, user_id: str) -> Any:
        """Create new user document and return DocRef."""
        doc_ref = self._collection.document(user_id)
        doc_ref.set({'user_id': user_id, 'first_login': solution.now()})
        return doc_ref

    def get_by_id(self, user_id: str) -> Any:
        """Find user by its ID."""
        doc_ref = self._get_doc_ref_by_id(user_id)
        return doc_ref.get().to_dict() if doc_ref is not None else None

    def exists(self, user_id: str) -> bool:
        """Check for existence of the user by its ID."""
        doc_ref = self._get_doc_ref_by_id(user_id)
        return bool(doc_ref)

    def save_question_answer(self, user_id: str, question: Any, answer: Any, llm_backend: str) -> Any:
        """Update user document."""
        doc_ref = self._get_doc_ref_by_id(user_id)
        if doc_ref is None:
            doc_ref = self.create(user_id)
        interaction: dict[str, Any] = {
            'answer': answer,
            'llm': llm_backend,
            'question': question,
            'timestamp': solution.now()
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
