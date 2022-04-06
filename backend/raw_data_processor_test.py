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

import os
from tempfile import NamedTemporaryFile

import pytest
from raw_data_processor import RawDataProcessor
from utils import convert_to_csv


class TestRawDataProcessor:
    """Test class for RawDataProcessor class."""

    @pytest.fixture
    def test_records(self):
        return [[1573149236256988, 100, 'PPX_ASYS'],
                [1573149236257088, 100, 'PPX_ASYS'],
                [1573149236257188, 300, 'PPX_ASYS'],
                [1573149236257288, 100, 'PPX_ASYS'],
                [1573149236257388, 100, 'PPX_ASYS'],
                [1573149236257488, 100, 'PPX_ASYS'],
                [1573149236257588, 100, 'PPX_ASYS'],
                [1573149236257688, 100, 'PPX_ASYS'],
                [1573149236257788, 5, 'PPX_ASYS'],
                [1573149236257888, 100, 'PPX_ASYS']]

    @pytest.fixture
    def testfile(self, test_records):
        """Returns a filename with test data saved."""

        tmpfile = NamedTemporaryFile()
        assert os.path.exists(tmpfile.name)

        with open(tmpfile.name, 'w') as tmpfilewriter:
            data_csv = convert_to_csv(test_records)
            tmpfilewriter.write(data_csv)
        return tmpfile

    def test_filename(self, testfile):
        """Tests if raw file is same as passed in."""
        raw_data = RawDataProcessor(testfile.name, 10)
        assert raw_data._rawfile == testfile.name
        testfile.close()

    def test_readable(self, testfile):
        """Tests if readable at start and end."""
        raw_data = RawDataProcessor(testfile.name, 1)
        for _ in range(11):
            assert raw_data.readable()
            raw_data.read_next_slice()
        assert not raw_data.readable()
        testfile.close()

    def test_saved_records(self, testfile, test_records):
        """Tests if records saved is same as expected."""
        raw_data = RawDataProcessor(testfile.name, 10)
        records = raw_data.read_next_slice()
        assert records == test_records
        testfile.close()

    def test_read_next_slice_returns_error_message_for_empty_file(self):
        """Tests to ensure it returns an error message for empty files."""
        empty_file = NamedTemporaryFile()
        raw_data = RawDataProcessor(empty_file.name, 10)

        records = raw_data.read_next_slice()

        assert isinstance(records, str)

        empty_file.close()

    def test_read_next_slice_returns_error_message_for_bad_data(self):
        """Tests to ensure it returns an error message files with bad data."""
        bad_data = NamedTemporaryFile()
        with open(bad_data.name, 'w') as tmpfilewriter:
            tmpfilewriter.write('1,2,has,many,columns\n')
            tmpfilewriter.write('not_a_number,2,rail_name\n')
            tmpfilewriter.write('1,not_a_number,rail_name\n')
        raw_data = RawDataProcessor(bad_data.name, 10)

        records = raw_data.read_next_slice()

        assert isinstance(records, str)

        bad_data.close()
