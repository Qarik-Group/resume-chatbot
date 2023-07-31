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

from pathlib import Path
from typing import Annotated, Any
from datetime import datetime
from fastapi import Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chat_dao
from common import api_tools, constants, googleai_tools, llm_tools, solution, gcs_tools, admin_dao
from common.cache import cache
from common.log import Logger, log_params, log

logger = Logger(__name__).get_logger()
logger.info('Initializing...')

LAST_LOCAL_INDEX_UPDATE: datetime | None = None
LOCAL_DEVELOPMENT_MODE: bool = bool(solution.getenv('LOCAL_DEVELOPMENT_MODE', default=False))
INDEX_BUCKET: str = solution.getenv('EMBEDDINGS_BUCKET_NAME')
if LOCAL_DEVELOPMENT_MODE:
    INDEX_DIR: str = 'dev/tmp/embeddings'
else:
    INDEX_DIR: str = 'tmp/embeddings'


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


def get_user_id(user_email: str | None) -> str:
    """Extract user ID from the request headers.˝"""
    user_id: str = 'anonymous'
    if user_email is None:
        logger.warning('No authenticated user email found in the request headers.')
    else:
        # Header passed from IAP
        # Extract part of the x_goog_authenticated_user_email string after the ':'
        # Example: accounts.google.com:rkharkovski@qarik.com -> rkharkovski@qarik.com
        user_id = user_email.split(':')[-1]
    logger.debug('Received question from user: %s', user_id)
    return user_id


def run_query(question: str, user_id: str, query_engine: Any, llm_backend: str) -> str:
    """Run a query against the LLM model."""
    try:
        logger.debug('Querying LLM...')
        answer = str(query_engine.query(question))
    except Exception as e:
        logger.error('Error querying LLM: %s', e)
        try:
            _db.save_question_answer(user_id=user_id,
                                     question=question,
                                     answer=f'Error querying LLM: {e}',
                                     llm_backend=llm_backend)
        except Exception:
            pass
        raise SystemError('Error querying LLM: %s' % e)

    _db.save_question_answer(user_id=user_id,
                             question=question,
                             answer=answer,
                             llm_backend=llm_backend)
    return answer


class AskInput(BaseModel):
    question: str


@log_params
def ask_llm(data: AskInput,
            provider: constants.LlmProvider,
            x_goog_authenticated_user_email: Annotated[str | None, Header()] = None) -> dict[str, str]:
    """Ask a question to the given LLM model."""
    question = data.question
    refresh_index()
    query_engine = llm_tools.get_resume_query_engine(index_dir=INDEX_DIR, provider=provider)
    if query_engine is None:
        raise SystemError('No resumes found in the database. Please upload resumes.')

    user_id: str = get_user_id(x_goog_authenticated_user_email)
    answer: str = run_query(question=question,
                            user_id=user_id,
                            query_engine=query_engine,
                            llm_backend=constants.GPT_MODEL)
    return {'answer': answer}


@app.post('/ask_gpt')
@log_params
def ask_gpt(data: AskInput, x_goog_authenticated_user_email: Annotated[str | None, Header()] = None) -> dict[str, str]:
    """Ask a question to the GPT-3 model and return the answer."""
    return ask_llm(data=data, provider=constants.LlmProvider.OPEN_AI, x_goog_authenticated_user_email=x_goog_authenticated_user_email)


@app.post('/ask_palm')
@log_params
def ask_palm(data: AskInput, x_goog_authenticated_user_email: Annotated[str | None, Header()] = None) -> dict[str, str]:
    """Ask a question to the Google PaLM model."""
    return ask_llm(data=data, provider=constants.LlmProvider.GOOGLE_PALM, x_goog_authenticated_user_email=x_goog_authenticated_user_email)


@app.post('/ask_llama')
@log_params
def ask_llama(data: AskInput, x_goog_authenticated_user_email: Annotated[str | None, Header()] = None) -> dict[str, str]:
    """Ask a question to the local Llama 2 model."""
    return {'answer': 'Local Llama 2 is not implemented yet.'}


@app.post('/ask_google')
@log_params
def ask_google(data: AskInput, x_goog_authenticated_user_email: Annotated[str | None, Header()] = None) -> dict[str, str]:
    """Ask a question to the Google Enterprise Search (Gen AI) model."""
    question = data.question
    user_id: str = get_user_id(x_goog_authenticated_user_email)
    answer: str = run_query(question=question,
                            user_id=user_id,
                            query_engine=googleai_tools,
                            llm_backend='Google Enterprise Search')
    return {'answer': answer}


@app.get('/people')
@log_params
def list_people() -> list[str]:
    """List all people names found in the database of uploaded resumes."""
    refresh_index()
    people = llm_tools.load_resumes(resume_dir='', index_dir=INDEX_DIR)
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
    if LOCAL_DEVELOPMENT_MODE:
        index_path = Path(INDEX_DIR)
        if not index_path.exists():
            # Only generate embeddings if they do not exist
            llm_tools.generate_embeddings(resume_dir='dev/tmp', index_dir=INDEX_DIR)
        return

    global LAST_LOCAL_INDEX_UPDATE
    last_resume_refresh = admin_dao.AdminDAO().get_resumes_timestamp()
    if LAST_LOCAL_INDEX_UPDATE is None or LAST_LOCAL_INDEX_UPDATE < last_resume_refresh:
        logger.info('Refreshing local index of resumes...')
        gcs_tools.download(bucket_name=INDEX_BUCKET, local_dir=INDEX_DIR)
        LAST_LOCAL_INDEX_UPDATE = last_resume_refresh
        return

    logger.info('Skipping refresh of resumes index because no changes in source resume were detected.')
