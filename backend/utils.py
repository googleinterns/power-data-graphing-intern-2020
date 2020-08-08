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

"""String and downsample utility functions."""


import logging
import os

FLOAT_PRECISION = 4


def parse_csv_line(line):
    """Parses record from csv file.

    Parse record and return in list type, containing time, value, and
    channel.

    Args:
        line: A string representing single line record in csv format.

    Returns:
        A list of power data records each of which contains timestamp, power value, and channel,
            e.g. [[12345678, 80, "SYSTEM"],[23456789, 60, "SENSOR"]]. Returns None if the
            given file is empty.
    """
    if not line:
        return None
    data_point = line.strip('\n').split(',')
    data_point[0] = float(data_point[0])
    data_point[1] = round(float(data_point[1]), FLOAT_PRECISION)
    return data_point


def convert_to_csv(records):
    """Convert records in list type to csv string.

    Args:
        records: A list of power data records each of which contains timestamp, power value,
        and channel. e.g. [[12345678, 80, "SYSTEM"],[23456789, 60, "SENSOR"]].

    Returns:
        A string that contains all CSV records, None if the given list if empty.
    """
    if not records:
        return None

    csv_lines = list()
    for record in records:
        string_record = [str(element) for element in record]
        csv_line = ','.join(string_record)
        csv_lines.append(csv_line)

    return '\n'.join(csv_lines)


def get_experiment_name(path):
    experiment_name = path.strip(' ').strip(
        '\n').strip('.csv')
    return experiment_name


def warning(message, *args):
    logging.warning(message, *args)


def error(message, *args):
    logging.error(message, *args)


def get_line_number(filename):
    """Reads the given file and returns the number of lines.

    Args:
        filename: A string for the file name.

    Returns:
        An integer for the number of lines.
    """
    number = 0
    with open(filename, 'r') as filereader:
        for _ in filereader:
            number += 1
    return number


def get_level_name(index):
    return 'level' + str(index)


def get_slice_name(level, index):
    filename = 's{}.csv'.format(index)
    return '/'.join([str(level), filename])


def get_slice_path(root_dir, level, level_slice, strategy=None):
    """Gets the path of the slice from level and strategy. If strategy is None for
        level0.
    Args:
        root_dir: A string that represents the directory of preprocesse files.
        level: A string or int of level name or number.
        level_slice: A string or int of slice name of number.
        strategy: A string of downsampling strategy.

    Returns:
        A string of the path of slice.
    """
    level_name = level
    if isinstance(level, int):
        level_name = get_level_name(level)

    level_slice_name = level_slice
    if isinstance(level_slice, int):
        level_slice_name = get_slice_name(level_name, level_slice)

    if level_name == 'level0':
        return '/'.join([root_dir, level_slice_name])
    return '/'.join([root_dir, strategy, level_slice_name])


def mkdir(path):
    if not os.path.isdir(path):
        os.makedirs(path)
