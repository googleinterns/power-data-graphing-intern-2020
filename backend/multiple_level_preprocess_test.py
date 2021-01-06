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
# pylint: disable=W0212

from math import ceil
from math import log
from tempfile import NamedTemporaryFile
import os
import pytest

from multiple_level_preprocess import MultipleLevelPreprocess
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
        preprocess = MultipleLevelPreprocess('dummy')
        preprocess._number_per_slice = number_per_slice
        preprocess._downsample_level_factor = downsample_factor
        preprocess._minimum_number_level = min_num_level

        levels, level_names = preprocess._get_levels_metadata(raw_number, 1024)
        expected_number_levels = int(log(raw_number, downsample_factor))
        if expected_number_levels == 0:
            expected_number_levels = 1

        assert len(levels) == expected_number_levels
        assert len(levels) == len(level_names)
        assert len(levels[0]['names']) == ceil(raw_number/number_per_slice)
