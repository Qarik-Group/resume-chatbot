# Copyright 2023 Google LLC
# Copyright 2023 Qarik Group, LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Creation of a dummy embeddings file to initialize VertexAI."""

import json
import uuid
import numpy as np
from query_engine.matching_engine import ME_DIMENSIONS

# Create a dummy embeddings file to initialize when creating the index dummy embedding
init_embedding = {'id': str(uuid.uuid4()), 'embedding': list(np.zeros(ME_DIMENSIONS))}

# dump embedding to a local file
with open('tmp/dummy_embeddings.json', 'w') as f:
    json.dump(init_embedding, f)
