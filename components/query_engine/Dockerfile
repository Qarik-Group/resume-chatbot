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

ENV COMPONENT_NAME="query_engine"
ENV RUN_FILE="service"
ENV APP_USER="user1"
ENV PATH="/home/$APP_USER/.local/bin:$PATH"
ENV BASE_DIR="/app"
# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED True

# Create group:user to run the application
RUN groupadd -g 6006 $APP_USER && useradd -m -r -u 6006 -g $APP_USER $APP_USER

RUN mkdir -p $BASE_DIR/$COMPONENT_NAME
RUN chown $APP_USER $BASE_DIR
USER $APP_USER
WORKDIR $BASE_DIR/$COMPONENT_NAME

ADD ./common/requirements.txt ./common/
ADD ./requirements.txt ./
RUN pip install -r requirements.txt -r ./common/requirements.txt
# Files below change more often, hence we copy them last
ADD ./common/*.py ./common/
ADD ./*.py ./

# Run the web service on container startup.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --timeout 0 --chdir $BASE_DIR $RUN_FILE:app -k uvicorn.workers.UvicornWorker
