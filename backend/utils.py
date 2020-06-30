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

"""String utilities

    A few functions for parsing csv records, get cache file names.
"""


import sys
FLOAT_PRECISION = 4


def parse_line(line):
    """Parse record from csv file

        Parse record and return in list type, containing time, value, and
        source.

        Args:
            line: single line record in csv format

        Returns:
            list: single record with time and value in float type,
                source in string type.
    """
    if not line:
        return None
    data_point = line.strip('\n').split(',')
    data_point[0] = int(data_point[0])
    data_point[1] = round(float(data_point[1]), FLOAT_PRECISION)
    return data_point


def csv_format(records):
    """format record in list type to csv string format

        Transform records in list type to csv string format, separate columns
        with commas.

        Args:
            records: power data records in list format

        Returns:
            string: records in csv string format
    """
    if not records:
        return None

    csv_lines = list()
    for record in records:
        string_record = [str(element) for element in record]
        csv_line = ','.join(string_record)
        csv_lines.append(csv_line)

    return '\n'.join(csv_lines)


def cache_filename(filename, strategy):
    """Get filename of preprocessed result

        Get the filename of the preprocessed records in given
        strategy.

        Args:
            filename: filename of the experiment (e.g. DMM_single_channel.csv)
            strategy: one of STRATEGIES

        Returns:
            string: filename of preprocessed records
    """
    experiment = filename.strip(' ').strip('\n').strip('.csv')
    return experiment + '_' + strategy + '.csv'


def printd(string):
    # DEBUG
    print(string, flush=True)
    sys.stdout.flush()
