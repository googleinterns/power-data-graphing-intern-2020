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

"""Test Module for utils.py"""

import pytest

from utils import convert_to_csv
from utils import get_file_name
from utils import get_slice_path
from utils import parse_csv_line


class TestUtilsClass:
    """Test class for utils.py"""
    @pytest.fixture
    def test_records(self):
        """Generates test records data."""
        test_records_data = [
            [1573149236256988, 100.0, 'PPX_ASYS'],
            [1573149236257088, 100.0, 'PPX_ASYS'],
            [1573149236257188, 300.0, 'PPX_ASYS'],
            [1573149236257288, 100.0, 'PPX_ASYS'],
            [1573149236257388, 100.0, 'PPX_ASYS'],
            [1573149236257488, 100.0, 'PPX_ASYS'],
            [1573149236257588, 100.0, 'PPX_ASYS'],
            [1573149236257688, 100.0, 'PPX_ASYS'],
            [1573149236257788, 5.1, 'PPX_ASYS'],
            [1573149236257888, 100.0, 'PPX_ASYS']
        ]
        return test_records_data

    @pytest.fixture
    def test_csv_records(self, test_records):
        """Generates test records in csv format."""
        test_csv_strings = []
        for record in test_records:
            csv_string_one_line = ','.join(
                [str(element) for element in record])
            if not test_csv_strings:
                test_csv_strings.append(csv_string_one_line)
                continue
            csv_string_single_entry = '\n'.join(
                [test_csv_strings[-1], csv_string_one_line])
            test_csv_strings.append(csv_string_single_entry)
        return test_csv_strings

    def test_convert_to_csv(self, test_records, test_csv_records):
        """Tests on convert_to_csv"""
        for length in range(len(test_records)):
            assert convert_to_csv(
                test_records[:length+1]) == test_csv_records[length]

    def test_parse_csv_line(self, test_records, test_csv_records):
        """Tests on parse_csv_line"""
        for index in range(len(test_csv_records)):
            parsed_records = [parse_csv_line(
                csv_single_line) for csv_single_line in test_csv_records[index].split('\n')]
            assert parsed_records == test_records[:index+1]

    @pytest.mark.parametrize('input_line',
                             [
                                 'this,line,has,5,columns',
                                 '2,columns',
                                 'not_a_number,254.02,rail_name',
                                 '5214567426,not_a_number,rail_name'
                             ])
    def test_parse_csv_line_error_cases(self,input_line):
        actual = parse_csv_line(input_line)

        assert actual == None


    @pytest.mark.parametrize('root_dir,level,level_slice,strategy,exp',
                             [
                                 ('tmp', 'level0', 's1.csv',
                                  'max', 'tmp/level0/s1.csv'),
                                 ('tmp', 'level1', 's1.csv',
                                  'max', 'tmp/max/level1/s1.csv'),
                             ])
    def test_get_slice_path(self, root_dir, level, level_slice, strategy, exp):
        """Tests get_slice_path on different levels."""
        result = get_slice_path(root_dir, level, level_slice, strategy)
        assert result == exp

    @pytest.mark.parametrize('filename,experiment', [
        ('tmp/1.csv', 'tmp/1'),
        ('bin/tmp/1.csv', 'bin/tmp/1'),
        ('tmp/name', 'tmp/name'),
        ('name.csv', 'name'),
    ])
    def test_get_file_name(self, filename, experiment):
        result = get_file_name(filename)
        assert result == experiment
