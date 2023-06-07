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

from fastapi import Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import api_tools
import solution
import llm_tools
from log import Logger, log_params

logger = Logger(__name__).get_logger()
logger.info('Initializing...')


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


class AskInput(BaseModel):
    question: str


@app.post('/ask')
@log_params
def ask(data: AskInput, x_goog_authenticated_user_email: Annotated[str | None, Header()] = None) -> dict[str, str]:
    question = data.question

    # TODO: investigate if this may be cached or shared across requests
    logger.debug('Initializing query engine...')
    query_engine = llm_tools.get_resume_query_engine()
    if query_engine is None:
        raise SystemError('No resumes found in the database. Please upload resumes.')

    # Here are the headers passed from IAP
    user_id: str = 'anonymous'
    if x_goog_authenticated_user_email is None:
        logger.warning('No authenticated user email found in the request headers.')
    else:
        # Extract part of the x_goog_authenticated_user_email string after the ':'
        # Example: accounts.google.com:rkharkovski@qarik.com -> rkharkovski@qarik.com
        user_id = x_goog_authenticated_user_email.split(':')[-1]
    logger.debug('Received question from user: %s', user_id)

    # logger.debug('Saving the question to Firestore')
    # chat_ref = db.collection('chats').document(user_id)
    # chat_ref.set({'user_id': user_id, 'question': question}, merge=True)

    logger.debug('Querying LLM...')
    answer = query_engine.query(question)
    # TODO - experiment with different prompt tunings
    # response = query_engine.query(query_text + constants.QUERY_SUFFIX)

    # logger.debug('Saving answer to Firestore...')
    # chat_ref.update({'answer': answer})

    return {'answer': str(answer)}


@app.get('/people')
@log_params
def list_people() -> list[str]:
    """List all people names found in the database of uploaded resumes."""
    people = llm_tools.load_resumes()
    return [person for person in people.keys()]


@app.get('/health', name='Health check and information about the software version and configuration.')
@log_params
def healthcheck() -> dict:
    """Verify that the process is up without testing backend connections."""
    return solution.health_status()
