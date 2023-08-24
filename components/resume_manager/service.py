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

import fastapi
from common import api_tools, constants, gcs_tools, llm_tools, solution, admin_dao
from common.log import Logger, log_params

logger = Logger(__name__).get_logger()
logger.info('Initializing...')


INDEX_BUCKET: str = solution.getenv('EMBEDDINGS_BUCKET_NAME')
RESUME_DIR: str = 'tmp'
INDEX_DIR: str = f'{RESUME_DIR}/embeddings'

app = api_tools.ServiceAPI(title='Resume PDF Manager', description='Eventarc handler.')

# In case you need to print the log of all inbound HTTP headers
app.router.route_class = api_tools.DebugHeaders


@app.post('/resumes', name='Handle Eventarc events.')
@log_params
def update_embeddings(event_data: dict = fastapi.Body()) -> dict:
    """Handle resume updates in GCS bucket and generate embeddings."""
    gcs_tools.download(bucket_name=event_data['bucket'], local_dir=RESUME_DIR)
    # TODO - need to generate proper embeddings for each provider, not hard coded
    llm_tools.generate_embeddings(resume_dir=RESUME_DIR, index_dir=INDEX_DIR, provider=constants.LlmProvider.OPEN_AI)
    gcs_tools.upload(bucket_name=INDEX_BUCKET, local_dir=INDEX_DIR)
    admin_dao.AdminDAO().touch_resumes(timestamp=solution.now())
    return {'status': 'ok'}


@app.get('/health', name='Health check and information about the software version and configuration.')
@log_params
def healthcheck() -> dict:
    """Verify that the process is up without testing backend connections."""
    return solution.health_status()
