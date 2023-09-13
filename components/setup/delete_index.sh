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

# Get index ID from vertex AI
INDEX_NAME=$(gcloud ai indexes list \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --format="value(name)")

INDEX_ID=$(gcloud ai indexes list \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --format="value(id)")

ENDPOINT=$(gcloud ai index-endpoints list \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --format="value(name)")

gcloud ai index-endpoints undeploy-index "${ENDPOINT}" \
  --deployed-index-id "${INDEX_NAME}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}"

gcloud ai index-endpoints delete "${ENDPOINT}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}"

gcloud ai indexes delete "${INDEX_ID}" \
  --project "${PROJECT_ID}" \
  --region "${REGION}"
