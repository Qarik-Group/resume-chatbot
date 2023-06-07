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

#############################################
# Deploy Cloud Run service
#############################################
deploy() {
  ARGS=(
    --image "${ARTIFACT_REGISTRY}/${IMAGE_NAME}"
    --service-account "${CHAT_SVC_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com"
    --region "${REGION}"
    --project "${PROJECT_ID}"
    --set-env-vars "OPENAI_API_KEY=${OPENAI_API_KEY}"
    --set-env-vars "PROJECT_ID=${PROJECT_ID}"
    --set-env-vars "LOG_LEVEL=DEBUG"
    --allow-unauthenticated
  )
  # --ingress all
  # The lines below only needed if using Serverless VPC Connector
  # --vpc-egress all-traffic
  # --vpc-connector "projects/${PROJECT_ID}/locations/${REGION}/connectors/${VPC_CONNECTOR_NAME}" \

  if [[ "${ENABLE_IAP}" == "true" ]]; then
    # TODO: In some cases when the CLoud Run scales down to 0, the IAP has trouble waiking it up
    ARGS+=(--min-instances 1)
    ARGS+=(--ingress internal-and-cloud-load-balancing)
  else
    ARGS+=(--ingress all)
  fi

  log "Deploying Cloud Run service [${CHAT_SVC_NAME}]..."
  set -o xtrace
  gcloud run deploy "${CHAT_SVC_NAME}" "${ARGS[@]}"
  set +o xtrace

  local PROJECT_NUMBER
  PROJECT_NUMBER=$(get_project_number "${PROJECT_ID}")

  if [[ "${ENABLE_IAP}" == "true" ]]; then
    log "Granting invoker role to IAP service..."
    gcloud run services add-iam-policy-binding "${CHAT_SVC_NAME}" \
      --member "serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-iap.iam.gserviceaccount.com" \
      --region "${REGION}" \
      --role "roles/run.invoker"
  fi

  log "Granting invoker role to domain users..."
  gcloud run services add-iam-policy-binding "${CHAT_SVC_NAME}" \
    --region "${REGION}" \
    --member "domain:${ORG_DOMAIN}" \
    --role "roles/run.invoker"
}

###############################################
# MAIN
###############################################
build "${IMAGE_NAME}"
deploy
if [[ "${ENABLE_IAP}" == "true" ]]; then
  create_iap "${CHAT_SVC_NAME}"
fi
