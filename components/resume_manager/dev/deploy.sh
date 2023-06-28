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

#############################################
# Create Eventarc trigger to call service when GCS state changes
#############################################
create_gcs_trigger() {
  local TRIGGER_ADD="new-resume"
  local TRIGGER_DELETE="delete-resume"
  local PROJECT_NUMBER
  PROJECT_NUMBER=$(get_project_number "${PROJECT_ID}")

  if gcloud eventarc triggers list --location "${REGION}" --project "${PROJECT_ID}" | grep "${TRIGGER_ADD}"; then
    log "Trigger [${TRIGGER_ADD}] already exists, skipping..."
  else
    log "Creating Eventarc trigger to call service when new resume is added..."
    gcloud eventarc triggers create "${TRIGGER_ADD}" \
      --location "${REGION}" \
      --destination-run-service "${RESUME_SVC_NAME}" \
      --destination-run-path "/resumes" \
      --destination-run-region "${REGION}" \
      --event-filters "type=google.cloud.storage.object.v1.finalized" \
      --event-filters "bucket=${RESUME_BUCKET_NAME}" \
      --service-account "${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
  fi

  if gcloud eventarc triggers list --location "${REGION}" --project "${PROJECT_ID}" | grep "${TRIGGER_DELETE}"; then
    log "Trigger [${TRIGGER_DELETE}] already exists, skipping..."
  else
    log "Creating Eventarc trigger to call service when resume is deleted..."
    gcloud eventarc triggers create "${TRIGGER_DELETE}" \
      --location "${REGION}" \
      --destination-run-service "${RESUME_SVC_NAME}" \
      --destination-run-path "/resumes" \
      --destination-run-region "${REGION}" \
      --event-filters "type=google.cloud.storage.object.v1.deleted" \
      --event-filters "bucket=${RESUME_BUCKET_NAME}" \
      --service-account "${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
  fi
}
#############################################
# Deploy Cloud Run service
#############################################
deploy() {
  ARGS=(
    --image "${ARTIFACT_REGISTRY}/${IMAGE_NAME}"
    --service-account "${RESUME_SVC_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com"
    --region "${REGION}"
    --project "${PROJECT_ID}"
    --set-env-vars "PROJECT_ID=${PROJECT_ID}"
    --set-env-vars "LOG_LEVEL=${LOG_LEVEL}"
    --set-env-vars "OPENAI_API_KEY=${OPENAI_API_KEY}"
    --set-env-vars "EMBEDDINGS_BUCKET_NAME=${EMBEDDINGS_BUCKET_NAME}"
    --allow-unauthenticated
    --ingress internal
  )

  log "Deploying Cloud Run service [${RESUME_SVC_NAME}]..."
  set -o xtrace
  gcloud run deploy "${RESUME_SVC_NAME}" "${ARGS[@]}"
  set +o xtrace
}

###############################################
# MAIN
###############################################
TMP="./tmp/source"
prepare_sources "${TMP}"
pushd "${TMP}" || die "Unable to change directory to [${TMP}]"
build "${IMAGE_NAME}"
popd || exit
deploy
create_gcs_trigger
