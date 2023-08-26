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
import threading
from typing import Annotated, Any
from datetime import datetime
from langchain.llms import VertexAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.embeddings import VertexAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFDirectoryLoader
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
"""Keep track of the most recent local index update to avoid unnecessary refreshes."""

LLAMA_FILE_LOCK = threading.Lock()
"""Lock to prevent concurrent updates of the same index - needed in case we have more than one request processing."""

CHROMA_LOCK = threading.Lock()
"""Lock to prevent concurrent creation of langchain."""

LOCAL_DEVELOPMENT_MODE: bool = bool(solution.getenv('LOCAL_DEVELOPMENT_MODE', default=False))
"""Flag to indicate if we are running in local development mode."""

RESUME_BUCKET_NAME: str = solution.getenv('RESUME_BUCKET_NAME')
"""Location to download source PDF resumes from."""

INDEX_BUCKET: str = solution.getenv('EMBEDDINGS_BUCKET_NAME')
"""Location to download llama-index embeddings from."""

LOCAL_DEV_DATA_DIR: str = 'dev/tmp'
"""Location of the local data directory for development on local machine."""

LOCAL_PROD_DATA_DIR: str = 'tmp/chroma-source-resumes'
"""Location of the local data directory for storing resumes PDF files copied from GCS."""

if LOCAL_DEVELOPMENT_MODE:
    LLAMA_INDEX_DIR: str = 'dev/tmp/embeddings'
else:
    LLAMA_INDEX_DIR = 'tmp/embeddings'

LANGCHAIN_ENGINE = None
"""Langchain engine singleton that is used to answer questions."""

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


def run_query(question: Any, user_id: str, query_method: Any, llm_backend: str) -> Any:
    """Run a query against the LLM model."""
    try:
        logger.debug(f'Querying LLM [{llm_backend}]...')
        answer = query_method(question)
    except Exception as e:
        logger.error('Error querying LLM: %s', e)
        try:
            _db.save_question_answer(user_id=user_id,
                                     question=str(question),
                                     answer=f'Error querying LLM: {e}',
                                     llm_backend=llm_backend)
        except Exception:
            pass
        raise SystemError('Error querying LLM: %s' % e)

    _db.save_question_answer(user_id=user_id,
                             question=str(question),
                             answer=str(answer),
                             llm_backend=llm_backend)
    return answer


class AskInput(BaseModel):
    """Input parameters for the ask endpoint."""
    question: str


class VoteInput(BaseModel):
    """Input parameters for the vote endpoint."""
    llm_backend: str
    question: str
    answer: str
    upvoted: bool
    downvoted: bool


@app.get('/people')
@log_params
def list_people() -> list[str]:
    """List all people names found in the database of uploaded resumes."""
    refresh_llama_index()
    people = llm_tools.load_resumes(resume_dir='', index_dir=LLAMA_INDEX_DIR)
    return [person for person in people.keys()]


@app.get('/health', name='Health check and information about the software version and configuration.')
@log_params
def healthcheck() -> dict:
    """Verify that the process is up without testing backend connections."""
    return solution.health_status()


@log_params
def ask_llm(data: AskInput,
            provider: constants.LlmProvider,
            x_goog_authenticated_user_email: Annotated[str | None, Header()] = None) -> dict[str, str]:
    """Ask a question to the given LLM model."""
    question = data.question
    refresh_llama_index()
    query_engine = llm_tools.get_resume_query_engine(index_dir=LLAMA_INDEX_DIR, provider=provider)
    if query_engine is None:
        raise SystemError('No resumes found in the database. Please upload resumes.')

    user_id: str = get_user_id(x_goog_authenticated_user_email)
    answer = run_query(question=question,
                       user_id=user_id,
                       query_method=query_engine.query,
                       llm_backend=constants.GPT_MODEL)
    return {'answer': str(answer)}


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


@app.post('/ask_google')
@log_params
def ask_google(data: AskInput, x_goog_authenticated_user_email: Annotated[str | None, Header()] = None) -> dict[str, str]:
    """Ask a question to the Google Enterprise Search (Gen AI) model."""
    question = data.question
    user_id: str = get_user_id(x_goog_authenticated_user_email)
    answer = run_query(question=question,
                       user_id=user_id,
                       query_method=googleai_tools.query,
                       llm_backend='Google Enterprise Search')
    return {'answer': str(answer)}


@app.post('/ask_vertex')
@log_params
def ask_local(data: AskInput, x_goog_authenticated_user_email: Annotated[str | None, Header()] = None) -> dict[str, str]:
    """Ask a question to the local LLM model."""
    global LANGCHAIN_ENGINE
    refresh_chroma_index()
    answer = run_query(question={'query': data.question},
                       user_id=get_user_id(x_goog_authenticated_user_email),
                       query_method=LANGCHAIN_ENGINE,
                       llm_backend=f'Local LLM [{constants.GOOGLE_PALM_MODEL_LOCAL}]')
    # return {'answer': str(answer)}
    return {'answer': answer['result']}


@app.post('/vote')
@log_params
def vote(data: VoteInput, x_goog_authenticated_user_email: Annotated[str | None, Header()] = None) -> list:
    """Ask a question to the local LLM model."""
    return [{'name': 'ChatGPT',
             'up': 11,
             'down': -22, },
            {'name': 'Google Enterprise Search',
             'up': 33,
             'down': -44, },
            {'name': 'Google PaLM',
             'up': 55,
             'down': -66, },
            {'name': 'Google VertexAI',
             'up': 77,
             'down': -88, },
            ]


@cache
@log
def refresh_llama_index():
    """Refresh the index of resumes from the database using Llama-Index."""
    if LOCAL_DEVELOPMENT_MODE:
        index_path = Path(LLAMA_INDEX_DIR)
        if not index_path.exists():
            # TODO - need to generate proper embeddings for each provider, not hard coded
            llm_tools.generate_embeddings(resume_dir=LOCAL_DEV_DATA_DIR, index_dir=LLAMA_INDEX_DIR,
                                          provider=constants.LlmProvider.OPEN_AI)
        return

    global LAST_LOCAL_INDEX_UPDATE
    global LLAMA_FILE_LOCK
    last_resume_refresh = admin_dao.AdminDAO().get_resumes_timestamp()
    if LAST_LOCAL_INDEX_UPDATE is None or LAST_LOCAL_INDEX_UPDATE < last_resume_refresh:
        logger.info('Refreshing local index of resumes...')
        # Prevent concurrent updates of the same index - needed in case we have more than one request processing
        with LLAMA_FILE_LOCK:
            # Check for condition again because the index may have been updated while we were waiting for the lock
            if LAST_LOCAL_INDEX_UPDATE is None or LAST_LOCAL_INDEX_UPDATE < last_resume_refresh:
                gcs_tools.download(bucket_name=INDEX_BUCKET, local_dir=LLAMA_INDEX_DIR)
        LAST_LOCAL_INDEX_UPDATE = last_resume_refresh
        return

    logger.info('Skipping refresh of resumes index because no changes in source resumes were detected.')


@log
def create_langchain_client() -> None:
    global LANGCHAIN_ENGINE

    if LOCAL_DEVELOPMENT_MODE:
        source_pdf_path = LOCAL_DEV_DATA_DIR
    else:
        source_pdf_path = LOCAL_PROD_DATA_DIR
        # Download source PDF files from GCS into local folder for processing
        gcs_tools.download(bucket_name=RESUME_BUCKET_NAME, local_dir=LOCAL_PROD_DATA_DIR)

    # Load docs...
    loader = PyPDFDirectoryLoader(path=source_pdf_path)
    documents = loader.load()

    # split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2500, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    logger.info(f'# of documents created from source PDFs = {len(docs)}')

    embeddings = VertexAIEmbeddings()

    # Store docs in local vector store as index
    # it may take a while since API is rate limited
    db = Chroma.from_documents(documents=docs, embedding=embeddings)

    # Expose index to the retriever
    retriever = db.as_retriever(search_type='similarity', search_kwargs={'k': 15})

    # LLM model
    llm = VertexAI(model_name=constants.GOOGLE_PALM_MODEL_LOCAL, max_output_tokens=1024,
                   temperature=0.0, top_p=0.3, top_k=10, verbose=True)

    # Create chain to answer questions
    # Uses LLM to synthesize results from the search index.
    # We use Vertex PaLM Text API for LLM
    LANGCHAIN_ENGINE = RetrievalQA.from_chain_type(
        llm=llm, chain_type='stuff', retriever=retriever, return_source_documents=False)


@cache
@log
def refresh_chroma_index():
    """Refresh the index of resumes from the database using Chroma Vector DB."""
    global LAST_LOCAL_INDEX_UPDATE
    global CHROMA_LOCK
    global LANGCHAIN_ENGINE

    if LOCAL_DEVELOPMENT_MODE:
        # In local development mode we don't need to refresh the index and only load it on the first time
        if LAST_LOCAL_INDEX_UPDATE is None:
            last_resume_refresh = solution.now()
        else:
            last_resume_refresh = LAST_LOCAL_INDEX_UPDATE
    else:
        last_resume_refresh = admin_dao.AdminDAO().get_resumes_timestamp()
        if last_resume_refresh is None:
            last_resume_refresh = solution.now()

    if LAST_LOCAL_INDEX_UPDATE is None or \
            LANGCHAIN_ENGINE is None or \
            LAST_LOCAL_INDEX_UPDATE < last_resume_refresh:
        # Prevent concurrent updates of the same index - needed in case we have more than one request processing
        with CHROMA_LOCK:
            # Check for condition again because the index may have been updated while we were waiting for the lock
            if LAST_LOCAL_INDEX_UPDATE is None or \
                    LANGCHAIN_ENGINE is None or \
                    LAST_LOCAL_INDEX_UPDATE < last_resume_refresh:
                create_langchain_client()
        LAST_LOCAL_INDEX_UPDATE = last_resume_refresh
        return
