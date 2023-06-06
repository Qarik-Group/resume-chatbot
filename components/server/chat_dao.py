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
"""Data Access Object to abstract access to the database from the rest of the app."""

from datetime import timedelta
from typing import Any

import datetimes
import solution
import firestore_tools
from log import Logger, log
from google.cloud import firestore    # type: ignore

logger = Logger(__name__).get_logger()


class ChatDao:
    """Device object that handles database persistence."""

    def __init__(self) -> None:
        self._db = firestore_tools.create_firestore_client()
        self._collection = self._db.collection(f'{solution.RESOURCE_PREFIX}_users')
        """Firestore collection that keeps track of users known to the system."""

    @log
    def _get_doc_ref_by_id(self, user_id: str) -> firestore.DocumentReference | None:
        """Find device Firestore Doc Ref by its ID. Return None if does not exist."""
        doc_ref = self._collection.document(user_id)
        return doc_ref if doc_ref.get().exists else None

    # @log
    # def get_by_id(self, user_id: str) -> models_device.DeviceOutput | None:
    #     """Find device by its ID."""
    #     doc_ref = self._get_doc_ref_by_id(user_id)
    #     return models_device.DeviceOutput(**doc_ref.get().to_dict()) if doc_ref is not None else None

    # @log
    # def get_by_serial(self, serial_no: str) -> models_device.DeviceOutput | None:
    #     """Find device by its Serial Number."""
    #     query = self._collection.where('serial_number', '==', serial_no)
    #     device = query.get()
    #     return models_device.DeviceOutput(**device[0].to_dict()) if device is not None else None

    # @log
    # def get_by_filter(self, property_name: str, value, batch_size: int = None) -> list[models_device.DeviceOutput]:
    #     """Find list of device IDs by certain property value. Limit number of entries to the 'batch_size'."""
    #     documents = self._collection.where(property_name, '==', value).get()
    #     result = []
    #     counter = 0
    #     for doc in documents:
    #         if batch_size is not None and counter > batch_size:
    #             break
    #         counter += 1
    #         result.append(models_device.DeviceOutput(**doc.to_dict()))
    #     return result

    # @log
    # def exists(self, user_id: str) -> bool:
    #     """Check for existence of the device by its ID."""
    #     doc_ref = self._get_doc_ref_by_id(user_id)
    #     return bool(doc_ref)

    # @log
    # def id_from_serial(self, serial_no: str) -> str | None:
    #     """Find device ID by its Serial number."""
    #     query = self._collection.where('serial_number', '==', serial_no)
    #     device = query.get()
    #     return device[0].to_dict()['user_id'] if device else None

    # @log
    # def update_timestamp(self, user_id: str) -> Any:
    #     """Update value of the 'last_updated_timestamp' to the current time."""
    #     doc_ref = self._collection.document(user_id)
    #     return doc_ref.update({'last_updated_timestamp': datetimes.now()})

    # @log
    # def update_simulation(self, user_id: str, simulate: bool) -> Any:
    #     """Update value of the 'last_updated_timestamp' to the current time."""
    #     doc_ref = self._collection.document(user_id)
    #     return doc_ref.update({'is_simulated': simulate})

    # @log
    # def update(self, user_id: str, data: models_device.Device) -> Any:
    #     """Update device document."""
    #     doc_ref = self._collection.document(user_id)
    #     if not doc_ref.get().exists:
    #         return None
    #     device = models_device.DeviceOutput(**data.dict())
    #     device.last_updated_timestamp = datetimes.now()
    #     return doc_ref.set(device.dict(exclude_none=True), merge=True)

    # @log
    # def update_telemetry(self, user_id: str, data: models_device.Telemetry) -> str | None:
    #     """Update device document."""
    #     doc_ref = self._collection.document(user_id)
    #     if not doc_ref.get().exists:
    #         return None
    #     device: models_device.DeviceOutput = models_device.DeviceOutput(**doc_ref.get().to_dict())

    #     # Throttle device telemetry updates to no more than one per few seconds
    #     interval_seconds = 1.2
    #     next_update = device.last_updated_timestamp + timedelta(seconds=interval_seconds)
    #     if next_update > datetimes.now():
    #         # logger.debug('Last update was less than %s seconds ago - ignoring it', interval_seconds)
    #         # Ignore this update since it was less than a second ago compared to the previous one
    #         # Firestore limits the number of updates to the same document to no more than 1 per second
    #         # In the meantime all true telemetry will be saved in BQ in another service
    #         return 'Throttling update due to high volume'

    #     device.telemetry = data
    #     device.last_updated_timestamp = datetimes.now()
    #     doc_ref.set(device.dict(exclude_none=True), merge=True)
    #     return 'Telemetry updated OK.'

    # @log
    # def get_all_devices(self) -> list[models_device.DeviceOutput]:
    #     """Return list of all devices in the database."""
    #     devices: list[models_device.DeviceOutput] = []
    #     for doc in self._collection.stream():
    #         devices.append(models_device.DeviceOutput(**doc.to_dict()))
    #     logger.debug('Found %s devices in the database', len(devices))
    #     return devices
