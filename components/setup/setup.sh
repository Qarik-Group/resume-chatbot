#!/usr/bin/env bash
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

# shellcheck source=/dev/null
source "../../setenv.sh"

###############################################
# MAIN
###############################################
if ! gsutil ls "gs://${ME_EMBEDDING_BUCKET}" &>/dev/null; then
  log "Creating GCS bucket [${ME_EMBEDDING_BUCKET}]..."
  gsutil mb -p "${PROJECT_ID}" -c regional -l "${REGION}" "gs://${ME_EMBEDDING_BUCKET}"
else
  log "GCS bucket [${ME_EMBEDDING_BUCKET}] already exists. Skipping..."
fi

log "Installing Python packages..."
pip install -r requirements.txt

TMP="./tmp"
mkdir -p "${TMP}"

log "Creating dummy embeddings file..."
python3 create_dummy_embeddings.py

log "Copy dummy embeddings to the GCS bucket..."
gsutil cp "${TMP}/dummy_embeddings.json" "gs://${ME_EMBEDDING_BUCKET}/init_index/dummy_embeddings.json"

log "Creating VertexAI Embeddings engine and other needed infra..."
python3 vertexai_setup.py
