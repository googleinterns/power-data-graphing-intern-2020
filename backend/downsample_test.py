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
from math import ceil
from random import randint

import pytest

from downsample import _average_downsample
from downsample import _max_min_downsample
from downsample import strategy_reducer


class TestDownsampleClass:
    """Test class for downsample.py"""

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
    def records_one_channel_complex(self):
        """Generates single channel complex test data."""
        start = 1573149236256988.0
        records_one_channel_complex = [[start, 100, 'SYS']]
        for _ in range(500):
            records_one_channel_complex.append(
                [
                    records_one_channel_complex[-1][0] +
                    randint(1E4, 1E6),
                    randint(0, 500),
                    'SYS'
                ])

        last = -1
        for record in records_one_channel_complex:
            assert record[0] >= last
            last = record[0]

        return records_one_channel_complex

    @pytest.fixture
    def records_multi_channel_complex(self):
        """Generates multiple channel complex test data."""
        start = 1573149236256988.0
        channels = ['SYS', 'PPX_ASYS', 'PP1800_SOC']
        records_multi_channel_complex = [[start, 100, 'PP1800_SOC']]
        for _ in range(500):
            for channel in channels:
                records_multi_channel_complex.append(
                    [
                        records_multi_channel_complex[-1][0] +
                        randint(1E4, 1E6),
                        randint(0, 500),
                        channel
                    ])
        assert 'SYS' in [record[2]
                         for record in records_multi_channel_complex]
        assert 'PPX_ASYS' in [record[2]
                              for record in records_multi_channel_complex]
        assert 'PP1800_SOC' in [record[2]
                                for record in records_multi_channel_complex]
        assert len([[]
                    for record in records_multi_channel_complex
                    if record[2] == 'SYS']) >= 500
        assert len([[]
                    for record in records_multi_channel_complex
                    if record[2] == 'PPX_ASYS']) >= 500
        assert len([[]
                    for record in records_multi_channel_complex
                    if record[2] == 'PP1800_SOC']) >= 500
        last = -1
        for record in records_multi_channel_complex:
            assert record[0] >= last
            last = record[0]
        return records_multi_channel_complex

    @pytest.mark.parametrize("downsample_factor,expected_records_indices", [
        (1, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
        (2, [0, 2, 4, 6, 9]),
        (4, [2, 4, 9]),
        (100, [2])
    ])
    def test_max_min_downsample_max_strategy(self, records,
                                             downsample_factor,
                                             expected_records_indices):
        """Tests on _max_min_downsample method in max downsample strategy,
        with differing input records."""
        downsample_results = _max_min_downsample(
            records, True, downsample_factor)
        expected_records = [records[index]
                            for index in expected_records_indices]
        assert downsample_results == expected_records

    @pytest.mark.parametrize("downsample_factor,expected_records_indices", [
        (0, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
        (2, [0, 3, 4, 6, 8]),
        (4, [0, 4, 8]),
        (100, [8])
    ])
    def test_max_min_downsample_min_strategy(self,
                                             records,
                                             downsample_factor,
                                             expected_records_indices):
        """Tests on _max_min_downsample method in min downsample strategy,
        with differing input records."""
        downsample_results = _max_min_downsample(
            records, False, downsample_factor)
        expected_records = [records[index]
                            for index in expected_records_indices]
        assert downsample_results == expected_records

    def test_average_downsample_max_zero_factor(self, records):
        """Tests on _average_downsample method, with max_records=0."""
        downsample_factor = 0
        test_result = _average_downsample(records, downsample_factor)
        assert test_result == records

    def test_average_downsample_avg_one(self, records):
        """Tests on _average_downsample method, with max_records=1."""
        max_records = 1
        downsample_factor = ceil(len(records) / max_records)
        test_result = _average_downsample(records, downsample_factor)
        expected_average = [
            [
                sum([record[0] for record in records]) / len(records),

                sum([record[1] for record in records]) / len(records),
                'PPX_ASYS'

            ]
        ]
        assert test_result == expected_average

    def test_average_downsample_avg_two(self, records):
        """Tests on _average_downsample method, with max_records=2."""
        max_records = 2
        downsample_factor = ceil(len(records) / max_records)
        test_result = _average_downsample(records, downsample_factor)

        # Calculates average over first and second halves.
        expected_average = [
            [
                sum([record[0] for record in records[:len(records) // 2]]
                    ) / (len(records) // 2),
                sum([record[1] for record in records[:len(records) // 2]]

                    ) / (len(records) // 2),
                'PPX_ASYS'

            ],
            [
                sum([record[0] for record in records[len(records) // 2:]]
                    ) / (len(records) // 2),
                sum([record[1] for record in records[len(records) // 2:]]

                    ) / (len(records) // 2),
                'PPX_ASYS'

            ],
        ]
        assert test_result == expected_average

    def format_one_channel_downsample(self, targets, name):
        """Formats the targets of single channel with given channel name to dict format.
        Args:
            targets: A list of records.
            name: A string of the channel name.


        Returns:
            A dict for the targets.
        """

        if not targets:
            return [{'data': [], 'name': name}]

        return [{'name': name, 'data': [[record[0], record[1]]for record in targets]}]

    def format_multi_channel_downsample(self, targets):
        """Formats the targets of multiple channel with given channel name to dict format.
        Args:
            targets: A list of records.


        Returns:
            A dict for the targets.
        """
        result = dict()
        for target in targets:
            record_list = result.get(target[2], [])
            record_list.append([target[0], target[1]])
            result[target[2]] = record_list
        return result

    @pytest.mark.parametrize('downsample_factor', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    def test_strategy_reducer(self, records, downsample_factor):
        """Tests on strategy_reducer method, check if right strategy is applied"""
        assert strategy_reducer(records, 'max', downsample_factor) == _max_min_downsample(
            records, True, downsample_factor)
        assert strategy_reducer(records, 'min', downsample_factor) == _max_min_downsample(
            records, False, downsample_factor)
        assert strategy_reducer(records, 'avg', downsample_factor) == _average_downsample(
            records, downsample_factor)

        assert strategy_reducer(
            records, 'not_exist', downsample_factor) == []
