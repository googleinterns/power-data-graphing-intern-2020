# Copyright 2020 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================
"""Test Module for RawDataProcessor class."""
# pylint: disable=W0212


import pytest
from raw_data_processor import RawDataProcessor
from gcs_test_utils import upload

TEST_FILENAME = 'raw_processor_test.csv'


class TestRawDataProcessor:
    """Test class for RawDataProcessor class."""
    @pytest.fixture
    def test_records(self):
        return [
            [1573149236256988, 100, 'PPX_ASYS'],
            [1573149236257088, 100, 'PPX_ASYS'],
            [1573149236257188, 300, 'PPX_ASYS'],
            [1573149236257288, 100, 'PPX_ASYS'],
            [1573149236257388, 100, 'PPX_ASYS'],
            [1573149236257488, 100, 'PPX_ASYS'],
            [1573149236257588, 100, 'PPX_ASYS'],
            [1573149236257688, 100, 'PPX_ASYS'],
            [1573149236257788, 5, 'PPX_ASYS'],
            [1573149236257888, 100, 'PPX_ASYS']
        ]

    @pytest.fixture
    def test_bucket(self, test_records):
        """Returns a filename with test data saved."""

        bucket = upload(TEST_FILENAME, test_records)
        return bucket

    def test_saved_records(self, test_bucket, test_records):
        """Tests if records saved is same as expected."""
        raw_data = RawDataProcessor(TEST_FILENAME, 10, test_bucket)
        records = raw_data.read_next_slice()
        assert records == test_records
