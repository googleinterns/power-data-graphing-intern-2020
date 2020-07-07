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

"""Test Module for downsample.py"""

import os
import random
import tempfile

import pytest

from downsample import average_downsample
from downsample import downsample
from downsample import lttb_downsample
from downsample import max_min_downsample
from downsample import secondary_downsample
from downsample import strategy_reducer
from downsample import triangle_area
from utils import convert_to_csv


class TestDownsampleClass:
    """Test cllass for downsample.py"""

    @pytest.fixture
    def records(self):
        """Generates test data."""
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
    def records_complex_case(self):
        """Generates complex test data."""
        start = 1573149236256988
        records_complex_case = [[start, 100, 'SYS']]
        for _ in range(500):
            records_complex_case.append(
                [
                    records_complex_case[-1][0] + random.randint(1E4, 1E6),
                    random.randint(0, 500),
                    'SYS'
                ])

        last = -1
        for record in records_complex_case:
            assert record[0] >= last
            last = record[0]

        return records_complex_case

    @pytest.mark.parametrize('max_records', [0, 5, 10, 20, 30, 40, 1000000])
    def test_limit_of_records(self, records, max_records):
        """Tests if data is within the threshold."""
        limit = min(len(records), max_records)
        assert len(max_min_downsample(
            records, True, max_records)) <= limit
        assert len(max_min_downsample(
            records, False, max_records)) <= limit
        assert len(average_downsample(
            records, max_records)) <= limit
        assert len(lttb_downsample(
            records, max_records)) <= limit

    @pytest.mark.parametrize("point1,point2,point3,area", [
        ([0, 0], [0, 1], [1, 0], 0.5),
        ([0, 0], [0, 10], [10, 0], 50),
        ([0, 0], [40, 0], [400, 20], 400),
        ([0, 0], [40, 0], [400, 0], 0),
    ])
    def test_triangle_area(self, point1, point2, point3, area):
        """Tests on triangle area."""
        assert abs(triangle_area(point1, point2, point3) - area) <= 0.01

    def test_lttb_downsample(self, records):
        """Tests on lttb_downsample method"""
        max_records = 0
        test_result = lttb_downsample(records, max_records)
        assert test_result == []

        max_records = 1
        test_result = lttb_downsample(records, max_records)
        assert test_result == [records[0]]

        max_records = 2
        test_result = lttb_downsample(records, max_records)
        assert test_result == [records[0], records[-1]]

        max_records = 3
        test_result = lttb_downsample(records, max_records)
        assert test_result == [records[0], records[2], records[-1]]

        max_records = 4
        test_result = lttb_downsample(records, max_records)
        assert test_result == [records[0], records[2], records[8], records[-1]]

        max_records = 100
        test_result = lttb_downsample(records, max_records)
        assert test_result == records

        max_records = 100
        test_result = lttb_downsample([], max_records)
        assert test_result == []

    def test_max_downsample(self, records):
        """Tests on max_min_downsample method, only work on maximun downsample"""
        max_records = 0
        test_result = max_min_downsample(records, True, max_records)
        assert test_result == []

        max_records = 1
        test_result = max_min_downsample(records, True, max_records)
        assert test_result == [records[2]]

        max_records = 2
        test_result = max_min_downsample(records, True, max_records)
        assert test_result == [records[2], records[5]]

        max_records = 100
        test_result = max_min_downsample(records, True, max_records)
        assert test_result == records

        max_records = 100
        test_result = max_min_downsample([], True, max_records)
        assert test_result == []

    def test_min_downsample(self, records):
        """Tests on max_min_downsample method, only work on minimum downsample"""
        max_records = 0
        test_result = max_min_downsample(records, False, max_records)
        assert test_result == []

        max_records = 1
        test_result = max_min_downsample(records, False, max_records)
        assert test_result == [records[8]]

        max_records = 2
        test_result = max_min_downsample(records, False, max_records)
        assert test_result == [records[0], records[8]]

        max_records = 100
        test_result = max_min_downsample(records, False, max_records)
        assert test_result == records

        max_records = 100
        test_result = max_min_downsample([], False, max_records)
        assert test_result == []

    def test_average_downsample(self, records):
        """Tests on average_downsample method"""
        max_records = 0
        test_result = average_downsample(records, max_records)
        assert test_result == []

        max_records = 1
        test_result = average_downsample(records, max_records)
        expected_average = [
            [
                sum([record[0] for record in records]) / len(records),
                sum([record[1] for record in records]) / len(records),
                records[0][2]
            ]
        ]
        assert test_result == expected_average

        max_records = 2
        test_result = average_downsample(records, max_records)

        # Calculates average over first and second halves.
        expected_average = [
            [
                sum([record[0] for record in records[:len(records) // 2]]
                    ) / (len(records) // 2),
                sum([record[1] for record in records[:len(records) // 2]]
                    ) / (len(records) // 2),
                records[0][2]
            ],
            [
                sum([record[0] for record in records[len(records) // 2:]]
                    ) / (len(records) // 2),
                sum([record[1] for record in records[len(records) // 2:]]
                    ) / (len(records) // 2),
                records[0][2]
            ],
        ]
        assert test_result == expected_average

        max_records = 100
        test_result = average_downsample(records, max_records)
        expected_average = records
        assert test_result == expected_average

        max_records = 100
        test_result = average_downsample([], max_records)
        assert test_result == []

    def assert_records_in_each_second(self, filename, max_records_per_second):
        """Asserts that records are sampled on a per-second basis.

        Args:
            filename: A string representing name of the records file.
            max_records_per_second: An interger representing number of records to save per second.
        """
        result = downsample(filename, 'min', max_records_per_second)
        for index in range(len(result) - max_records_per_second * 2):
            assert result[index + 2 * max_records_per_second][0] - \
                result[index][0] >= 1E6

    def test_downsample(self, records_complex_case):
        """Tests on downsample method"""
        tmpfile = tempfile.NamedTemporaryFile()
        assert os.path.exists(tmpfile.name)
        with open(tmpfile.name, 'w') as tmpfilewriter:
            data_csv = convert_to_csv(records_complex_case)
            tmpfilewriter.write(data_csv)

        self.assert_records_in_each_second(tmpfile.name, 1)
        self.assert_records_in_each_second(tmpfile.name, 10)
        self.assert_records_in_each_second(tmpfile.name, 50)

        tmpfile.close()
        assert not os.path.exists(tmpfile.name)

    def test_strategy_reducer(self, records):
        """Tests on strategy_reducer method"""

        # Test if right strategy is applied.
        for max_records in range(15):
            assert strategy_reducer(records, 'max', max_records) == max_min_downsample(
                records, True, max_records)
            assert strategy_reducer(records, 'min', max_records) == max_min_downsample(
                records, False, max_records)
            assert strategy_reducer(records, 'avg', max_records) == average_downsample(
                records, max_records)
            assert strategy_reducer(records, 'lttb', max_records) == lttb_downsample(
                records, max_records)
            assert strategy_reducer(
                records, 'not_exist', max_records) == []

    def test_secondary_downsample(self, records_complex_case):
        """Tests on secondary_downsample method"""
        tmpfile = tempfile.NamedTemporaryFile()
        assert os.path.exists(tmpfile.name)
        with open(tmpfile.name, 'w') as tmpfilewriter:
            data_csv = convert_to_csv(records_complex_case)
            tmpfilewriter.write(data_csv)

        # Test without timespan.
        for max_records in range(0, 200, 40):
            assert secondary_downsample(tmpfile.name, 'max', max_records, None, None) \
                == max_min_downsample(records_complex_case, True, max_records)
            assert secondary_downsample(tmpfile.name, 'min', max_records, None, None) \
                == max_min_downsample(records_complex_case, False, max_records)
            assert secondary_downsample(tmpfile.name, 'avg', max_records, None, None) \
                == average_downsample(records_complex_case, max_records)
            assert secondary_downsample(tmpfile.name, 'lttb', max_records, None, None) \
                == lttb_downsample(records_complex_case, max_records)
            assert secondary_downsample(
                tmpfile.name, 'not_exist', max_records, None, None) == []

        # Test with timespan given.
        for max_records in range(0, 200, 40):
            middle_half = (125, 275)
            middle_half_records = records_complex_case[middle_half[0]:
                                                       middle_half[1]]
            start, end = (
                records_complex_case[middle_half[0]][0],
                records_complex_case[middle_half[1] - 1][0]
            )

            assert secondary_downsample(tmpfile.name, 'max', max_records, start, end) \
                == max_min_downsample(middle_half_records, True, max_records)
            assert secondary_downsample(tmpfile.name, 'min', max_records, start, end) \
                == max_min_downsample(middle_half_records, False, max_records)
            assert secondary_downsample(tmpfile.name, 'avg', max_records, start, end) \
                == average_downsample(middle_half_records, max_records)
            assert secondary_downsample(tmpfile.name, 'lttb', max_records, start, end) \
                == lttb_downsample(middle_half_records, max_records)
            assert secondary_downsample(
                tmpfile.name, 'not_exist', max_records, start, end) == []

        tmpfile.close()
        assert not os.path.exists(tmpfile.name)
