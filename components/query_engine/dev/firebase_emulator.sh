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

# FIRESTORE_EMULATOR_HOST=localhost:8070

# See additional details here: https://firebase.google.com/docs/emulator-suite/install_and_configure
firebase emulators:start --only firestore --project "${PROJECT_ID}"
