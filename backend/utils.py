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
        original_filename: A string filename of the experiment (e.g. tmp/DMM_single_channel.csv)
        strategy: One of STRATEGIES in string.

    Returns:
        A string representing the filename for the preprocessed results.
    """
    original_path_no_postfix = original_filename.strip(' ').strip(
        '\n').strip('.csv')
    experiment_name = original_path_no_postfix.split('/')[-1]
    target_parent_path = os.path.join(PREPROCESS_DIR, original_path_no_postfix)
    if not os.path.isdir(target_parent_path):
        os.makedirs(target_parent_path)
    file_path = os.path.join(
        target_parent_path, experiment_name + '_' + strategy + '.csv')
    return file_path


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
    return '/'.join([level, filename])


def mkdir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


# def write_records_to_file(records, filename):
#     with open(filename, 'w') as filewriter:
#         if type(records) is defaultdict:
