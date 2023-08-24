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

TMP="./tmp/source"
prepare_sources "${TMP}"
cd "${TMP}" || exit

log "Building docker image for running locally on MacOs..."
podman build -t "${IMAGE_NAME}:dev" . --log-level=debug

# Purge all images from local docker registry
# podman image prune -a -f

# Delete all images from local docker registry
# podman rmi $(podman images -a -q) -f
