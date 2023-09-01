#!/bin/bash
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
set -o allexport
# shellcheck source=/dev/null
source "./.env"
# shellcheck source=/dev/null
source "./utils.sh"

print_header "Configuring Resume Chatbot"
setup_local_os
authenticate_gcp
install_firestore_emulator
install_python_virtual_env
enable_apis
create_registry
create_firestore_instance
create_resume_bucket
create_embeddings_bucket
define_chat_svc_sa
define_resume_svc_sa
create_sa "${UI_SVC_NAME}"
setup_resume_updates
create_eventarc_chat_channel
setup_vertexai

if [[ "${ENABLE_IAP}" == "true" ]]; then
  enable_oauth
  reserve_ip
  create_ssl_certificate
fi
print_footer
