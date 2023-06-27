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
source "../../../setenv.sh"

# curl --url "${RESUME_MGR_DEV_URL}/health"

# curl -X POST \
#   --url "${RESUME_MGR_DEV_URL}/resumes"

# curl -X POST \
#   -d "{\"aa\":\"bb\"}" \
#   -H "Content-Type: application/json" \
#   --url "${RESUME_MGR_DEV_URL}/resumes"

MSG_FILE="test_gcs_event.json"
curl -X POST \
  -d "@${MSG_FILE}" \
  -H "Content-Type: application/json" \
  --url "${RESUME_MGR_DEV_URL}/resumes"
