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

#############################################
# Grant IAM roles to chat service account
#############################################
define_chat_svc_service_account() {
  local CHAT_SVC_SA_ROLES=(
    roles/datastore.user
  )

  create_sa "${CHAT_SVC_NAME}"
  local CHAT_SVC_EMAIL="${CHAT_SVC_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com"

  for role in "${CHAT_SVC_SA_ROLES[@]}"; do
    log "Applying [${role}] to [${CHAT_SVC_EMAIL}]..."
    gcloud -q projects add-iam-policy-binding "${PROJECT_ID}" \
      --member="serviceAccount:${CHAT_SVC_EMAIL}" --role="${role}" &>/dev/null
  done
}

#############################################
# Enable GCP APIs
#############################################
enable_apis() {
  log "Enable required GCP services..."
  gcloud services enable \
    appengine.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    cloudidentity.googleapis.com \
    cloudresourcemanager.googleapis.com \
    firestore.googleapis.com \
    logging.googleapis.com \
    run.googleapis.com \
    storage.googleapis.com

  if [[ "${ENABLE_IAP}" == "true" ]]; then
    gcloud services enable \
      certificatemanager.googleapis.com \
      compute.googleapis.com \
      iap.googleapis.com \
      vpcaccess.googleapis.com
  fi
}

###############################################
# MAIN
###############################################
print_header "Configuring Resume Chatbot"
authenticate_gcp
install_firestore_emulator
install_python_virtual_env
enable_apis
create_registry
create_firestore_instance
define_chat_svc_service_account
create_sa "${UI_SVC_NAME}"

if [[ "${ENABLE_IAP}" == "true" ]]; then
  enable_oauth
  reserve_ip
  create_ssl_certificate
fi
print_footer
