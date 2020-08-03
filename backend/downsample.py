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

"""Downsample strategies.

Contains all of the downsample strategies. Use downsample(), and
secondary_downsample() for downsampling records stored in files.
"""
from math import ceil


FLOAT_PRECISION = 4
SECOND_TO_MICROSECOND = 1E6
STRATEGIES = ['max', 'min', 'avg']


def _max_min_downsample(records, is_max, downsample_factor):
    """Downsamples records by maximum or minimum value.

    Args:
        records: A list of records ([time, power, channel]) in 1 second.
        is_max: A boolean indicating if using max or not.
        downsample_factor: Take one record per "downsample_factor" records.

    Returns:
        A list of records with lower sampling rate.
        Example:
            [
                [time,power,channel1],
                [time,power,channel1],
                [time,power,channel1]
            ]
    """
    if downsample_factor <= 1:
        return records

    number_records = ceil(len(records) / downsample_factor)
    result = list()
    for index in range(number_records):
        records_in_timespan = records[index *
                                      downsample_factor: (index+1)*downsample_factor]
        if is_max:
            result.append(
                max(records_in_timespan, key=lambda record: record[1]))
        else:
            result.append(
                min(records_in_timespan, key=lambda record: record[1]))
    return result


def _average_downsample(records, downsample_factor):
    """Downsamples records by average value.

    Args:
        records: A list of records ([time, power, channel]) in 1 second.
        downsample_factor: Take one record per "downsample_factor" records.

    Returns:
        A list of downsampled records.
        Example:
            [
                [time,power,channel1],
                [time,power,channel1],
                [time,power,channel1]
            ]
    """
    if downsample_factor <= 1:
        return records

    number_records = ceil(len(records) / downsample_factor)
    result = list()
    for index in range(number_records):
        records_in_timespan = records[index *
                                      downsample_factor: (index+1)*downsample_factor]
        average = [0, 0, records_in_timespan[0][2]]
        for record in records_in_timespan:
            average[0] += record[0]
            average[1] += record[1]

        average[0] /= len(records_in_timespan)
        average[1] /= len(records_in_timespan)

        average[0] = int(average[0])
        average[1] = round(average[1], FLOAT_PRECISION)
        result.append(average)
    return result


def strategy_reducer(records, strategy, downsample_factor):
    """Applies relative downsample function to the records, based on strategy string.

    Args:
        records: A list of records ([time, power, channel]).
        strategy: A string representing downsampling strategy.
        downsample_factor: Take one record per "downsample_factor" records.

    Returns:
        A list of downsampled records with number under max_records.
        Example:
            [
                [time,power,channel1],
                [time,power,channel1],
                [time,power,channel1]
            ]
    """
    if strategy == 'max':
        res = _max_min_downsample(
            records, is_max=True, downsample_factor=downsample_factor)
    elif strategy == 'min':
        res = _max_min_downsample(
            records, is_max=False, downsample_factor=downsample_factor)
    elif strategy == 'avg':
        res = _average_downsample(
            records, downsample_factor=downsample_factor)
    else:
        res = list()
    return res
