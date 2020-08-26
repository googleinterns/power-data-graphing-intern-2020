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

"""A Test module for LevelSlicesReader Class."""
# pylint: disable=W0212

import pytest
from level_slices_reader import LevelSlicesReader
from gcs_test_utils import upload

TEST_FILENAME = 'slice_reader_test.csv'
TEST_FILENAME2 = 'slice_reader_test2.csv'


class TestLevelSlicesReader:
    """A Test Class for LevelSlicesReader Class."""
    @pytest.fixture
    def test_records1(self):
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
    def test_records2(self):
        return [
            [1573149236257988, 100, 'SYS'],
            [1573149236258888, 100, 'SYS'],
            [1573149236259888, 100, 'SYS'],
            [1573149236260888, 100, 'SYS'],
            [1573149236261888, 100, 'SYS'],
            [1573149236262888, 100, 'SYS'],
            [1573149236263888, 100, 'SYS'],
            [1573149236264888, 100, 'SYS'],
            [1573149236265888, 100, 'SYS'],
            [1573149236266888, 100, 'SYS'],
            [1573149236267888, 100, 'SYS'],
            [1573149236268888, 100, 'SYS'],
            [1573149236269888, 100, 'SYS'],
        ]

    def test_format_response(self, test_records1):
        """Tests if format is right on calling format_response."""
        bucket = upload(TEST_FILENAME, test_records1)
        test_slice = LevelSlicesReader([TEST_FILENAME], bucket)

        formatted = test_slice.format_response()
        expected = []
        assert formatted == expected

        test_slice.read(None, None)
        formatted = test_slice.format_response()
        expected = [{'name': test_records1[0][2], 'data':[
            [record[0], record[1]] for record in test_records1]}]
        assert formatted == expected

    def test_read_slices_dummy_time(self, test_records1, test_records2):
        """Tests multiple slice reading with dummy start and end."""
        bucket = upload(TEST_FILENAME, test_records1)
        bucket = upload(TEST_FILENAME2, test_records2)

        test_slice = LevelSlicesReader(
            filenames=[TEST_FILENAME, TEST_FILENAME2], bucket=bucket)
        test_slice.read(-1, float('inf'))
        assert test_slice._records['PPX_ASYS'] == test_records1
        assert test_slice._records['SYS'] == test_records2

    def test_read_slices_with_time(self, test_records1, test_records2):
        """Tests multiple slice reading with specified start and end."""
        bucket = upload(TEST_FILENAME, test_records1)
        bucket = upload(TEST_FILENAME2, test_records2)

        test_slice = LevelSlicesReader(
            filenames=[TEST_FILENAME, TEST_FILENAME2], bucket=bucket)

        start = test_records1[-1][0]
        end = test_records2[0][0]
        test_slice.read(start, end)
        assert test_slice._records['PPX_ASYS'] == [test_records1[-1]]
        assert test_slice._records['SYS'] == [test_records2[0]]
