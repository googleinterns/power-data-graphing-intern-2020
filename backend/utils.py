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
PREPROCESS_DIR = 'preprocess'
METADATA = 'metadata.json'


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


def generate_filename_on_strategy(original_filename, strategy):
    """Generates filename of preprocessed result based on the strategy.

    Args:
        original_filename: A string filename of the file (e.g. tmp/DMM_single_channel.csv)
        strategy: One of STRATEGIES in string.

    Returns:
        A string representing the filename for the preprocessed results.
    """
    original_path_no_postfix = original_filename.strip(' ').strip(
        '\n').strip('.csv')
    file_name = original_path_no_postfix.split('/')[-1]
    target_parent_path = os.path.join(PREPROCESS_DIR, original_path_no_postfix)
    if not os.path.isdir(target_parent_path):
        os.makedirs(target_parent_path)
    file_path = os.path.join(
        target_parent_path, file_name + '_' + strategy + '.csv')
    return file_path


def get_file_name(path):
    """Get the file name without .csv postfix.

    Args:
        path: A string for the absolute path to the file.

    Returns:
        A string for the path without .csv postfix
    """
    parent_path = path.strip(' ').strip(
        '\n').strip('.csv')
    file_name = parent_path.split('/')[-1]
    return file_name


def warning(message, *args):
    logging.warning(message, *args)


def error(message, *args):
    logging.error(message, *args)


def info(message, *args):
    logging.info(message, *args)


def get_level_name(index):
    return 'level' + str(index)


def get_slice_name(index):
    """Gets the name of slice.

    Args:
        index: An int representing the index of the slice.

    Returns:
        A string representing the name of the slice.
    """
    filename = 's{}.csv'.format(index)
    return filename


def get_slice_path(root_dir, level, level_slice, strategy=None):
    """Gets the path of the slice from level and strategy. If strategy is None for
        level0.
    Args:
        root_dir: A string that represents the directory of preprocesse files.
        level: A string of level name.
        level_slice: A string of slice name.
        strategy: A string representing a downsampling strategy.

    Returns:
        A string indicating the file path with given slice of data.
    """
    slice_name = level_slice
    if level not in slice_name:
        slice_name = '/'.join([level, level_slice])

    if level == 'level0':
        return '/'.join([root_dir, slice_name])
    return '/'.join([root_dir, strategy, slice_name])


def mkdir(path):
    if not os.path.isdir(path):
        os.makedirs(path)
