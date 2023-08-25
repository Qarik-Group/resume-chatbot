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

# log "Get list of people..."
# gcurl -i "${CHAT_SVC_DEV_URL}/people"

log "Ask a question about a person..."
# gcurl -i -X POST \
#   -d "{\"question\":\"What is email of Steven Kim?\"}" \
#   "${CHAT_SVC_DEV_URL}/ask_vertex"

gcurl -i -X POST \
  -d "{\"question\":\"Where does Roman Kharkovski live?\"}" \
  "${CHAT_SVC_DEV_URL}/ask_gpt"
