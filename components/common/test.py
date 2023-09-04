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

import unittest

from common import solution
from common.admin_dao import AdminDAO
from common.log import Logger, log

logger = Logger(__name__).get_logger()
logger.info('Initializing...')


class TestAdmin(unittest.TestCase):

    @log
    def test_get_resumes_timestamp(self) -> None:
        """Test get resume update."""
        admin: AdminDAO = AdminDAO()
        current_time = solution.now()
        result = admin.get_resumes_timestamp()
        assert result is None or current_time < result

    @log
    def test_erase_resumes_timestamp(self) -> None:
        """Test erasing the timestamp."""
        admin: AdminDAO = AdminDAO()
        assert admin.erase_resumes_timestamp() is None
        assert admin.get_resumes_timestamp() is None

    @log
    def test_touch_resumes(self) -> None:
        """Test resume update."""
        admin: AdminDAO = AdminDAO()
        current_time = solution.now()

        assert current_time == admin.touch_resumes(timestamp=current_time)
        assert current_time == admin.get_resumes_timestamp()


if __name__ == '__main__':
    unittest.main()
