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

"""A Test module for LevelSlice Class."""
# pylint: disable=W0212
import os
from math import ceil
from tempfile import NamedTemporaryFile
import pytest
from downsample import strategy_reducer
from level_slice import LevelSlice
from utils import convert_to_csv


class TestLevelClass:
    """Test Class for Testing LevelSlice"""
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

    def write_to_tmpfile(self, records):
        """Writes records to tmp file.

        Args:
            records: A list of records.

        Returns:
            An IO object.
        """
        tmpfile = NamedTemporaryFile()
        with open(tmpfile.name, 'w') as filewriter:
            data_csv = convert_to_csv(records)
            filewriter.write(data_csv)
        assert os.path.exists(tmpfile.name)
        return tmpfile

    def test_read(self, test_records1):
        """Tests if read records same as saved ones."""
        tmpfile = self.write_to_tmpfile(test_records1)
        test_slice = LevelSlice(tmpfile.name)
        test_slice.read()
        assert test_slice._records['PPX_ASYS'] == test_records1

        tmpfile.close()

    def test_empty_read(self):
        """Tests read behavior when none filename is supplied."""
        tmpfile = self.write_to_tmpfile([])
        test_slice = LevelSlice(tmpfile.name)
        assert test_slice._records == {}

        test_slice.read()
        assert test_slice._records == {}

    def test_add_records_single_channel(self, test_records1):
        """Tests if right records added on calling add_records, add single channel."""
        formatted_test_records = {test_records1[0][2]: test_records1}

        test_slice = LevelSlice('dummy')
        assert test_slice._records == {}

        expected_test_records = formatted_test_records
        test_slice.add_records(formatted_test_records)
        assert test_slice._records == expected_test_records

        expected_test_records = {
            test_records1[0][2]: test_records1+test_records1}
        test_slice.add_records(formatted_test_records)
        assert test_slice._records == expected_test_records

    def test_add_records_multi_channel(self, test_records1, test_records2):
        """Tests if right records added on calling add_records, add multiple channels."""
        formatted_test_records = {
            test_records1[0][2]: test_records1, test_records2[0][2]: test_records2, }

        test_slice = LevelSlice('dummy')
        assert test_slice._records == {}

        expected_test_records = formatted_test_records
        test_slice.add_records(formatted_test_records)
        assert test_slice._records == expected_test_records

    def test_get_start(self, test_records1):
        """Tests start time is earliest in all records."""
        tmpfile = self.write_to_tmpfile(test_records1)
        test_slice = LevelSlice(tmpfile.name)
        assert test_slice._start == -1

        test_slice.read()
        assert test_slice.get_first_timestamp() == test_records1[0][0]

        tmpfile.close()

    def test_save_member(self, test_records1):
        """Tests if object member records saved."""
        tmpfile = NamedTemporaryFile()
        test_save_slice = LevelSlice(tmpfile.name)

        formatted_test_records = {test_records1[0][2]: test_records1}
        test_save_slice.add_records(formatted_test_records)
        test_save_slice.save()

        test_read_slice = LevelSlice(tmpfile.name)
        test_read_slice.read()
        assert test_read_slice._records == formatted_test_records

        tmpfile.close()

    def test_save_parameter(self, test_records1):
        """Tests if parameter records saved."""
        tmpfile = NamedTemporaryFile()
        test_save_slice = LevelSlice(tmpfile.name)

        formatted_test_records = {test_records1[0][2]: test_records1}
        test_save_slice.save(test_records1)

        test_read_slice = LevelSlice(tmpfile.name)
        test_read_slice.read()
        assert test_read_slice._records == formatted_test_records

        tmpfile.close()

    @pytest.mark.parametrize('strategy', ['max', 'min', 'avg'])
    @pytest.mark.parametrize('factor', [1, 2, 4, 6, 8, 10, 100])
    def test_downsample_factor(self, test_records1, strategy, factor):
        """Tests if right downsample strategy is applied, using downsample factor."""
        tmpfile = self.write_to_tmpfile(test_records1)
        test_slice = LevelSlice(tmpfile.name)

        test_slice.read()
        downsampled = test_slice.downsample(strategy, factor)

        assert downsampled['PPX_ASYS'] == strategy_reducer(
            test_records1, strategy, factor)

        tmpfile.close()

    @pytest.mark.parametrize('strategy', ['max', 'min', 'avg'])
    @pytest.mark.parametrize('max_records', [1, 2, 3, 4, 6, 8, 10, 100])
    def test_downsample_max_records(self, test_records1, strategy, max_records):
        """Tests if right downsample strategy is applied, using max records."""
        tmpfile = self.write_to_tmpfile(test_records1)
        test_slice = LevelSlice(tmpfile.name)

        test_slice.read()
        downsampled = test_slice.downsample(strategy, max_records=max_records)
        downsample_factor = ceil(len(test_records1)/max_records)

        assert downsampled['PPX_ASYS'] == strategy_reducer(
            test_records1, strategy, downsample_factor)

        tmpfile.close()
