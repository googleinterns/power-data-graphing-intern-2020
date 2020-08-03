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

"""Test Module for multiple_level_preprocess.py"""

from collections import defaultdict
from math import ceil
from math import log
from tempfile import NamedTemporaryFile
import os
import pytest

from multiple_level_preprocess import binary_search
from multiple_level_preprocess import _get_basic_meta_info
from multiple_level_preprocess import _get_levels_metadata
from utils import convert_to_csv


class TestMlpClass:
    """Test Class for multiple_level_preprocess.py"""

    def write_to_tmpfile(self, records_to_be_written):
        """Writes records in a temperary file.

        Args:
            records_to_be_written: A list of records.

        Returns:
            A fileIO object for that temp file.
        """
        tmpfile = NamedTemporaryFile()
        assert os.path.exists(tmpfile.name)
        with open(tmpfile.name, 'w') as tmpfilewriter:
            data_csv = convert_to_csv(records_to_be_written)
            tmpfilewriter.write(data_csv)
        return tmpfile

    @pytest.mark.parametrize('numbers,value,expected', [
        ([0, 2, 4, 6, 8, 10, 12], -1, 0),
        ([0, 2, 4, 6, 8, 10, 12], 0, 0),
        ([0, 2, 4, 6, 8, 10, 12], 1, 0),
        ([0, 2, 4, 6, 8, 10, 12], 2, 0),
        ([0, 2, 4, 6, 8, 10, 12], 3, 1),
        ([0, 2, 4, 6, 8, 10, 12], 4, 1),
        ([0, 2, 4, 6, 8, 10, 12], 5, 2),
        ([0, 2, 4, 6, 8, 10, 12], 6, 2),
        ([0, 2, 4, 6, 8, 10, 12], 12, 5),
        ([0, 2, 4, 6, 8, 10, 12], 13, 6),
        ([0, 2, 4, 6, 8, 10, 12], 100, 6),
    ])
    def test_binary_search_increasing(self, numbers, value, expected):
        """Tests binary search with list of numbers in increasing order."""
        assert binary_search(numbers, value, False) == expected

    @pytest.mark.parametrize('numbers,value,expected', [
        ([10, 8, 6, 4, 2, 0], 100, 0),
        ([10, 8, 6, 4, 2, 0], 10, 0),
        ([10, 8, 6, 4, 2, 0], 9, 0),
        ([10, 8, 6, 4, 2, 0], 8, 1),
        ([10, 8, 6, 4, 2, 0], 7, 1),
        ([10, 8, 6, 4, 2, 0], 4, 3),
        ([10, 8, 6, 4, 2, 0], 3, 3),
        ([10, 8, 6, 4, 2, 0], 1, 4),
        ([10, 8, 6, 4, 2, 0], 0, 5),
        ([10, 8, 6, 4, 2, 0], -1, 5),
    ])
    def test_binary_search_decreasing(self, numbers, value, expected):
        """Tests binary search with list of numbers in decreasing order."""
        assert binary_search(numbers, value, True) == expected

    @pytest.mark.parametrize('raw_number,number_per_slice,downsample_factor,min_num_level',
                             [
                                 (100, 2, 10, 10),
                                 (1000, 5, 6, 7),
                                 (89, 200000, 100, 600),
                                 (10000000, 100000, 100, 500),
                                 (10000000, 200000, 100, 600),
                             ])
    def test_get_levels_metadata_num_levels_slices(self,
                                                   raw_number,
                                                   number_per_slice,
                                                   downsample_factor,
                                                   min_num_level):
        """Tests _get_levels_metadata on number of levels and slices."""
        levels, level_names = _get_levels_metadata(
            raw_number,
            1024,
            number_per_slice,
            downsample_factor,
            min_num_level
        )
        expected_number_levels = int(log(raw_number, downsample_factor))
        if expected_number_levels == 0:
            expected_number_levels = 1

        assert len(levels) == expected_number_levels
        assert len(levels) == len(level_names)
        assert len(levels[0]['names']) == ceil(raw_number/number_per_slice)
