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

import threading
from datetime import datetime
from typing import Any

from common import admin_dao, constants, gcs_tools, solution
from common.cache import cache
from common.log import Logger, log
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.embeddings import VertexAIEmbeddings  # type: ignore
from langchain.llms import VertexAI  # type: ignore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

logger = Logger(__name__).get_logger()
logger.info('Initializing...')

CHUNK_SIZE: int = 2500
"""Number of characters to split the resume into for processing."""

CHUNK_OVERLAP: int = 0
"""Number of characters to overlap between chunks."""

MAX_OUTPUT_TOKENS: int = 1024
"""Maximum number of tokens to generate."""

TEMPERATURE: float = 0.0
"""Temperature for sampling."""

TOP_P: float = 0.3
"""Top p for sampling."""

TOP_K: int = 10
"""Top k for sampling."""

SIMILARITY_SEARCH_K: int = 11
"""Number of similar documents to return from the index."""

LANGCHAIN_ENGINE: Any = None
"""Langchain engine singleton that is used to answer questions."""

RESUME_BUCKET_NAME: str = solution.getenv('RESUME_BUCKET_NAME')
"""Location to download source PDF resumes from."""

LOCAL_PROD_DATA_DIR: str = 'tmp/chroma-source-resumes'
"""Location of the local data directory for storing resumes PDF files copied from GCS."""

CHROMA_LOCK = threading.Lock()
"""Lock to prevent concurrent creation of langchain."""

LAST_LOCAL_INDEX_UPDATE: datetime | None = None
"""Keep track of the most recent local index update to avoid unnecessary refreshes."""

LOCAL_DEV_DATA_DIR: str = 'dev/tmp'
"""Location of the local data directory for development on local machine."""


@log
def _create_langchain_client():
    """Create a new Langchain client and initialize the index. Returns Langchain engine singleton."""
    global LANGCHAIN_ENGINE

    if solution.LOCAL_DEVELOPMENT_MODE:
        source_pdf_path = LOCAL_DEV_DATA_DIR
    else:
        source_pdf_path = LOCAL_PROD_DATA_DIR
        # Download source PDF files from GCS into local folder for processing
        gcs_tools.download(bucket_name=RESUME_BUCKET_NAME, local_dir=LOCAL_PROD_DATA_DIR)

    # Load docs...
    loader = PyPDFDirectoryLoader(path=source_pdf_path)
    documents = loader.load()

    # split the documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    docs = text_splitter.split_documents(documents)
    logger.info(f'# of documents created from source PDFs = {len(docs)}')

    embeddings = VertexAIEmbeddings()

    # Store docs in local vector store as index
    # it may take a while since API is rate limited
    db = Chroma.from_documents(documents=docs, embedding=embeddings)

    # Expose index to the retriever
    retriever = db.as_retriever(search_type='similarity', search_kwargs={'k': SIMILARITY_SEARCH_K})

    # LLM model
    llm = VertexAI(model_name=constants.GOOGLE_PALM_MODEL,
                   max_output_tokens=MAX_OUTPUT_TOKENS,
                   temperature=TEMPERATURE,
                   top_p=TOP_P,
                   top_k=TOP_K,
                   verbose=True)

    # Create chain to answer questions
    # Uses LLM to synthesize results from the search index.
    # We use Vertex PaLM Text API for LLM
    LANGCHAIN_ENGINE = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type='stuff',
        retriever=retriever,
        return_source_documents=False)


@cache
@log
def _refresh_chroma_index() -> None:
    """Refresh the index of resumes from the database using Chroma Vector DB. Returns retrieval engine client."""
    global CHROMA_LOCK
    global LAST_LOCAL_INDEX_UPDATE

    if solution.LOCAL_DEVELOPMENT_MODE:
        # In local development mode we don't need to refresh the index and only load it on the first time
        if LAST_LOCAL_INDEX_UPDATE is None:
            last_resume_refresh: datetime = solution.now()
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
                _create_langchain_client()


@log
def query(question: str) -> str:
    """Ask a question to the Google PaLM model using local index store in ChromaDB and Langchain. For large datasets this will not scale well."""
    global LANGCHAIN_ENGINE
    _refresh_chroma_index()
    # answer = LANGCHAIN_ENGINE({'query': query})['result']
    answer = LANGCHAIN_ENGINE(question)['result']
    return str(answer)
