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

from unidecode import unidecode
from google.cloud import discoveryengine
from common import solution
from common.log import Logger, log_params

logger = Logger(__name__).get_logger()
logger.info('Initializing...')

LOCATION = 'global'
SEARCH_ENGINE_ID = 'skills-search_1688081193007'
SERVING_CONFIG_ID = 'default_config'


@log_params
def query(search_query: str) -> str | None:
    """Query the Google Discovery Engine with summarization enabled."""
    # Create a client
    client = discoveryengine.SearchServiceClient()

    # The full resource name of the search engine serving config
    # e.g. projects/{project_id}/locations/{location}
    serving_config = client.serving_config_path(
        project=solution.PROJECT_ID,
        location=LOCATION,
        data_store=SEARCH_ENGINE_ID,
        serving_config=SERVING_CONFIG_ID,
    )

    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=search_query,
    )
    response = client.search(request)
    # https://cloud.google.com/generative-ai-app-builder/docs/reference/rest/v1/SearchResponse
    # print(response)

    for a in response.results[0].document.derived_struct_data['extractive_answers']:
        for b in a.items():
            return unidecode(str(b[1]))

    return None
