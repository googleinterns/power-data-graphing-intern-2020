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

"""HTTP server module

    Expose HTTP endpoints for triggering preprocess and send downsampled data.
"""

from flask import request
from flask import jsonify
from flask import Flask
from flask_cors import CORS
import utils
import downsample

NUMBER_OF_RECORDS_PER_REQUEST = 800
NUMBER_OF_RECORDS_PER_SECOND = 2000
FLOAT_PRECISION = 4
STRATEGIES = ['max', 'min', 'lttb', 'avg']

FILENAME = 'DMM_result_single_channel.csv'

app = Flask(__name__)
CORS(app)


@app.route('/data')
def get_data():
    """HTTP endpoint to get data

        Retrives all power data from local file given a limit on number of
        records from request body.
    """
    strategy = request.args.get('strategy', default='avg', type=str)
    start = request.args.get('start', default=None, type=int)
    end = request.args.get('end', default=None, type=int)
    if not strategy in STRATEGIES:
        return 'Incorrect Strategy', 400

    cache_filename = utils.cache_filename(FILENAME, strategy)
    data = downsample.secondary_downsample(
        cache_filename, strategy, NUMBER_OF_RECORDS_PER_REQUEST, start, end)

    return jsonify(data)


@app.route('/preprocessing')
def preprocessing():
    """HTTP endpoint to preprocess data

        Preprocess data for all strategy and save results locally,
        each strategy in a file.
    """
    for strategy in STRATEGIES:
        data = downsample.downsample(
            FILENAME, strategy, NUMBER_OF_RECORDS_PER_SECOND)
        data_csv = utils.csv_format(data)
        output_filename = utils.cache_filename(FILENAME, strategy)
        with open(output_filename, 'w') as filewriter:
            filewriter.write(data_csv)
            filewriter.flush()
    return 'Preprocessing Successful!'


@app.before_first_request
def initialize():
    """Initialize with preprocessing

        Preprocess all power data at the first request.
    """
    # TODO(tangyifei@): Initialize at the start of service, instead of first request.
    preprocessing()


if __name__ == '__main__':
    app.run(port=5000)
