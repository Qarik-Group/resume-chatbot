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
FROM python:3.11.0-slim

ENV RUN_FILE="service"
ENV APP_USER="user1"

# Create group:user to run the application
RUN groupadd -g 6006 $APP_USER && useradd -m -r -u 6006 -g $APP_USER $APP_USER
USER $APP_USER

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED True
ENV PATH="/home/$APP_USER/.local/bin:$PATH"
ENV BASE_DIR="/app"
WORKDIR $BASE_DIR

ADD --chown=$APP_USER:$APP_USER ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Files below change more often, hence we copy them last
ADD --chown=$APP_USER:$APP_USER . ./

# Run the web service on container startup.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --timeout 0 --chdir $BASE_DIR $RUN_FILE:app -k uvicorn.workers.UvicornWorker
