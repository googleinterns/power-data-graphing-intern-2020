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
"""Test Module for RawData class."""
# pylint: disable=W0212

import os
from tempfile import NamedTemporaryFile

import pytest
from raw_data import RawData
from utils import convert_to_csv


class TestRawData:
    """Test class for RawData class."""
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
        raw_data = RawData(testfile.name, 10)
        assert raw_data._rawfile == testfile.name
        testfile.close()

    def test_readable(self, testfile):
        """Tests if readable at start and end."""
        raw_data = RawData(testfile.name, 1)
        for _ in range(11):
            assert raw_data.readable()
            raw_data.read()
        assert not raw_data.readable()
        testfile.close()

    def test_saved_records(self, testfile, test_records):
        """Tests if records saved is same as expected."""
        raw_data = RawData(testfile.name, 10)
        records = raw_data.read()
        assert records == test_records
        testfile.close()

    def test_close(self, testfile):
        """Tests if the file io object is closed after close is called."""
        raw_data = RawData(testfile.name, 10)
        assert not raw_data._file.closed
        raw_data.close()
        assert raw_data._file.closed
        testfile.close()
