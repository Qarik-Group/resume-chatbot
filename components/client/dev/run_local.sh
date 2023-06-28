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
cd ..

echo "Running as local process..."
npm start

# echo "Running in local docker (make sure you run the ./build_local.sh first)..."
# docker run --env-file .env --env-file ../../.env -p "${HOST_PORT}:${PORT}" --rm "${IMAGE_NAME}"
