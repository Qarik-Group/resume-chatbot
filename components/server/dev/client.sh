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
set -u # Exit if variable is not set
set -e # Exit if error is detected during pipeline execution
cd ..
set -o allexport
# shellcheck source=/dev/null
source "../../.env"
# shellcheck source=/dev/null
source "./.env"
# shellcheck source=/dev/null
source "../../utils.sh"

# CHAT_SVC_URL=$(get_svc_url "${CHAT_SVC_NAME}")
CHAT_SVC_URL="https://34.95.89.166.nip.io"

log "CHAT_SVC_URL=${CHAT_SVC_URL}"
# Get list of people
gcurl -i "${CHAT_SVC_URL}/people"
