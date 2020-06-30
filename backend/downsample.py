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
import utils


SECOND_TO_MICROSECOND = 1E6
FLOAT_PRECISION = 4


def triangle_area(point1, point2, point3):
    """Calculate the area of triangle

        Calculate the area of triangle formed by the given three points.

        Args:
            point1: Index of the first point
            point2: Index of the second point
            point3: Index of the third point

        Returns:
            float: Area in float
    """
    return abs(point1[0] * point2[1] -
               point1[1] * point2[0] + point2[0] * point3[1] -
               point2[1] * point3[0] + point3[0] * point1[1] -
               point3[1] * point1[0]) / 2


def lttb_downsample(records, max_records):
    """Largest-triangle-three-buckets Downsampling strategy

        Downsample records and select those of highest significance.
        The time series to be downsampled is split into buckets of the same number
        as max_records, then select one record for each bucket.
        Significance is defined by the area form by the point in the current bucket and
        records in the left and right bucket.
        The process goes from left to right, so the left record is chosen already and
        right record is the average in the right bucket.
        If a bucket has only one record, choose that record.

    Args:
        records: records in 1 second
        max_records: limit of returned records

    Returns:
        list: downsampled records
    """
    if len(records) <= max_records:
        return records
    timespan = (records[-2][0] - records[1][0]) / (max_records - 2)
    buckets = list()

    start = -float('inf')
    for i, record in enumerate(records):
        if i == 0 or i == len(records) - 1:
            buckets.append([record])
            continue
        if record[0] - start > timespan:
            buckets.append([record])
            start = record[0]
        else:
            buckets[-1].append(record)

    result = list()
    for i, bucket in enumerate(buckets):
        if len(bucket) == 1:
            result.append(bucket[0])
            continue
        if len(bucket) == 0:
            continue

        # Calculate average in the next bucket
        next_average = [0, 0]
        next_index = i + 1
        while not buckets[next_index]:
            next_index += 1
        if next_index >= len(buckets) - 1:
            continue
        for record in buckets[next_index]:
            next_average[0] += record[0]
            next_average[1] += record[1]
        next_average[0] /= len(buckets[next_index])
        next_average[1] /= len(buckets[next_index])

        result.append(
            max(bucket, key=lambda record: triangle_area(result[-1], record, next_average)))
    return result


def max_min_downsample(records, method, max_records):
    """Maximum and Minimum Downsampling strategy

        Downsample the records with max or min strategy specified by parameter.

        Args:
            records: Records in 1 second
            method: one of {max, min} to specify the strategy you want to use.
            max_records: limit of returned records

        Returns:
            list: downsampled records from the given records with number of
            NUMBER_OF_RECORDS_PER_SECOND.
    """
    if len(records) <= max_records:
        return records

    timespan = len(records) // max_records
    result = list()
    for index in range(max_records):
        records_in_timespan = records[index * timespan: (index+1)*timespan]
        if method == 'max':
            result.append(
                max(records_in_timespan, key=lambda record: record[1]))
        elif method == 'min':
            result.append(
                min(records_in_timespan, key=lambda record: record[1]))
    return result


def average_downsample(records, max_records):
    """Average Downsampling strategy

    Downsample the records with average strategy.

    Args:
        records: records in 1 second
        max_records: limit of returned records

    Returns:
        list: downsampled records
    """
    if len(records) <= max_records:
        return records

    timespan = len(records) // max_records
    result = list()
    for index in range(max_records):
        records_in_timespan = records[index * timespan: (index+1)*timespan]
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


def downsample(filename, strategy, max_records_per_second):
    """Read the file and downsample with the given strategy.

        Assume the records file is on local disk, read the records and
        downsample the records in one-second-at-a-time fashion.

        Args:
            filename: The name of the records file
            strategy: Downsampling strategy.
            max_records_per_second: Number of records to save per second

        Returns:
            list: Downsampled data in the given file.
    """
    data = list()

    with open(filename, 'r') as filereader:
        temp_store = list()
        start_time = 0
        for i, line in enumerate(filereader):
            temp_store.append(utils.parse_line(line))
            if temp_store[-1] is None or temp_store[-1][0] - \
                    start_time > SECOND_TO_MICROSECOND:
                start_time = temp_store[-1][0]
                if strategy == 'max':
                    res = max_min_downsample(
                        temp_store, method='max', max_records=max_records_per_second)
                elif strategy == 'min':
                    res = max_min_downsample(
                        temp_store, method='min', max_records=max_records_per_second)
                elif strategy == 'avg':
                    res = average_downsample(
                        temp_store, max_records=max_records_per_second)
                elif strategy == 'lttb':
                    res = max_min_downsample(
                        temp_store, method='min', max_records=max_records_per_second)
                else:
                    res = list()

                data.extend(res)
                temp_store = list()
    return data


def secondary_downsample(filename, strategy, max_records, start, end):
    """Read the file and downsample with the given strategy.

        Assume the records file is on local disk, read the records and downsample the records
        to be within max records.
        Optional arguments start and end to specify a timespan in which records must be laid.

        Args:
            filename: The name of the records file
            strategy: Downsampling strategy.
            max_records: Number of records to save
            start: start of timespan
            end: end of timespan

        Returns:
            list: Downsampled data in the given file.
    """

    with open(filename, 'r') as filereader:
        data = list()
        for line in filereader.readlines():
            record = utils.parse_line(line)
            if start is None or end is None or start <= record[0] <= end:
                data.append(record)
        if strategy == 'max':
            res = max_min_downsample(
                data, method='max', max_records=max_records)
        elif strategy == 'min':
            res = max_min_downsample(
                data, method='min', max_records=max_records)
        elif strategy == 'avg':
            res = average_downsample(
                data, max_records=max_records)
        elif strategy == 'lttb':
            res = lttb_downsample(
                data,  max_records=max_records)
        else:
            res = list()
        return res
