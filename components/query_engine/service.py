# Copyright 2023 Qarik Group, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License');
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
"""Main API service that handles REST API calls to LLM and is run on server."""

from typing import Annotated
from datetime import datetime
from fastapi import Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chat_dao
from common import api_tools, chatgpt_tools, googleai_tools, solution, gcs_tools, admin_dao
from common.cache import cache
from common.log import Logger, log_params, log

logger = Logger(__name__).get_logger()
logger.info('Initializing...')

INDEX_BUCKET: str = solution.getenv('EMBEDDINGS_BUCKET_NAME')
INDEX_DIR: str = 'tmp/embeddings'
LAST_LOCAL_INDEX_UPDATE: datetime | None = None

app = api_tools.ServiceAPI(title='Resume Chatbot API (experimental)',
                           description='Request / response API for the Resume Chatbot that uses LLM for queries.')

# In case you need to print the log of all inbound HTTP headers
# app.router.route_class = api_tools.DebugHeaders

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

_db = chat_dao.ChatDao()
"""Data Access Object to abstract access to the database from the rest of the app."""


class AskInput(BaseModel):
    question: str


@app.post('/ask_gpt')
@log_params
def ask_gpt(data: AskInput, x_goog_authenticated_user_email: Annotated[str | None, Header()] = None) -> dict[str, str]:
    """Ask a question to the GPT-3 model and return the answer."""
    question = data.question

    # TODO: investigate if this may be cached or shared across requests
    refresh_index()
    logger.debug('Initializing query engine...')
    query_engine = chatgpt_tools.get_resume_query_engine(index_dir=INDEX_DIR)
    if query_engine is None:
        raise SystemError('No resumes found in the database. Please upload resumes.')

    user_id: str = 'anonymous'
    if x_goog_authenticated_user_email is None:
        logger.warning('No authenticated user email found in the request headers.')
    else:
        # Header passed from IAP
        # Extract part of the x_goog_authenticated_user_email string after the ':'
        # Example: accounts.google.com:rkharkovski@qarik.com -> rkharkovski@qarik.com
        user_id = x_goog_authenticated_user_email.split(':')[-1]
    logger.debug('Received question from user: %s', user_id)

    try:
        logger.debug('Querying LLM...')
        answer = query_engine.query(question)
        # TODO - experiment with different prompt tunings
        # response = query_engine.query(query_text + constants.QUERY_SUFFIX)
    except Exception as e:
        logger.error('Error querying LLM: %s', e)
        try:
            _db.save_question_answer(user_id=user_id, question=question, answer=f'Error querying LLM: {e}')
        except Exception:
            pass
        raise SystemError('Error querying LLM: %s' % e)

    _db.save_question_answer(user_id=user_id, question=question, answer=str(answer))
    return {'answer': str(answer)}


@app.post('/ask_google')
@log_params
def ask_google(data: AskInput, x_goog_authenticated_user_email: Annotated[str | None, Header()] = None) -> dict[str, str]:
    """Ask a question to the Google model and return the answer."""
    question = data.question
    answer = googleai_tools.query(search_query=question)
    return {'answer': answer}


@app.get('/people')
@log_params
def list_people() -> list[str]:
    """List all people names found in the database of uploaded resumes."""
    refresh_index()
    people = chatgpt_tools.load_resumes(resume_dir='', index_dir=INDEX_DIR)
    return [person for person in people.keys()]


@app.get('/health', name='Health check and information about the software version and configuration.')
@log_params
def healthcheck() -> dict:
    """Verify that the process is up without testing backend connections."""
    return solution.health_status()


@cache
@log
def refresh_index():
    """Refresh the index of resumes from the database."""
    global LAST_LOCAL_INDEX_UPDATE
    last_resume_refresh = admin_dao.AdminDAO().get_resumes_timestamp()
    if LAST_LOCAL_INDEX_UPDATE is None or LAST_LOCAL_INDEX_UPDATE < last_resume_refresh:
        logger.info('Refreshing local index of resumes...')
        gcs_tools.download(bucket_name=INDEX_BUCKET, local_dir=INDEX_DIR)
        LAST_LOCAL_INDEX_UPDATE = last_resume_refresh
        return

    logger.info('Skipping refresh of resumes index because it was done less than 60 seconds ago.')
