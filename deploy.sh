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

# shellcheck source=/dev/null
source "setenv.sh"

COMPONENT_LIST=()

# Deploy all parts of the application
for dir in "${PROJECT_HOME}"/components/*; do
  if [ -f "${dir}/dev/deploy.sh" ]; then
    COMPONENT_LIST+=("${dir}")
    log "***** Deploying component in [${dir}] *****"
    cd "${dir}/dev" && ./deploy.sh >"${dir}/dev/deploy.log" 2>&1 &
  fi
done

ALL_DEPLOYMENTS=("${COMPONENT_LIST[@]}")
log "Waiting for all deployments to finish."
# Loop until all log files in COMPONENT_LIST have marker DEPLOYMENT_COMPLETE_MARKER
while [ ${#COMPONENT_LIST[@]} -gt 0 ]; do
  sleep 3
  # echo "COMPONENT_LIST=${COMPONENT_LIST[*]}"
  for i in "${!COMPONENT_LIST[@]}"; do
    dir="${COMPONENT_LIST[${i}]}"
    echo "Waiting for deployment in [${dir}]..."
    if grep "${DEPLOYMENT_COMPLETE_MARKER}" "${dir}/dev/deploy.log"; then
      unset 'COMPONENT_LIST[i]'
      continue
    else
      tail -n 1 "${dir}/dev/deploy.log"
    fi
  done
done

log "***************************************"
log "All deployments finished."
log "***************************************"
for dir in "${ALL_DEPLOYMENTS[@]}"; do
  log "***** Deployment in [${dir}] *****"
  tail -n 5 "${dir}/dev/deploy.log"
done
