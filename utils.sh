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

###############################################
# Common constants
###############################################
# Seconds in a minute
ONE_SECOND="1"
# Seconds in a minute
ONE_MINUTE=$((ONE_SECOND * 60))
# Seconds in an hour
ONE_HOUR=$((ONE_MINUTE * 60))
# Seconds in a single day
ONE_DAY=$((ONE_HOUR * 24))
# shellcheck disable=SC2034
ONE_MONTH=$((ONE_DAY * 31))
# shellcheck disable=SC2034

###############################################
# Starts measurements of time
###############################################
start_timer() {
  if [ -z ${__START_TIME__+x} ]; then
    __START_TIME__=$(date +%s)
  fi
}

###############################################
# Stop timer and write data into the log file
###############################################
measure_timer() {
  if [ -z ${__START_TIME__+x} ]; then
    __MEASURED_TIME__=0
    start_timer
  else
    local END_TIME
    END_TIME=$(date +%s)
    local TIMER
    TIMER=$((END_TIME - __START_TIME__))
    __MEASURED_TIME__=$(printf "%.0f\n" "${TIMER}")
  fi
}

SEPARATOR__IN="------>>>>>>"
SEPARATOR_OUT="<<<<<<------"
_LOG_COLOR='\033[32m'
_NORMAL_COLOR='\033[0m'
###############################################
# Print starting headlines of the script
# Params:
#   1 - text to show
###############################################
print_header() {
  start_timer
  local CALLER
  CALLER="$(basename "$(test -L "$0" && readlink "$0" || echo "$0")")"
  printf "${_LOG_COLOR}%s STARTED: ${CALLER}${_NORMAL_COLOR} %s\n" "${SEPARATOR__IN}" "$1"
}

###############################################
# Print closing footer of the scrit
###############################################
print_footer() {
  measure_timer
  local CALLER
  CALLER="$(basename "$(test -L "$0" && readlink "$0" || echo "$0")")"
  printf "${_LOG_COLOR}%s FINISHED: ${CALLER}${_NORMAL_COLOR} %s seconds\n" "${SEPARATOR_OUT}" "${__MEASURED_TIME__}"
}

###############################################
# Wait for user input
###############################################
pause() {
  read -r -p "Press Enter to continue or Ctrl-C to terminate..."
}

##############################################################################
# Replace standard ECHO with custom ou t
# PARAMS: 1 - Text to show (mandatory)
#         2 - Logging level (optional) - see levels below
##############################################################################
# Available logging levels (least to most verbose)
ECHO_NONE="0"
ECHO_NO_PREFIX="1"
ECHO_ERROR="2"
ECHO_WARNING="3"
ECHO_INFO="4"
ECHO_DEBUG="5"
# Default logging level
ECHO_LEVEL="${ECHO_INFO}"

log() {
  local CALLER
  CALLER="$(basename "$(test -L "$0" && readlink "$0" || echo "$0")")"
  local RED='\033[0;31m'
  local GREEN='\033[32m'
  local ORANGE='\033[33m'
  local PREFIX="${CALLER}: "

  if [ $# -gt 1 ]; then
    local ECHO_REQUESTED=$2
  else
    local ECHO_REQUESTED=${ECHO_INFO}
  fi

  if [ "${ECHO_REQUESTED}" -gt ${ECHO_LEVEL} ]; then return; fi
  if [ "${ECHO_REQUESTED}" = ${ECHO_NONE} ]; then return; fi
  if [ "${ECHO_REQUESTED}" = ${ECHO_ERROR} ]; then PREFIX="${RED}[ERROR] ${PREFIX}"; fi
  if [ "${ECHO_REQUESTED}" = ${ECHO_WARNING} ]; then PREFIX="${RED}[WARNING] ${PREFIX}"; fi
  if [ "${ECHO_REQUESTED}" = ${ECHO_INFO} ]; then PREFIX="${GREEN}[INFO] ${PREFIX}"; fi
  if [ "${ECHO_REQUESTED}" = ${ECHO_DEBUG} ]; then PREFIX="${ORANGE}[DEBUG] ${PREFIX}"; fi
  if [ "${ECHO_REQUESTED}" = ${ECHO_NO_PREFIX} ]; then PREFIX="${GREEN}"; fi

  measure_timer
  printf "${PREFIX}%s${_NORMAL_COLOR} ${__MEASURED_TIME__}s\n" "$1"
}

#############################################
# Print an error message to stderr and exit the current script
# Arguments:
#  Message to display.
#  Error code to exit with. (optional, defult: 1). If the exit code is 0,
#  no red color or stderr is used
# Outputs:
#  Message to stderr and stdout
#############################################
die() {
  if [ -n "${2+x}" ] && [ "${2}" == "0" ]; then
    log "$1"
  else
    log "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $*" "${ECHO_ERROR}" >&2
  fi
  exit "${2:-1}" # exit with second parameter value (default: 1)
}

###############################################################################
# Lookup Project number
# Input:
#   $1 (optional) - or use PROJECT_ID variable
# Returns:
#   project number
###############################################################################
get_project_number() {
  local ID
  if [ -z ${1+x} ]; then
    ID="${PROJECT_ID}"
  else
    ID="${1}"
  fi
  if ! gcloud projects describe "${ID}" --format="value(projectNumber)" 2>/dev/null; then
    echo ""
  fi
}

#############################################
# Custom Curl command
#############################################
gcurl() {
  TOKEN=$(gcloud auth print-identity-token)
  curl -H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json" --fail-with-body "$@" || die
}

#############################################
# Lookup name of the cloud run service
# Input:
#   $1 - name of the service
#   Must have REGION and PROJECT_ID globally set (which it always is)
# Returns:
#   URL of the service
#############################################
get_svc_url() {
  if ! gcloud run services describe "${1}" \
    --region "${REGION}" \
    --format "value(status.url)" \
    --project "${PROJECT_ID}" 2>/dev/null; then
    echo ""
  fi
}

#############################################
# Install Firebase local emulator
#############################################
install_firestore_emulator() {
  if [[ -d /opt/homebrew/lib/node_modules/firebase-tools ]]; then
    log "Firebase emulator already exists. Skipping..."
    return
  fi
  log "Install Firebase local emulator..."
  npm install -g firebase-tools
}

#############################################
# Install Python virtualenv
#############################################
install_python_virtual_env() {
  if ! command -v python3 &>/dev/null; then
    die "Python is not installed. Please install Python 3.11+"
  fi

  if [[ -d .venv ]]; then
    log "Python virtual env already exists. Skipping..."
  else
    log "Create Python virtual env..."
    python -m venv .venv
  fi
  source .venv/bin/activate
}

#############################################
# GCP auth
#############################################
authenticate_gcp() {
  log "Authenticate with Google Cloud..."
  gcloud auth login
  gcloud config set project "${PROJECT_ID}"
  log "Create Application Default Credentials for running local processes connecting to GCP services..."
  gcloud auth application-default login
}

#############################################
# Create Artifact registry
#############################################
create_registry() {
  # Check if registry REGISTRY_NAME already exists
  if gcloud artifacts repositories list --location "${REGION}" --format='value(name)' | grep "${REGISTRY_NAME}"; then
    log "Artifact registry [${REGISTRY_NAME}] already exists. Skipping..."
  else
    log "Create artifact registry..."
    gcloud artifacts repositories create "${REGISTRY_NAME}" \
      --repository-format docker \
      --location "${REGION}" \
      --description "Container registry for app images"
  fi

  CURRENT_GCP_USER=$(gcloud config get-value account)
  log "Grant editor permission to the repos in this project..."
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member "user:${CURRENT_GCP_USER}" \
    --role roles/artifactregistry.repoAdmin

  log "Setup authentication for registry..."
  gcloud auth configure-docker "${REGION}-docker.pkg.dev"
}

#############################################
# App Engine Application Creation
# This is needed for Firestore DB
#############################################
enable_app_engine() {
  if ! (gcloud app describe --project "${PROJECT_ID}" 2>/dev/null | grep "servingStatus: SERVING"); then
    log "Creating App Engine application for project [${PROJECT_ID}] in [${GAE_REGION}]."
    gcloud app create --project "${PROJECT_ID}" --region "${GAE_REGION}" 1>/dev/null
  else
    log "App Engine application already exists in project [${PROJECT_ID}]."
  fi
}

#############################################
# App Engine Application Creation
#############################################
create_firestore_instance() {
  enable_app_engine
  if gcloud app describe --project="${PROJECT_ID}" &>/dev/null; then
    if gcloud firestore databases list --project "${PROJECT_ID}" &>/dev/null; then
      log "Firestore already exists. Skipping..."
    else
      log "Create Firestore in Native mode."
      gcloud firestore databases create \
        --project "${PROJECT_ID}" \
        --location="${FIRESTORE_LOCATION}" \
        --quiet 1>/dev/null
    fi
    log "CHanging Firestore to Native mode..."
    gcloud alpha firestore databases update \
      --project "${PROJECT_ID}" \
      --type=firestore-native
  else
    die "App Engine is not enabled for project [${PROJECT_ID}]. Can not use Firestore."
  fi
}

#############################################
# Create SA to run the service
# Arguments:
#   $1: Service name
#############################################
create_sa() {
  local SVC_NAME=$1
  local SVC_ACCOUNT="${SVC_NAME}-sa"
  # Check if the service account SVC_ACCOUNT exists, and if not, create it in GCP IAM
  if [[ $(gcloud iam service-accounts list --filter="name:${SVC_ACCOUNT}" --format='value(name)') == "" ]]; then
    log "Creating SA [${SVC_ACCOUNT}] to run the service..."
    gcloud iam service-accounts create "${SVC_ACCOUNT}" \
      --description="Service account to run the ${SVC_NAME} service" \
      --display-name="${SVC_NAME} Service Account"
  else
    log "SA [${SVC_ACCOUNT}] already exists. Skipping..."
  fi
}

#############################################
# Create temp directory with sources for build
# Arguments:
#   $1: TMP directory
#############################################
prepare_sources() {
  local TMP=$1
  rm -rf "${TMP}"
  mkdir -p "${TMP}"
  cp ../* "${TMP}" || true
  cp -r ../../common "${TMP}"
}

#############################################
# Build docker image
# Arguments:
#   $1: Image name
#############################################
build() {
  local IMAGE_NAME=$1
  log "Building docker image [${IMAGE_NAME}] and pushing to artifact registry [${ARTIFACT_REGISTRY}]..."
  gcloud builds submit . --tag "${ARTIFACT_REGISTRY}/${IMAGE_NAME}"
}

#############################################
# Create static external IP for load balancer
#############################################
reserve_ip() {
  log "Reserving external IP for chat service..."
  gcloud compute addresses create "${CHAT_SVC_NAME}-ip" \
    --network-tier PREMIUM \
    --ip-version IPV4 \
    --global

  log "Reserving external IP for UI service..."
  gcloud compute addresses create "${UI_SVC_NAME}-ip" \
    --network-tier PREMIUM \
    --ip-version IPV4 \
    --global
}

#############################################
# Create self-managed SSL certificate
#############################################
create_ssl_certificate() {
  CHAT_DOMAIN=$(gcloud compute addresses list --filter "${CHAT_SVC_NAME}-ip" --format='value(ADDRESS)').nip.io
  UI_DOMAIN=$(gcloud compute addresses list --filter "${UI_SVC_NAME}-ip" --format='value(ADDRESS)').nip.io

  log "Create a Google-managed SSL certificate resource..."
  gcloud compute ssl-certificates create "${CERT}" \
    --description "Skills bot certificate" \
    --domains "${CHAT_DOMAIN},${UI_DOMAIN}" \
    --global

  log "Provisioning a Google-managed certificate might take up to 60 minutes..." ${ECHO_WARNING}
}

#############################################
# Prepare Oauth for IAP to protect CloudRun
# This is based on the following article:
# https://codelabs.developers.google.com/secure-serverless-application-with-identity-aware-proxy#0
#############################################
enable_oauth() {
  local PROJECT_NUMBER
  PROJECT_NUMBER=$(get_project_number "${PROJECT_ID}")
  if gcloud alpha iap oauth-brands list | grep "${PROJECT_NUMBER}"; then
    log "Brand already exists. Skipping..."
  else
    CURRENT_GCP_USER=$(gcloud config get-value account)
    log "Create a brand for OAuth consent screen..."
    gcloud alpha iap oauth-brands create \
      --application_title "Resume Chatbot" \
      --support_email "${CURRENT_GCP_USER}"
  fi

  log "Create a client using the brand name..."
  gcloud alpha iap oauth-clients create "projects/${PROJECT_ID}/brands/${PROJECT_NUMBER}" \
    --display_name "${OAUTH_CLIENT_DISPLAY_NAME}"

  log "Create IAP service account..."
  gcloud beta services identity create --service=iap.googleapis.com --project "${PROJECT_ID}"
}

#############################################
# Create serverless VPC connector for CloudRun instances
#############################################
create_serverless_connector() {
  local VPC_NAME="skills-bot-vpc"
  local SUBNET_NAME="skills-bot-subnet"

  log "Creating custom VPC network..."
  gcloud compute networks create "${VPC_NAME}" --subnet-mode custom

  log "Creating VPC subnetwork..."
  gcloud compute networks subnets create "${SUBNET_NAME}" \
    --network "${VPC_NAME}" \
    --range "10.0.0.0/24" \
    --region "${REGION}"

  log "Create serverless connector..."
  gcloud compute networks vpc-access connectors create "${VPC_CONNECTOR_NAME}" \
    --network "${VPC_NAME}" \
    --region "${REGION}" \
    --range "10.1.0.0/28"
}

#############################################
# Create Network Endpoint Group
# This is needed to protect CloudRun with IAP
# Arguments:
#   $1: Service name
#############################################
create_iap() {
  local SVC_NAME=$1

  NEG="${SVC_NAME}-neg"
  BACKEND="${SVC_NAME}-backend"
  URL_MAP="${SVC_NAME}-url-map"
  HTTP_PROXY="${SVC_NAME}-http-proxy"
  FORWARDING_RULE="${SVC_NAME}-forwarding-rule"

  if gcloud compute forwarding-rules list --filter="${FORWARDING_RULE}" --format='value(name)'; then
    log "Forwarding rule [${FORWARDING_RULE}] already exists, and most likely IAP is already setup. Skipping..."
    return
  fi

  DOMAIN=$(gcloud compute addresses list --filter "${SVC_NAME}-ip" --format='value(ADDRESS)').nip.io
  local PROJECT_NUMBER
  PROJECT_NUMBER=$(get_project_number "${PROJECT_ID}")

  log "Creating Network Endpoint Group..."
  gcloud compute network-endpoint-groups create "${NEG}" \
    --project "${PROJECT_ID}" \
    --region "${REGION}" \
    --network-endpoint-type=serverless \
    --cloud-run-service "${SVC_NAME}"

  log "Creating backend for NEG..."
  gcloud compute backend-services create "${BACKEND}" --global

  log "Add NEG to backend..."
  gcloud compute backend-services add-backend "${BACKEND}" \
    --global \
    --network-endpoint-group "${NEG}" \
    --network-endpoint-group-region "${REGION}"

  log "Add URL map to backend..."
  gcloud compute url-maps create "${URL_MAP}" --default-service "${BACKEND}"

  log "Create target HTTPS proxy..."
  gcloud compute target-https-proxies create "${HTTP_PROXY}" \
    --ssl-certificates "${CERT}" \
    --url-map "${URL_MAP}"

  if gcloud compute forwarding-rules list --filter="${FORWARDING_RULE}" --format='value(name)'; then
    log "Forwarding rule [${FORWARDING_RULE}] already exists. Skipping..."
  else
    log "Create a forwarding rule to route incoming requests to the proxy..."
    gcloud compute forwarding-rules create "${FORWARDING_RULE}" \
      --load-balancing-scheme=EXTERNAL \
      --network-tier=PREMIUM \
      --address "${SVC_NAME}-ip" \
      --global \
      --ports=443 \
      --target-https-proxy "${HTTP_PROXY}"
  fi

  log "Store the client name, ID and secret..."
  CLIENT_NAME=$(gcloud alpha iap oauth-clients list "projects/${PROJECT_ID}/brands/${PROJECT_NUMBER}" \
    --format='value(name)' \
    --filter "displayName:${OAUTH_CLIENT_DISPLAY_NAME}")

  CLIENT_ID=${CLIENT_NAME##*/}
  log "ClientID=${CLIENT_ID}"
  log "Client Name=${CLIENT_NAME}"
  CLIENT_SECRET=$(gcloud alpha iap oauth-clients describe "${CLIENT_NAME}" --format='value(secret)')

  log "Enable IAP on the backend service..."
  gcloud iap web enable --resource-type=backend-services \
    --oauth2-client-id "${CLIENT_ID}" \
    --oauth2-client-secret "${CLIENT_SECRET}" \
    --service "${BACKEND}"

  log "Verify the SSL certificate is ACTIVE..."
  gcloud compute ssl-certificates list --format='value(MANAGED_STATUS)'

  log "Service URL..."
  log "https://${DOMAIN}"
  log "It takes 5-7 minutes for the changes to take effect!" ${ECHO_WARNING}

  log "Grant access to IAP resource to users..."
  gcloud iap web add-iam-policy-binding \
    --resource-type backend-services \
    --service "${BACKEND}" \
    --member "domain:${ORG_DOMAIN}" \
    --role='roles/iap.httpsResourceAccessor'
}

#############################################
# Grant IAM roles to chat service account
#############################################
define_chat_svc_sa() {
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

  log "Granting GCS reader role to [${CHAT_SVC_EMAIL}] on bucket [${EMBEDDINGS_BUCKET_NAME}]..."
  gsutil iam ch "serviceAccount:${CHAT_SVC_EMAIL}:roles/storage.objectViewer" "gs://${EMBEDDINGS_BUCKET_NAME}"
}

#############################################
# Grant IAM roles to resume service account
#############################################
define_resume_svc_sa() {
  create_sa "${RESUME_SVC_NAME}"
  local RESUME_SVC_EMAIL="${RESUME_SVC_NAME}-sa@${PROJECT_ID}.iam.gserviceaccount.com"

  log "Granting GCS admin role to [${RESUME_SVC_EMAIL}] on bucket [${EMBEDDINGS_BUCKET_NAME}]..."
  gsutil iam ch "serviceAccount:${RESUME_SVC_EMAIL}:roles/storage.admin" "gs://${EMBEDDINGS_BUCKET_NAME}"

  log "Granting GCS reader role to [${RESUME_SVC_EMAIL}] on bucket [${RESUME_BUCKET_NAME}]..."
  gsutil iam ch "serviceAccount:${RESUME_SVC_EMAIL}:roles/storage.objectViewer" "gs://${RESUME_BUCKET_NAME}"
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
    eventarc.googleapis.com \
    eventarcpublishing.googleapis.com \
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

#############################################
# Create a GCS bucket for resume storage
#############################################
create_resume_bucket() {
  if ! gsutil ls "gs://${RESUME_BUCKET_NAME}" &>/dev/null; then
    log "Creating GCS bucket for resume storage..."
    gsutil mb -p "${PROJECT_ID}" -c regional -l "${REGION}" "gs://${RESUME_BUCKET_NAME}"
    gsutil cp data/*.pdf "gs://${RESUME_BUCKET_NAME}"
  else
    log "GCS bucket for resume storage already exists. Skipping..."
  fi
}

#############################################
# Create a GCS bucket for storing processed embeddings
#############################################
create_embeddings_bucket() {
  if ! gsutil ls "gs://${EMBEDDINGS_BUCKET_NAME}" &>/dev/null; then
    log "Creating GCS bucket for resume storage..."
    gsutil mb -p "${PROJECT_ID}" -c regional -l "${REGION}" "gs://${EMBEDDINGS_BUCKET_NAME}"
  else
    log "GCS bucket for resume storage already exists. Skipping..."
  fi
}

#############################################
# Create custom Eventarc channel for chat history
#############################################
create_eventarc_chat_channel() {
  log "Creating Eventarc channel..."
  gcloud eventarc channels create "${CHAT_CHANNEL}" --location "${REGION}"
}

#############################################
# Setup needed configuration for resume updates
#############################################
setup_resume_updates() {
  local PROJECT_NUMBER
  local SERVICE_ACCOUNT
  PROJECT_NUMBER=$(get_project_number "${PROJECT_ID}")

  # Default compute service account will be used in triggers
  log "Granting the eventarc.eventReceiver role to the default compute service account..."
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member "serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role roles/eventarc.eventReceiver

  # This is needed for the Eventarc Cloud Storage trigger
  log "Granting the pubsub.publisher role to the Cloud Storage service account..."
  SERVICE_ACCOUNT=$(gsutil kms serviceaccount -p "${PROJECT_ID}")

  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member "serviceAccount:${SERVICE_ACCOUNT}" \
    --role roles/pubsub.publisher
}
