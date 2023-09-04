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
# shellcheck disable=SC2034

log "Running local 'setenv_dev.sh'"

COMPONENT_NAME="query_engine"
# shellcheck disable=SC2034
COMPONENT_DIR="${PROJECT_HOME}/components/${COMPONENT_NAME}"
LOG_LEVEL=DEBUG
IMAGE_NAME=${CHAT_SVC_NAME}-img
CACHE_TIMEOUT=60
PORT=8080
CHAT_SVC_DEV_URL="http://127.0.0.1:${QUERY_ENG_DEV_PORT}"
# CHAT_SVC_DEV_URL=$(get_svc_url "${CHAT_SVC_NAME}")
