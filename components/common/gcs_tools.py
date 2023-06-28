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
"""Set of utility functions to work with Firestore."""

import os
import shutil

from common.log import Logger, log_params
from google.cloud import storage

logger = Logger(__name__).get_logger()


@log_params
def download(bucket_name: str, local_dir: str) -> None:
    """Download files from GCS."""
    logger.debug(f'Current dir: {os.getcwd()}')
    # Make sure the local temp directory is empty before we do anything
    if os.path.exists(local_dir):
        shutil.rmtree(local_dir)
    os.makedirs(local_dir)

    # Download all blobs from the bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs()
    for blob in blobs:
        local_file_path: str = f'{local_dir}/{blob.name}'
        local_dir_path = os.path.dirname(local_file_path)
        if not os.path.exists(local_dir_path):
            os.makedirs(local_dir_path)
        if not os.path.exists(local_file_path):
            blob.download_to_filename(local_file_path)
            logger.debug(f'Downloaded {blob.name} to {local_file_path}')


@log_params
def delete_all_objects(bucket_name: str):
    """Delete all objects from the GCS bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs()

    for blob in blobs:
        blob.delete()


@log_params
def upload(bucket_name: str, local_dir: str) -> None:
    """Upload local files to GCS."""
    delete_all_objects(bucket_name=bucket_name)
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    for root, _, files in os.walk(local_dir):
        for file in files:
            local_file_path = os.path.join(root, file)
            blob = bucket.blob(local_file_path.replace(f'{local_dir}/', ''))
            blob.upload_from_filename(local_file_path)
            logger.debug(f'File {local_file_path} uploaded to {local_file_path.replace(local_dir,"")}.')
