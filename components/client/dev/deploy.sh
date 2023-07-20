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
# Deploy Cloud Run service
#############################################
deploy() {
  ARGS=(
    --image "${ARTIFACT_REGISTRY}/${IMAGE_NAME}"
    --service-account "${UI_SVC_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com"
    --region "${REGION}"
    --project "${PROJECT_ID}"
    --allow-unauthenticated
  )

  if [[ "${ENABLE_IAP}" == "true" ]]; then
    ARGS+=(--ingress internal-and-cloud-load-balancing)
  else
    ARGS+=(--ingress all)
  fi

  log "Deploying Cloud Run service [${CHAT_SVC_NAME}]..."
  set -o xtrace
  gcloud run deploy "${UI_SVC_NAME}" "${ARGS[@]}"
  set +o xtrace

  local PROJECT_NUMBER
  PROJECT_NUMBER=$(get_project_number "${PROJECT_ID}")

  if [[ "${ENABLE_IAP}" == "true" ]]; then
    log "Granting invoker role to IAP service..."
    gcloud run services add-iam-policy-binding "${UI_SVC_NAME}" \
      --member "serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-iap.iam.gserviceaccount.com" \
      --region "${REGION}" \
      --role "roles/run.invoker"
  fi

  log "Granting invoker role to domain users..."
  gcloud run services add-iam-policy-binding "${UI_SVC_NAME}" \
    --member "domain:${ORG_DOMAIN}" \
    --region "${REGION}" \
    --role "roles/run.invoker"
}

###############################################
# MAIN
###############################################
cd ..
build "${IMAGE_NAME}"
deploy
if [[ "${ENABLE_IAP}" == "true" ]]; then
  create_iap "${UI_SVC_NAME}"
fi
echo "${DEPLOYMENT_COMPLETE_MARKER}"
