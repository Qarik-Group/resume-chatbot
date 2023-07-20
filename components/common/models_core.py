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

from pydantic import BaseModel
from humps import camelize    # type:ignore


def to_camel(string):
    """Convert string to camel case."""
    return camelize(string)


class CamelModel(BaseModel):
    """Used to automatically generate camel case output used for REST APIs from Pythonic snake case."""

    class Config:
        """Utility class used for automatic snake to camel case conversion."""
        alias_generator = to_camel
        allow_population_by_field_name = True
