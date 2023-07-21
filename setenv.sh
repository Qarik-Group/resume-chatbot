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

# Exit on error. Append "|| true" if you expect an error.
set -o errexit
# Exit on error inside any functions or subshells.
set -o errtrace
# Do not allow use of undefined vars. Use ${VAR:-} to use an undefined VAR
set -o nounset
# Catch the error in case mysqldump fails (but gzip succeeds) in `mysqldump |gzip`
set -o pipefail

PROJECT_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PROJECT_HOME

# shellcheck source=/dev/null
source "${PROJECT_HOME}/utils.sh"
log "Running top level 'setenv.sh'"

export PYTHONPATH="${PROJECT_HOME}/components"
export LOG_LEVEL="DEBUG"

# ------------------------- Check for the global settings
if [ ! -f "${PROJECT_HOME}/.env" ]; then
  echo "Making a copy of [${PROJECT_HOME}/.env.example] into [${PROJECT_HOME}/.env]."
  cp "${PROJECT_HOME}/.env.example" "${PROJECT_HOME}/.env"
fi
set -o allexport
# shellcheck source=/dev/null
source "${PROJECT_HOME}/.env"

# ------------------------- Check for the local settings
if [ ! -f "./setenv_dev.sh" ] && [ -f "./setenv_example.sh" ]; then
  echo "Making a copy of [./setenv_example.sh] into [./setenv_dev.sh]."
  cp "./setenv_example.sh" "./setenv_dev.sh"
fi

if [ -f "./setenv_dev.sh" ]; then
  # shellcheck source=/dev/null
  source "./setenv_dev.sh"
fi
